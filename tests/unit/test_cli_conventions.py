"""Standard CLI conventions: --version, clear input errors, examples in help."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli


def test_version_flag_prints_the_name_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.startswith("auxflow ")


@pytest.mark.parametrize("command", cli.COMMANDS)
def test_missing_file_is_a_clear_error_not_a_traceback(
    command: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main([command, str(tmp_path / "absent.tex")]) == 2
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "no such file" in captured.err
    assert "Traceback" not in captured.err


def test_directory_argument_says_to_give_the_main_tex_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["classify", str(tmp_path)]) == 2

    assert "is a directory" in capsys.readouterr().err


def test_binary_file_is_reported_as_not_utf8_text(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    blob = tmp_path / "main.tex"
    blob.write_bytes(b"\xff\xfe\x00\x80")

    assert cli.main(["check", str(blob)]) == 2

    assert "not UTF-8 text" in capsys.readouterr().err


def test_readable_file_is_not_rejected(tmp_path: Path) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(r"\label{a}\ref{a}", encoding="utf-8")

    assert cli.main(["check", str(doc)]) == 0


@pytest.mark.parametrize("command", cli.COMMANDS)
def test_every_command_help_ends_with_a_runnable_example(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["help", command]) == 0
    out = capsys.readouterr().out

    assert f"auxflow {command}" in out.split("example", 1)[1]
