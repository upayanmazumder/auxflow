"""Colour is opt-in for pipes, never touches machine output, and always carries plain wording."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from auxflow import cli

_ESC = "\033["


def _doc(tmp_path: Path, text: str = r"\label{a}\ref{a}") -> Path:
    doc = tmp_path / "main.tex"
    doc.write_text(text, encoding="utf-8")
    return doc


def test_piped_output_has_no_colour_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["classify", str(_doc(tmp_path))]) == 0

    assert _ESC not in capsys.readouterr().out


def test_always_colours_the_state_word_and_keeps_the_plain_sentence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["--color", "always", "classify", str(_doc(tmp_path))]) == 0
    out = capsys.readouterr().out

    assert f"{_ESC}1m{_ESC}32mCERTIFIED{_ESC}0m" in out
    assert "In plain terms:" in out


def test_never_overrides_force_color(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")

    assert cli.main(["--color", "never", "classify", str(_doc(tmp_path))]) == 0

    assert _ESC not in capsys.readouterr().out


def test_no_color_environment_beats_auto(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("FORCE_COLOR", "1")

    assert cli.main(["classify", str(_doc(tmp_path))]) == 0

    assert _ESC not in capsys.readouterr().out


def test_machine_output_is_never_coloured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path)

    assert cli.main(["--color", "always", "plan", str(doc)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["classification"] == "CERTIFIED"

    assert cli.main(["--color", "always", "graph", str(doc)]) == 0
    assert _ESC not in capsys.readouterr().out


def test_amplifying_explanation_stays_hedged_and_names_the_escape_hatch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(
        tmp_path,
        "\\newcounter{n}\n\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\n\\label{l}\n",
    )

    assert cli.main(["classify", str(doc)]) == 1
    out = " ".join(capsys.readouterr().out.split())

    assert "may keep changing" in out
    assert "--force" in out
    assert "cannot converge" not in out


def test_check_reports_a_clean_result_on_stderr_and_keeps_stdout_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["check", str(_doc(tmp_path))]) == 0
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "No problems found." in captured.err


def test_check_counts_errors_and_warnings_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, r"\usepackage{exotic}\ref{absent}")

    assert cli.main(["check", str(doc)]) == 1

    assert "Found 1 error(s) and 1 warning(s)." in capsys.readouterr().err
