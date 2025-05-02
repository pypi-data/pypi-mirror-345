"""Logic for adding/vendoring the relevant libraries."""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from deprive import Import, collect_package, modify_package

from paven.utils import remove_all as _remove_all
from paven.utils import remove_matching_regex as _remove_matching_regex

if TYPE_CHECKING:
    from paven.configuration import Paven

logger = logging.getLogger(__name__)


def download_libraries(requirements: Path, destination: Path) -> None:
    """Download the relevant libraries using pip."""
    from pip._internal.cli.main import main as _main

    _main(
        [
            "install",
            "--platform",
            "any",
            "-t",
            str(destination),
            "-r",
            str(requirements),
            "--no-compile",
            # We use --no-deps because we want to ensure that dependencies are provided.
            # This includes all dependencies recursively up the chain.
            "--no-deps",
        ]
    )


def _looks_like_glob(pattern: str) -> bool:
    return "*" in pattern or "?" in pattern or "[" in pattern


def remove_unnecessary_items(destination: Path, drop_paths: list[str]) -> None:
    """Cleanup any metadata directories created."""
    for pattern in drop_paths:
        if pattern.startswith("^"):
            _remove_matching_regex(destination, pattern)
        elif _looks_like_glob(pattern):
            _remove_all(destination.glob(pattern), protected=[])
        else:
            location = pattern
            _remove_all([destination / location], protected=[])


def rewrite_file_imports(
    item: Path,
    namespace: str,
    vendored_libs: list[str],
    additional_substitutions: list[dict[str, str]],
) -> None:
    """Rewrite 'import xxx' and 'from xxx import' for vendored_libs."""
    text = item.read_text()

    # Configurable rewriting of lines.
    for di in additional_substitutions:
        pattern, substitution = di["match"], di["replace"]
        text = re.sub(pattern, substitution, text)

    # If an empty namespace is provided, we don't rewrite imports.
    if namespace != "":
        for lib in vendored_libs:
            # Normal case "import a"
            text = re.sub(
                rf"^(\s*)import {lib}(\s|$)",
                rf"\1from {namespace} import {lib}\2",
                text,
                flags=re.MULTILINE,
            )
            # Special case "import a.b as b"
            text = re.sub(
                rf"^(\s*)import {lib}(\.\S+)(?=\s+as)",
                rf"\1import {namespace}.{lib}\2",
                text,
                flags=re.MULTILINE,
            )

            # Error on "import a.b": this cannot be rewritten
            # (except for the special case handled above)
            match = re.search(rf"^\s*(import {lib}\.\S+)", text, flags=re.MULTILINE)
            if match:
                line_number = text.count("\n", 0, match.start()) + 1
                raise ValueError(
                    "Encountered import that cannot be transformed for a namespace.\n"
                    f'File "{item}", line {line_number}\n'
                    f"  {match.group(1)}\n"
                    "\n"
                    "You will need to add a patch, that adapts the code to avoid a "
                    "`import dotted.name` style import here; since those cannot be "
                    "transformed for importing via a namespace."
                )

            # Normal case "from a import b"
            text = re.sub(
                rf"^(\s*)from {lib}(\.|\s)",
                rf"\1from {namespace}.{lib}\2",
                text,
                flags=re.MULTILINE,
            )

    item.write_text(text)


def reverse_rewrite(item: Path, namespace: str) -> None:
    """Reverse the import rewriting done by `rewrite_imports`."""
    if namespace == "":  # don't rewrite imports for the empty namespace case
        return
    text = item.read_text()
    if "\t" in text:
        raise NotImplementedError("Tabs are not supported in the codebase.")

    text = text.replace(f"from {namespace}.", "from ")
    text = text.replace(f"from {namespace} ", "")
    text = text.replace(f"import {namespace}.", "import ")

    item.write_text(text)


