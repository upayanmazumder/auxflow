r"""Phase 6 name diagnostics: missing references, citations, duplicate labels."""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.diagnostics import check_symbols
from auxflow.semantic.resolve import declare, resolve


def _check(source: str, file_id: str):
    document = parse(tokenize(source, file_id=file_id), file_id=file_id).document
    forest = build_forest({file_id: document})
    return check_symbols(resolve(forest, declare(forest)))


def test_undefined_reference_citation_and_duplicate_have_exact_spans() -> None:
    source = "\\ref{absent}\\cite{missing}\\label{twice}\\label{twice}"

    diagnostics = _check(source, "main.tex")

    assert len(diagnostics) == 3
    by_message = {d.message: d.span for d in diagnostics}
    assert by_message["undefined reference: 'absent'"].start == source.index("\\ref")
    assert by_message["undefined citation: 'missing'"].start == source.index("\\cite")
    assert by_message["duplicate label: 'twice'"].start == source.rindex("\\label")
    assert all(span.file_id == "main.tex" for span in by_message.values())
    assert all(span.end > span.start for span in by_message.values())


def test_citation_present_in_bibliography_has_no_diagnostic(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    (tmp_path / "refs.bib").write_text("@article{known,\n  title={Known}\n}\n")
    source = "\\cite{known}\\bibliography{refs}"

    assert _check(source, str(main)) == []
