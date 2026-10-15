r"""Phase 4 acceptance (sub-issue #27): the printer output is stable across
runs and covers every node kind; golden-style comparison for a fixture
document.

The fixture (fixtures/simple_document.tex) exercises documentclass,
usepackage, the document environment, sectioning, ref, a nested figure
environment, includegraphics with an optional argument, caption and label --
most of the node kinds a real document produces. Regenerate the golden file
only deliberately (tests/README.md: golden snapshots are "regenerated
deliberately and never automatically").
"""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import print_tree
from auxflow.lexer import tokenize
from auxflow.parser import parse

_FIXTURES = Path(__file__).parent / "fixtures"


def test_printed_ast_matches_the_golden_file() -> None:
    source = (_FIXTURES / "simple_document.tex").read_text()
    expected = (_FIXTURES / "simple_document.ast.txt").read_text()

    tokens = tokenize(source, file_id="simple_document.tex")
    result = parse(tokens, file_id="simple_document.tex")
    assert result.diagnostics == ()

    assert print_tree(result.document) + "\n" == expected


def test_printer_output_is_stable_across_runs() -> None:
    source = (_FIXTURES / "simple_document.tex").read_text()
    tokens = tokenize(source, file_id="simple_document.tex")
    document = parse(tokens, file_id="simple_document.tex").document

    first = print_tree(document)
    second = print_tree(document)
    assert first == second

    # a fresh parse of the same source produces identical output too --
    # nothing in the printer depends on object identity or id()-order.
    tokens_again = tokenize(source, file_id="simple_document.tex")
    document_again = parse(tokens_again, file_id="simple_document.tex").document
    assert print_tree(document_again) == first
