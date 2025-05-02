"""Loads configuration from pyproject.toml."""

# mypy: allow-any-generics, allow-any-explicit
from __future__ import annotations

from pathlib import Path
from typing import Any

import msgspec


class Transformations(msgspec.Struct):
    """Transformations to apply to the vendored files."""

    substitute: list[dict[str, str]] = []
    """Additional substitutions, done in addition to import rewriting."""

    drop: list[str] = []
    """Drop."""


class License(msgspec.Struct):
    """License information for the vendored libraries."""

    fallback_urls: dict[str, str] = {}
    """Fallbacks for licenses that can't be found."""

    directories: dict[str, str] = {}
    """Alternate directory name, when distribution name differs from the package name."""


class Paven(msgspec.Struct, forbid_unknown_fields=True):
    """Configuration for the paven tool."""

    root: Path
    """Root of the codebase."""

    destination: Path
    """Location to unpack into."""

    namespace: str
    """Final namespace to rewrite imports to originate from."""

    requirements: Path
    """Path to a pip-style requirement files."""

    patches_dir: Path | None = None
    """Location to ``.patch` files to apply after vendoring."""

    protected_files: list[str] = []
    """Filenames to ignore in target directory."""

    transformations: Transformations = msgspec.field(default_factory=Transformations)
    """Transformations to apply to the vendored files."""

    license: License = msgspec.field(default_factory=License)
    """License information."""

    typing_stubs: dict[str, list[str]] = {}
    """Overrides for which stub files are generated."""

    base_directory: Path = Path()
    """Base directory for all of the operation of this project."""

    _root_name: str | None = None
    """Name of the root package."""

    def __post_init__(self) -> None:
        """Post-initialization hook."""
        try:
            self.destination.relative_to(self.root)
        except ValueError as e:
            raise ValueError(
                f"destination {self.destination} must be a subdirectory of root {self.root}"
            ) from e
        self._root_name = self.root.name
        if not self.namespace.startswith(f"{self._root_name}."):
            raise ValueError(
                f"namespace {self.namespace} must start with the root name {self._root_name}."
            )

    @property
    def root_name(self) -> str:
        """The name of the root package."""
        if self._root_name is None:
            raise ValueError("Root name not set.")
        return self._root_name


class Tool(msgspec.Struct):
    """Container for the tool section of the pyproject.toml file."""

    paven: Paven


class PyProject(msgspec.Struct):
    """Container for the pyproject.toml file."""

    tool: Tool


def load_configuration(directory: Path) -> Paven:
    """Load the configuration from the pyproject.toml file."""
    # Read the contents of the file.
    file = directory / "pyproject.toml"

    def _dec_hook(typ: type[Any], value: Any) -> Any:
        """Convert JSON-compatible values to Python objects."""
        if issubclass(typ, Path):
            return typ(value)
        raise NotImplementedError(f"Unsupported type: {typ}")

    try:
        config = msgspec.convert(
            msgspec.toml.decode(file.read_text()), type=PyProject, dec_hook=_dec_hook
        )
    except msgspec.ValidationError as e:
        raise ValueError("Could not parse pyproject.toml.") from e

    return config.tool.paven


load_configuration(Path())
