r"""Phase 7 list components and the document-dependent bibliography chain."""

from __future__ import annotations

from collections import deque

from auxflow.ast import build_forest
from auxflow.ir import DepType, FactKind, lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _lower(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def _acyclic(facts, edges) -> bool:
    incoming = {fact_id: 0 for fact_id in facts}
    outgoing = {fact_id: [] for fact_id in facts}
    for edge in edges:
        incoming[edge.destination] += 1
        outgoing[edge.source].append(edge.destination)
    queue = deque(fact_id for fact_id, degree in incoming.items() if degree == 0)
    visited = 0
    while queue:
        visited += 1
        for target in outgoing[queue.popleft()]:
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    return visited == len(facts)


def test_toc_exists_affects_extent_but_not_its_own_value() -> None:
    source = "\\tableofcontents\\section{First}\\section{Second}"
    graph = _lower(source)
    entries = [fact for fact in graph.facts.values() if fact.kind is FactKind.TOC_ENTRY]
    exists = [fact for fact in entries if fact.component == "exists"]
    values = [fact for fact in entries if fact.component == "value"]
    volume = [fact for fact in graph.facts.values() if fact.kind is FactKind.CONTENT_VOLUME]
    extent = [fact for fact in graph.facts.values() if fact.kind is FactKind.LIST_EXTENT]

    assert len(exists) == len(values) == 2
    assert len(volume) == len(extent) == 1
    assert volume[0].source_location.start == source.index("\\section")
    for entry in exists:
        assert entry.fact_id in extent[0].dependencies
        assert volume[0].fact_id not in entry.dependencies
    for entry in values:
        assert volume[0].fact_id in entry.dependencies
    assert extent[0].fact_id in volume[0].dependencies
    assert _acyclic(graph.facts, graph.edges)


def test_bibliography_cascade_has_the_document_specific_chain() -> None:
    graph = _lower("\\tableofcontents\\cite{k}\\bibliography{refs}\\label{last}\\pageref{last}")

    def only(kind: FactKind, component: str):
        matches = [
            fact
            for fact in graph.facts.values()
            if fact.kind is kind and fact.component == component
        ]
        assert len(matches) == 1
        return matches[0]

    cite = only(FactKind.CITE_USE, "value")
    bbl_exists = only(FactKind.BBL, "exists")
    only(FactKind.BBL, "value")
    toc_exists = only(FactKind.TOC_ENTRY, "exists")
    toc_value = only(FactKind.TOC_ENTRY, "value")
    extent = only(FactKind.LIST_EXTENT, "value")
    volume = only(FactKind.CONTENT_VOLUME, "value")
    only(FactKind.LABEL_NUMBER, "value")
    page = only(FactKind.LABEL_PAGE, "value")
    page_use = only(FactKind.PAGEREF_USE, "value")

    edges = {(e.source, e.destination, e.dependency_type, e.pass_lag) for e in graph.edges}
    assert edges == {
        (cite.fact_id, bbl_exists.fact_id, DepType.TOOL, 1),
        (bbl_exists.fact_id, toc_exists.fact_id, DepType.LAYOUT, 1),
        (toc_exists.fact_id, extent.fact_id, DepType.LAYOUT, 0),
        (extent.fact_id, volume.fact_id, DepType.LAYOUT, 1),
        (volume.fact_id, toc_value.fact_id, DepType.LAYOUT, 0),
        (volume.fact_id, page.fact_id, DepType.LAYOUT, 0),
        (page.fact_id, page_use.fact_id, DepType.AUX_ROUNDTRIP, 1),
    }
    assert len(graph.facts) == 10
    assert _acyclic(graph.facts, graph.edges)
