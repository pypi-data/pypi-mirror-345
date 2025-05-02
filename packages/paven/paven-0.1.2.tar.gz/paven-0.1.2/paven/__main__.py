"""Run the paven tool as a script."""

from __future__ import annotations

from pathlib import Path

import doctyper

from paven.configuration import load_configuration
from paven.sync import revert_sync, run_sync


def run_paven(directory: Path = Path(), revert: bool = False) -> None:
    """Sync (or revert) vendored dependencies.

    Args:
        directory: Directory with a pyproject.toml file.
        revert: Whether to remove vendored dependencies and undo rewriting of import statements.
    """
    config = load_configuration(directory)
    if revert:
        revert_sync(config)
    else:
        run_sync(config)


if __name__ == "__main__":
    app = doctyper.SlimTyper(help=__doc__)
    app.command()(run_paven)
    app()
