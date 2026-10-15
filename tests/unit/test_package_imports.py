"""Phase 1 acceptance: the package is importable and the CLI surface is fixed.

docs/IMPLEMENTATION-PLAN.md phase 1 deliverable: "empty package importable".
docs/ARCHITECTURE.md fixes the subcommand surface; this test pins it so a
later phase cannot silently add or drop a subcommand without updating the
corresponding doc and plan. Sub-issue #17 acceptance: `import auxflow`
succeeds and `auxflow --help` lists every subcommand stub without raising.
"""

from __future__ import annotations

import pytest

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


def test_cli_help_exits_cleanly_and_lists_every_subcommand() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    assert excinfo.value.code == 0


def test_cli_help_text_lists_every_subcommand() -> None:
    parser = cli.build_parser()
    help_text = parser.format_help()
    for command in cli.COMMANDS:
        assert command in help_text


def test_cli_with_no_command_prints_help_and_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main([])
    assert exit_code == 1
    assert "auxflow" in capsys.readouterr().out


def test_cli_known_subcommand_not_yet_implemented() -> None:
    # run (phase 13) is the only subcommand not yet implemented.
    with pytest.raises(NotImplementedError):
        cli.main(["run", "doc.tex"])
