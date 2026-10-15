"""Phase 1 acceptance: the package is importable and the CLI surface is fixed.

docs/IMPLEMENTATION-PLAN.md phase 1 deliverable: "empty package importable".
docs/ARCHITECTURE.md fixes the subcommand surface; this test pins it so a
later phase cannot silently add or drop a subcommand without updating the
corresponding doc and plan.
"""

from __future__ import annotations

import auxflow
from auxflow import cli


def test_package_imports() -> None:
    assert auxflow is not None


def test_cli_entry_point_is_callable() -> None:
    assert callable(cli.main)


def test_cli_command_surface_matches_architecture() -> None:
    # One entry per phase that ships a subcommand, per docs/ARCHITECTURE.md.
    assert cli.COMMANDS == (
        "tokens",
        "ast",
        "symbols",
        "check",
        "graph",
        "classify",
        "plan",
        "run",
    )
