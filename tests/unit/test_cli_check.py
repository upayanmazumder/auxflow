r"""Phase 6 CLI: errors fail, warnings do not, and spans print."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli


def test_clean_document_exits_zero_without_diagnostics(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "clean.tex"
    doc.write_text("\\usepackage{graphicx}\\label{known}\\ref{known}")

    assert cli.main(["check", str(doc)]) == 0
    assert capsys.readouterr().out == ""


def test_undefined_reference_exits_nonzero_with_source_span(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "bad.tex"
    doc.write_text("\\ref{absent}")

    assert cli.main(["check", str(doc)]) == 1
    assert capsys.readouterr().out == (f"{doc}:1:1: error: undefined reference: 'absent'\n")


def test_warning_only_does_not_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    doc = tmp_path / "unknown-package.tex"
    doc.write_text("\\usepackage{exotic}")

    assert cli.main(["check", str(doc)]) == 0
    assert f"{doc}:1:1: warning: unmodelled package: 'exotic'" in capsys.readouterr().out


def test_cycle_exits_nonzero_with_closing_file_span(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main = tmp_path / "main.tex"
    child = tmp_path / "child.tex"
    main.write_text("\\input{child}")
    child.write_text("\\include{main}")

    assert cli.main(["check", str(main)]) == 1
    out = capsys.readouterr().out
    assert f"{child}:1:1: error: inclusion cycle:" in out
