r"""Phase 4 acceptance (sub-issue #27): visitor-pattern traversal.

The golden test in tests/golden/test_ast_printer_golden.py exercises the
printer, which is built on this traversal but overrides `visit` entirely
and never relies on `visit_<ClassName>` dispatch or `generic_visit`'s
default behaviour. This file tests those directly.
"""

from __future__ import annotations

from auxflow.ast import NodeVisitor, walk
from auxflow.lexer import tokenize
from auxflow.parser import MacroCall, Text, parse


def _document(source: str):
    tokens = tokenize(source, file_id="t.tex")
    return parse(tokens, file_id="t.tex").document


def test_visit_dispatches_to_a_matching_visit_method() -> None:
    seen: list[str] = []

    class Collector(NodeVisitor):
        def visit_MacroCall(self, node: MacroCall) -> None:
            seen.append(node.name)
            self.generic_visit(node)

    Collector().visit(_document("\\ref{a}\\label{b}"))
    assert seen == ["\\ref", "\\label"]


def test_generic_visit_recurses_into_macro_call_argument_content() -> None:
    # Argument is not itself a Node, but the Text nodes inside its content
    # must still be reached by generic_visit.
    seen: list[str] = []

    class Collector(NodeVisitor):
        def visit_Text(self, node: Text) -> None:
            seen.append(node.text)

    Collector().visit(_document("\\label{fig:a}"))
    assert "fig:a" in seen


def test_generic_visit_descends_into_unhandled_node_kinds_by_default() -> None:
    counts: dict[str, int] = {}

    class Counter(NodeVisitor):
        def generic_visit(self, node) -> None:  # type: ignore[no-untyped-def]
            counts[type(node).__name__] = counts.get(type(node).__name__, 0) + 1
            super().generic_visit(node)

    Counter().visit(_document("\\begin{itemize}\\item x\\end{itemize}"))
    assert counts.get("Environment") == 1
    assert counts.get("MacroCall") == 1  # \item


def test_walk_yields_every_node_including_the_root() -> None:
    document = _document("{a}")
    nodes = list(walk(document))
    assert nodes[0] is document
    assert any(type(n).__name__ == "Group" for n in nodes)
    assert any(type(n).__name__ == "Text" for n in nodes)


def test_walk_reaches_nodes_inside_macro_call_arguments() -> None:
    document = _document("\\label{fig:a}")
    texts = [n.text for n in walk(document) if isinstance(n, Text)]
    assert "fig:a" in texts
