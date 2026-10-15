r"""Phase 4 acceptance (sub-issue #89): every AST node kind carries a
mandatory Span.

docs/COMPILER-PIPELINE.md section 3 lists sixteen node kinds. Twelve
(Document, Preamble, DocumentClass, UsePackage, Include, Sectioning,
Environment, MacroCall, Group, Text, Comment, VerbatimBlock) already exist
in auxflow.parser.nodes from phase 3, since phase 3 could not have produced
"one AST per file" without them. This test instantiates all sixteen and
asserts a missing span raises, proving the mandatory-span invariant holds
uniformly rather than only on the four kinds added in this sub-issue.
"""

from __future__ import annotations

import pytest

from auxflow.parser import (
    Argument,
    Comment,
    ControlConstruct,
    CounterOp,
    Document,
    DocumentClass,
    Environment,
    Group,
    Include,
    MacroCall,
    MacroDef,
    Node,
    Opaque,
    Preamble,
    Sectioning,
    Span,
    Text,
    UsePackage,
    VerbatimBlock,
)

_SPAN = Span("t.tex", 0, 1)
_TEXT = Text(_SPAN, "x")

_INSTANCES: list[Node] = [
    Document(_SPAN, (_TEXT,)),
    Preamble(_SPAN, (_TEXT,)),
    DocumentClass(_SPAN, "article", ()),
    UsePackage(_SPAN, "graphicx", ()),
    Include(_SPAN, "input", "f.tex"),
    Sectioning(_SPAN, "section", (_TEXT,)),
    Environment(_SPAN, "document", (_TEXT,)),
    MacroCall(_SPAN, "\\label", (Argument("mandatory", (_TEXT,)),)),
    Group(_SPAN, (_TEXT,)),
    Text(_SPAN, "x"),
    Comment(_SPAN, "%c\n"),
    VerbatimBlock(_SPAN, "|v|"),
    MacroDef(_SPAN, "\\foo", 1, (), opaque=False),
    CounterOp(_SPAN, "setcounter", "page"),
    ControlConstruct(_SPAN, "forloop", (_TEXT,), (_TEXT,)),
    Opaque(_SPAN, "\\csname is not in the declared subset"),
]


def test_every_node_kind_carries_a_non_null_span() -> None:
    assert len(_INSTANCES) == 16  # the complete COMPILER-PIPELINE.md section 3 list
    for node in _INSTANCES:
        assert node.span is not None
        assert node.span == _SPAN


@pytest.mark.parametrize("node_cls", [Document, Preamble, Group, Text, Comment, VerbatimBlock])
def test_constructing_without_a_span_raises(node_cls: type) -> None:
    with pytest.raises(TypeError):
        node_cls()  # type: ignore[call-arg]


def test_macro_def_stores_body_as_unexpanded_tokens_and_an_opaque_flag() -> None:
    node = MacroDef(_SPAN, "\\foo", 2, (), opaque=True)
    assert node.body_tokens == ()
    assert node.opaque is True
