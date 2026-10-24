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


def test_nested_chapter_finds_explicit_and_inferred_graphics_at_entry_root(
    tmp_path: Path,
) -> None:
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapters" / "part"
    chapter.mkdir(parents=True)
    middle = tmp_path / "chapters" / "chapter.tex"
    leaf = chapter / "leaf.tex"
    images = tmp_path / "images"
    images.mkdir()
    (images / "sample-graph.pdf").write_bytes(b"pdf")
    source = (
        "before \\includegraphics{images/sample-graph.pdf} \\includegraphics{images/sample-graph}"
    )
    forest = build_forest(
        {
            str(main): _document(main, "\\input{chapters/chapter}"),
            str(middle): _document(middle, "\\input{part/leaf}"),
            str(leaf): _document(leaf, source),
        }
    )

    assert check_inclusions(forest) == []


def test_nested_chapter_uses_local_directory_without_other_document_directories(
    tmp_path: Path,
) -> None:
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapters"
    chapter.mkdir()
    leaf = chapter / "leaf.tex"
    (chapter / "local.png").write_bytes(b"png")
    unrelated = tmp_path / "other"
    unrelated.mkdir()
    other_main = unrelated / "main.tex"
    (unrelated / "foreign.pdf").write_bytes(b"pdf")
    source = "\\includegraphics{local}\\includegraphics{foreign}"
    forest = build_forest(
        {
            str(main): _document(main, "\\input{chapters/leaf}"),
            str(leaf): _document(leaf, source),
            str(other_main): _document(other_main, "other document"),
        }
    )

    diagnostics = check_inclusions(forest)

    assert len(diagnostics) == 1
    assert diagnostics[0].message == "missing graphics file: foreign"
    assert diagnostics[0].span.file_id == str(leaf)
    assert diagnostics[0].span.start == source.index("\\includegraphics{foreign}")


def test_nested_chapter_still_reports_missing_root_graphic_at_its_macro(
    tmp_path: Path,
) -> None:
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapters"
    chapter.mkdir()
    leaf = chapter / "leaf.tex"
    source = "prefix \\includegraphics{images/gone.pdf} suffix"
    forest = build_forest(
        {
            str(main): _document(main, "\\input{chapters/leaf}"),
            str(leaf): _document(leaf, source),
        }
    )

    diagnostics = check_inclusions(forest)

    assert len(diagnostics) == 1
    assert diagnostics[0].message == "missing graphics file: images/gone.pdf"
    assert diagnostics[0].span.file_id == str(leaf)
    assert diagnostics[0].span.start == source.index("\\includegraphics")


def test_same_named_local_and_root_graphics_are_both_valid_locations(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    chapter = tmp_path / "chapters"
    chapter.mkdir()
    leaf = chapter / "leaf.tex"
    (tmp_path / "plot.pdf").write_bytes(b"root")
    (chapter / "plot.pdf").write_bytes(b"local")
    source = "\\includegraphics{plot.pdf}"
    forest = build_forest(
        {
            str(main): _document(main, "\\input{chapters/leaf}"),
            str(leaf): _document(leaf, source),
        }
    )

    assert check_inclusions(forest) == []
    (tmp_path / "plot.pdf").unlink()
    assert check_inclusions(forest) == []
    (chapter / "plot.pdf").unlink()
    diagnostics = check_inclusions(forest)
    assert len(diagnostics) == 1
    assert diagnostics[0].message == "missing graphics file: plot.pdf"
    assert diagnostics[0].span.file_id == str(leaf)
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