def rewrite_imports(
    destination: Path,
    namespace: str,
    vendored_libs: list[str],
    additional_substitutions: list[dict[str, str]],
    reverse: bool = False,
) -> None:
    """Rewrite 'import xxx' and 'from xxx import' for vendored_libs."""
    if reverse and additional_substitutions:
        logger.warning("Cannot reverse additional substitutions when reversing rewrites. Ignoring.")
        additional_substitutions = []

    for item in destination.iterdir():
        if item.is_dir():
            rewrite_imports(item, namespace, vendored_libs, additional_substitutions, reverse)
        elif item.name.endswith(".py"):
            if reverse:
                reverse_rewrite(item, namespace)
            else:
                rewrite_file_imports(item, namespace, vendored_libs, additional_substitutions)


def detect_vendored_libs(destination: Path, files_to_skip: list[str]) -> list[str]:
    """Detect what libraries got downloaded."""
    retval = []
    for item in destination.iterdir():
        if item.is_dir():
            retval.append(item.name)
        elif item.name.endswith(".pyi"):  # generated stubs
            continue
        elif item.name not in files_to_skip:
            if not item.name.endswith(".py"):
                logger.warning("Got unexpected non-Python file: %s", item)
                continue
            retval.append(item.name[:-3])
    return retval


def _apply_patch(patch_file_path: Path, working_directory: Path) -> None:
    """Apply a patch to the working directory."""
    import subprocess

    subprocess.check_call(  # noqa: S603
        ["git", "apply", "--verbose", str(patch_file_path)],  # noqa: S607
        cwd=working_directory,
    )


def apply_patches(patch_dir: Path, working_directory: Path) -> None:
    """Apply all patches in the given directory to the working directory."""
    for patch in patch_dir.glob("*.patch"):
        _apply_patch(patch, working_directory)


def truncate_libs(config: Paven, vendored_libs: list[str]) -> None:
    """Truncate the list of vendored libraries to only include those that are actually used."""
    # TODO(tihoph): sub top-level imports can still be requirements for vendoring
    # TODO(tihoph): Adjust pyproject.toml::dependencies according to sync state
    graph = collect_package(config.root)
    non_vendored = {
        k: v
        for k, v in graph.items()
        if not k.module.startswith(f"{config.namespace}.") or k.module == config.namespace
    }
    requirements: dict[str, set[str]] = {}
    for lib in vendored_libs:
        extended = f"{config.namespace}.{lib}"
        for v in non_vendored.values():
            for elem in v:
                # must be external to be from the vendored package
                if not isinstance(elem, Import):
                    continue
                name = elem.name if isinstance(elem.name, str) else elem.name[0]
                fqn = elem.name if isinstance(elem.name, str) else f"{elem.name[0]}.{elem.name[1]}"
                if name.startswith((f"{lib}.", f"{extended}.")) or name in (lib, extended):
                    requirements.setdefault(lib, set()).add(fqn)

    for lib in vendored_libs:
        lib_path = config.destination / lib
        if lib not in requirements:
            logger.warning("No requirements found for vendored library, removing: %s", lib)
            _remove_all([lib_path], protected=[])
            continue
        required = {x.removeprefix(f"{config.namespace}.") for x in requirements[lib]}

        with TemporaryDirectory() as tmpdir_str:
            tmpdir = Path(tmpdir_str)
            modify_package(lib_path, required, tmpdir)
            shutil.rmtree(lib_path)
            tmpdir.rename(lib_path)

    # TODO(tihoph): Handle non-python files (e.g. data files) and directories.


def vendor_libraries(config: Paven) -> list[str]:
    """Vendor the libraries specified in the configuration."""
    destination = config.destination

    # Download the relevant libraries.
    download_libraries(config.requirements, destination)

    # Cleanup unnecessary directories/files created.
    remove_unnecessary_items(destination, config.transformations.drop)

    # Detect what got downloaded.
    vendored_libs = detect_vendored_libs(destination, config.protected_files)

    # Apply user provided patches.
    if config.patches_dir:
        apply_patches(config.patches_dir, working_directory=config.base_directory)

    # Truncate libraries to only include necessary files.
    truncate_libs(config, vendored_libs)

    # Rewrite the imports we want changed.
    rewrite_imports(config.root, config.namespace, vendored_libs, config.transformations.substitute)

    return vendored_libs
