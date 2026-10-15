r"""Phase 6 file diagnostics: missing include, graphics and cycle spans."""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.inclusion import check_inclusions


def _document(path: Path, source: str):
    path.write_text(source)
    return parse(tokenize(source, file_id=str(path)), file_id=str(path)).document


def test_missing_include_reports_source_macro_span(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    source = "before \\input{absent} after"
    forest = build_forest({str(main): _document(main, source)})

    diagnostics = check_inclusions(forest)

    assert len(diagnostics) == 1
    assert "unresolvable inclusion" in diagnostics[0].message
    assert diagnostics[0].span.file_id == str(main)
    assert diagnostics[0].span.start == source.index("\\input")


def test_missing_graphics_reports_macro_span_and_existing_png_is_accepted(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    source = "\\includegraphics[width=1cm]{absent.png}\\includegraphics{plot}"
    (tmp_path / "plot.png").write_bytes(b"image")
    forest = build_forest({str(main): _document(main, source)})

    diagnostics = check_inclusions(forest)

    assert len(diagnostics) == 1
    assert diagnostics[0].message == "missing graphics file: absent.png"
    assert diagnostics[0].span.file_id == str(main)
    assert diagnostics[0].span.start == 0


def test_two_file_cycle_reports_closing_include_span(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    child = tmp_path / "child.tex"
    forest = build_forest(
        {
            str(main): _document(main, "\\input{child}"),
            str(child): _document(child, "\\include{main}"),
        }
    )

    diagnostics = check_inclusions(forest)

    assert len(diagnostics) == 1
    assert diagnostics[0].message == f"inclusion cycle: {main} -> {child} -> {main}"
    assert diagnostics[0].span.file_id == str(child)
    assert diagnostics[0].span.start == 0
