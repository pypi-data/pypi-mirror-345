"""Utility functions for Paven."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def remove_all(items_to_cleanup: Iterable[Path], *, protected: list[Path]) -> None:
    """Removes all items in the given list of paths."""
    for item in items_to_cleanup:
        if not item.exists():
            continue
        if item in protected:
            continue
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()


def remove_matching_regex(path: Path, pattern: str) -> None:
    """Removes all items matching the given regex pattern in the given path."""
    compiled = re.compile(pattern)
    for dirpath_str, dirnames, filenames in os.walk(path):
        dirpath = Path(dirpath_str)
        rel_dirpath = dirpath.relative_to(path)
        # Delete matching folders
        for dirname in dirnames:
            if compiled.match((rel_dirpath / dirname).as_posix()):
                dirnames.remove(dirname)
                shutil.rmtree(dirpath / dirname)
        # Delete matching files
        for filename in filenames:
            if compiled.match((rel_dirpath / filename).as_posix()):
                (dirpath / filename).unlink()
