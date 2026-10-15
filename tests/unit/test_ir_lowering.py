r"""Phase 7 lowering preserves construct instances and typed dependencies."""

from __future__ import annotations

from auxflow.ast import build_forest
from auxflow.ir import DepType, FactKind, lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _lower(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def test_modelled_constructs_create_distinct_facts_and_typed_edges() -> None:
    graph = _lower(
        "\\tableofcontents\\listoffigures"
        "\\section{One}\\label{a}\\ref{a}\\pageref{a}"
        "\\begin{figure}\\caption{Plot}\\end{figure}"
        "\\cite{paper}\\bibliography{refs}"
        "\\section{Two}\\label{b}\\ref{b}"
    )
    facts = list(graph.facts.values())
    kinds = {fact.kind for fact in facts}
    assert {
        FactKind.LABEL_NUMBER,
        FactKind.LABEL_PAGE,
        FactKind.REF_USE,
        FactKind.PAGEREF_USE,
        FactKind.TOC_ENTRY,
        FactKind.LOF_ENTRY,
        FactKind.CITE_USE,
        FactKind.BBL,
        FactKind.LIST_EXTENT,
        FactKind.CONTENT_VOLUME,
    } <= kinds
    entries = [fact for fact in facts if fact.kind is FactKind.TOC_ENTRY]
    assert {fact.component for fact in entries} == {"exists", "value"}
    assert len([fact for fact in entries if fact.component == "exists"]) == 3
    assert len([fact for fact in facts if fact.kind is FactKind.LABEL_NUMBER]) == 2
    assert len([fact for fact in facts if fact.kind is FactKind.REF_USE]) == 2
    assert len({fact.fact_id for fact in facts}) == len(facts)
    assert all(fact.source_location.file_id == "main.tex" for fact in facts)
    assert all(fact.source_location.end > fact.source_location.start for fact in facts)
    assert {edge.dependency_type for edge in graph.edges} == {
        DepType.AUX_ROUNDTRIP,
        DepType.LAYOUT,
        DepType.TOOL,
    }
    for edge in graph.edges:
        assert edge.source in graph.facts
        assert edge.destination in graph.facts
        assert edge.source in graph.facts[edge.destination].dependencies
        assert edge.reason


def test_unsupported_macro_marks_document_facts_opaque() -> None:
    graph = _lower("\\label{a}\\csname unknown\\endcsname")
    assert any(f.kind is FactKind.OPAQUE for f in graph.facts.values())
    assert all(f.opaque for f in graph.facts.values())


def test_b08_control_bound_produces_page_reference_and_counter_read_facts() -> None:
    source = "\\newcounter{n}\\forloop{n}{0}{\\value{n}<\\pageref{last}}{~\\newpage}\\label{last}"
    graph = _lower(source)

    page_uses = [fact for fact in graph.facts.values() if fact.kind is FactKind.PAGEREF_USE]
    counter_reads = [fact for fact in graph.facts.values() if fact.kind is FactKind.COUNTER_READ]
    assert len(page_uses) == len(counter_reads) == 1
    assert page_uses[0].metadata["control_role"] == "condition"
    assert counter_reads[0].metadata["control_role"] == "condition"
    assert not any(fact.kind is FactKind.OPAQUE for fact in graph.facts.values())

    # docs/IR.md "Amplifying cycle": \newpage (a page-emission primitive)
    # makes CONTENT_VOLUME exist even though no generated list is present;
    # LABEL_PAGE(last) <-> PAGEREF_USE(last) <-> CONTENT_VOLUME closes once
    # taint (phase 9) adds the STRUCTURAL edge.
    volume = [fact for fact in graph.facts.values() if fact.kind is FactKind.CONTENT_VOLUME]
    label_page = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_PAGE)
    assert len(volume) == 1
    assert volume[0].source_location.start == source.index("\\newpage")
    assert volume[0].fact_id in label_page.dependencies
    assert any(
        e.source == volume[0].fact_id
        and e.destination == label_page.fact_id
        and e.dependency_type is DepType.LAYOUT
        for e in graph.edges
    )


def test_macro_definition_body_is_not_lowered_and_marks_facts_opaque() -> None:
    graph = _lower("\\newcommand{\\saved}{\\label{hidden}}\\label{visible}")

    labels = [fact.key for fact in graph.facts.values() if fact.kind is FactKind.LABEL_NUMBER]
    assert labels == ["visible"]
    assert any(fact.kind is FactKind.OPAQUE for fact in graph.facts.values())
    assert all(fact.opaque for fact in graph.facts.values())


def test_backward_reference_worked_example_matches_ir_md_exactly() -> None:
    r"""docs/IR.md "Backward reference, no generated lists": \chapter without
    \tableofcontents produces no TOC_ENTRY/LIST_EXTENT/CONTENT_VOLUME -- a
    sectioning construct always writes a potential list entry (matching real
    LaTeX's unconditional \addcontentsline), but it only affects pagination
    when a generated list (\tableofcontents) is actually present to
    typeset it. The document needs exactly LABEL_NUMBER(c:one).value and
    REF_USE(c:one), linked by one AUX_ROUNDTRIP lag-1 edge.
    """
    graph = _lower("\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}.")

    kinds = {(fact.kind, fact.component) for fact in graph.facts.values()}
    assert kinds == {
        (FactKind.LABEL_NUMBER, "value"),
        (FactKind.LABEL_PAGE, "value"),
        (FactKind.REF_USE, "value"),
    }
    assert len(graph.edges) == 1
    edge = graph.edges[0]
    label_number = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_NUMBER)
    ref_use = next(f for f in graph.facts.values() if f.kind is FactKind.REF_USE)
    assert edge.source == label_number.fact_id
    assert edge.destination == ref_use.fact_id
    assert edge.dependency_type is DepType.AUX_ROUNDTRIP
    assert edge.pass_lag == 1
    # LABEL_PAGE exists per \label's rule but has no edges: no generated
    # list means CONTENT_VOLUME is never instantiated for this document.
    label_page = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_PAGE)
    assert label_page.dependencies == ()
    assert not any(f.kind is FactKind.CONTENT_VOLUME for f in graph.facts.values())
