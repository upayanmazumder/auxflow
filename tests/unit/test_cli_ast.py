r"""Phase 4 acceptance (sub-issue #29): the `auxflow ast` CLI subcommand."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli


def test_ast_command_exits_zero_and_prints_the_forest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text("\\section{Intro}\nSee \\ref{fig:a}.")

    exit_code = cli.main(["ast", str(doc)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert f"=== {doc} ===" in out
    assert "Document [" in out
    assert "Sectioning(section) [" in out
    assert "MacroCall(\\ref) [" in out


def test_ast_command_reports_diagnostics_for_malformed_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "bad.tex"
    doc.write_text("\\section{unterminated")

    exit_code = cli.main(["ast", str(doc)])

    assert exit_code == 0  # still returns a tree, per the parser's recovery design
    out = capsys.readouterr().out
    assert "warning: unterminated group" in out
    assert "Document [" in out


def test_ast_command_reports_inclusion_cycles(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "self.tex"
    doc.write_text(f"\\input{{{doc}}}")

    exit_code = cli.main(["ast", str(doc)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "warning: inclusion cycle:" in out


def test_ast_command_prints_included_files_and_reports_mutual_cycle(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapter.tex"
    main.write_text("\\input{chapter}")
    chapter.write_text("\\include{main}")

    assert cli.main(["ast", str(main)]) == 0

    out = capsys.readouterr().out
    assert f"=== {main} ===" in out
    assert f"=== {chapter} ===" in out
    assert out.count("Document [") == 2
    assert "warning: inclusion cycle:" in out
    assert str(main) in out.split("warning: inclusion cycle:")[1]
    assert str(chapter) in out.split("warning: inclusion cycle:")[1]
