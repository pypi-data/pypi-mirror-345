"""Core logic of the sync task."""

# ruff: noqa: ERA001
from __future__ import annotations

from typing import TYPE_CHECKING

from paven.cleanup import cleanup_existing_vendored

# from paven.license import fetch_licenses
# from paven.stubs import generate_stubs
from paven.vendor import rewrite_imports, vendor_libraries

if TYPE_CHECKING:
    from paven.configuration import Paven


def run_sync(config: Paven) -> None:
    """Run the sync task."""
    cleanup_existing_vendored(config)
    vendor_libraries(config)
    # fetch_licenses(config)
    # generate_stubs(config, libraries)


def revert_sync(config: Paven) -> None:
    """Run the unsync task."""
    cleanup_existing_vendored(config)

    # Rewrite the imports we want changed.
    vendored_libs: list[str] = []  # we dont have to know which libraries are vendored for unsyncing
    # only additional as the namespace is removed anyway.
    rewrite_imports(
        config.root,
        config.namespace,
        vendored_libs,
        config.transformations.substitute,
        reverse=True,
    )
