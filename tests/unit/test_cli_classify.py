r"""Phase 11 (sub-issue #53): the `auxflow classify` CLI subcommand."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli


def test_amplifying_fixture_emits_amplifying_report_and_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text(
        "\\newcounter{n}\n\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\n"
        "Last page label here\\label{l}.\n"
    )

    exit_code = cli.main(["classify", str(doc)])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert out.startswith("auxflow: AMPLIFYING CYCLE -- this document may not converge.")
    assert "may not converge" in out
    assert "cannot converge" not in out


def test_amplifying_fixture_with_force_exits_zero_and_still_prints_the_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text(
        "\\newcounter{n}\n\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\n"
        "Last page label here\\label{l}.\n"
    )

    exit_code = cli.main(["classify", str(doc), "--force"])

    assert exit_code == 0
    assert "AMPLIFYING CYCLE" in capsys.readouterr().out


def test_certified_fixture_emits_certified_report_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text("\\label{a}\\ref{a}")

    exit_code = cli.main(["classify", str(doc)])

    assert exit_code == 0
    assert capsys.readouterr().out.startswith("auxflow: CERTIFIED --")


def test_unknown_fixture_emits_unknown_report_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text("\\usepackage{exotic}\\label{a}")

    exit_code = cli.main(["classify", str(doc)])

    assert exit_code == 0
    assert capsys.readouterr().out.startswith("auxflow: UNKNOWN --")


def test_unknown_report_groups_repeated_commands_and_keeps_locations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text("\\foo\\foo\\bar")

    assert cli.main(["classify", str(doc)]) == 0
    summary = capsys.readouterr().out
    assert "\\foo" in summary
    assert "\\bar" in summary
    assert "2 occurrences" in summary
    assert f"{doc}:1:1" in summary
    assert len(summary.splitlines()) < 20

    assert cli.main(["classify", str(doc), "--verbose"]) == 0
    detailed = capsys.readouterr().out
    assert f"{doc}:1:5" in detailed


def test_local_unmodelled_class_cannot_be_certified(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "Custom.cls").write_text("\\LoadClass{article}\n\\RequirePackage{acro}\n")
    doc = tmp_path / "main.tex"
    doc.write_text("\\documentclass{Custom}\n\\begin{document}\\label{x}\\ref{x}\\end{document}")

    assert cli.main(["classify", str(doc)]) == 0
    result = capsys.readouterr().out
    assert result.startswith("auxflow: UNKNOWN")
    assert "Custom" in result


def test_inline_verb_text_does_not_change_reference_classification(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(
        "\\documentclass{article}\\begin{document}\\verb|\\pageref{missing}|"
        "\\label{x}\\ref{x}\\end{document}"
    )

    assert cli.main(["classify", str(doc)]) == 0
    assert capsys.readouterr().out.startswith("auxflow: CERTIFIED")
