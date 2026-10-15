r"""Phase 9 (sub-issue #47): STRUCTURAL edge insertion to CONTENT_VOLUME."""

from __future__ import annotations

from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import DepType, FactKind, lower
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, Fact
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.parser.spans import Span
from auxflow.semantic.resolve import declare, resolve

_SPAN = Span("synthetic.tex", 0, 1)


def _lower(source: str) -> ARG:
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def test_amplifying_example_closes_the_documented_cycle_with_a_structural_edge() -> None:
    r"""docs/IR.md "Amplifying cycle": LABEL_PAGE(l) -> PAGEREF_USE(l)
    (AUX_ROUNDTRIP), PAGEREF_USE(l) -> CONTENT_VOLUME (STRUCTURAL, added by
    taint), CONTENT_VOLUME -> LABEL_PAGE(l) (LAYOUT) -- a closed cycle."""
    source = "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\\label{l}"
    graph = _lower(source)
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)

    result = insert_structural_edges(graph, taint)

    volume = next(f for f in result.facts.values() if f.kind is FactKind.CONTENT_VOLUME)
    page_use = next(f for f in result.facts.values() if f.kind is FactKind.PAGEREF_USE)
    label_page = next(f for f in result.facts.values() if f.kind is FactKind.LABEL_PAGE)

    structural = next(
        e for e in result.edges if e.source == page_use.fact_id and e.destination == volume.fact_id
    )
    assert structural.dependency_type is DepType.STRUCTURAL
    assert structural.pass_lag == 1
    assert str(page_use.source_location.start) in structural.reason
    assert str(page_use.source_location.end) in structural.reason

    layout = next(
        e
        for e in result.edges
        if e.source == volume.fact_id
        and e.destination == label_page.fact_id
        and e.dependency_type is DepType.LAYOUT
    )
    roundtrip = next(
        e
        for e in result.edges
        if e.source == label_page.fact_id
        and e.destination == page_use.fact_id
        and e.dependency_type is DepType.AUX_ROUNDTRIP
    )
    assert layout is not None and roundtrip is not None
    # the cycle is fully closed: CONTENT_VOLUME -> LABEL_PAGE -> PAGEREF_USE -> CONTENT_VOLUME
    assert structural.destination == layout.source == volume.fact_id


def test_reason_string_embeds_the_tainted_facts_span_verbatim() -> None:
    facts = {
        0: Fact(0, FactKind.PAGEREF_USE, "l", "value", "engine", None, Span("x.tex", 7, 19)),
        1: Fact(1, FactKind.CONTENT_VOLUME, None, "value", "engine", None, _SPAN),
    }
    arg = ARG(facts=facts, edges=[])

    result = insert_structural_edges(arg, {0})

    (edge,) = result.edges
    assert edge.reason == "value at x.tex:7-19 reaches a content-generating construct"


def test_no_structural_edges_when_the_document_has_no_content_volume() -> None:
    r"""No generated list and no \\newpage/\\clearpage: nothing to connect to."""
    graph = _lower("\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}.")
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)

    result = insert_structural_edges(graph, taint)

    assert taint == set()
    assert result.edges == graph.edges


def test_empty_taint_set_adds_no_edges_even_when_content_volume_exists() -> None:
    facts = {
        0: Fact(0, FactKind.CONTENT_VOLUME, None, "value", "engine", None, _SPAN),
        1: Fact(1, FactKind.LABEL_PAGE, "l", "value", "engine", None, _SPAN),
    }
    arg = ARG(facts=facts, edges=[DepEdge(0, 1, 0, DepType.LAYOUT, "synthetic")])

    result = insert_structural_edges(arg, set())

    assert result is arg
    assert result.edges == arg.edges


def test_structural_is_only_ever_added_here_never_by_lowering() -> None:
    graph = _lower(
        "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\\label{l}"
    )
    assert all(e.dependency_type is not DepType.STRUCTURAL for e in graph.edges)
