"""`auxflow help` is a command, not only a flag, and it works without a TeX engine."""

from __future__ import annotations

import pytest

from auxflow import cli


def test_help_lists_every_command_and_the_exit_codes(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["help"]) == 0
    out = capsys.readouterr().out

    for command in cli.COMMANDS:
        assert command in out
    assert "Exit status" in out
    assert "NO_COLOR" in out


def test_help_for_one_command_shows_its_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["help", "classify"]) == 0
    out = capsys.readouterr().out

    assert "usage: auxflow classify" in out
    assert "--force" in out
    assert "--verbose" in out


def test_help_for_an_unknown_command_fails_and_names_the_choices(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["help", "frobnicate"]) == 2
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "no command named 'frobnicate'" in captured.err
    assert "classify" in captured.err


def test_running_with_no_command_shows_the_overview_and_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main([]) == 1

    assert "Typical use" in capsys.readouterr().out


def test_top_level_help_text_gives_each_command_a_summary() -> None:
    text = cli.build_parser().format_help()

    assert "find undefined references" in text
    assert "show help for AuxFlow" in text


def test_help_has_no_colour_in_a_pipe(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["help"]) == 0

    assert "\033[" not in capsys.readouterr().out
