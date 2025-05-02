"""Logic for cleaning up already vendored files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from paven.utils import remove_all

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from paven.configuration import Paven


def determine_items_to_remove(destination: Path, *, files_to_skip: list[str]) -> Iterable[Path]:
    """Determines which items to remove from the destination directory."""
    if not destination.exists():
        # Folder does not exist, nothing to cleanup.
        return

    for item in destination.iterdir():
        if item.is_dir():
            # Directory
            yield item
        elif item.name not in files_to_skip:
            # File, not in files_to_skip
            yield item


def cleanup_existing_vendored(config: Paven) -> None:
    """Cleans up existing vendored files in `destination` directory."""
    destination = config.destination
    items = determine_items_to_remove(destination, files_to_skip=config.protected_files)

    remove_all(items, protected=[config.requirements])
