r"""Phase 11 (sub-issue #54): the two highest-value tests in the project.

docs/NON-CONVERGENCE.md "Testing":
  1. b08 must be classified amplifying, with all three facts named and
     correct spans.
  2. b05 must not be classified amplifying. A classifier that flags every
     document containing a table of contents is worthless, and this
     negative test is the guard against the most likely way for the
     analysis to fail while appearing to work.
"""

from __future__ import annotations

from pathlib import Path

from auxflow.analysis.classify import State, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import FactKind, lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve

_B08_SOURCE = (
    "\\newcounter{n}\n"
    "\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\n"
    "Last page label here\\label{l}.\n"
)
_B05_SOURCE = "\\tableofcontents\n\\section{One}\n\\label{p}\n\\pageref{p}\n"
_CORPUS = Path(__file__).resolve().parents[2] / "bench" / "corpus"


def _pipeline(source: str, file_id: str = "doc.tex"):
    document = parse(tokenize(source, file_id=file_id), file_id=file_id).document
    forest = build_forest({file_id: document})
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    condensation = build_condensation(graph, components)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, condensation, labels)
    return graph, classify(graph, components, labels, stable_pass)


def test_b08_is_amplifying_with_all_three_cycle_facts_named_at_correct_spans() -> None:
    graph, result = _pipeline(_B08_SOURCE)

    assert result.state is State.AMPLIFYING
    (cycle,) = result.amplifying_components
    kinds = {graph.facts[fact_id].kind for fact_id in cycle}
    assert kinds == {FactKind.PAGEREF_USE, FactKind.CONTENT_VOLUME, FactKind.LABEL_PAGE}

    pageref = next(f for f in graph.facts.values() if f.kind is FactKind.PAGEREF_USE)
    volume = next(f for f in graph.facts.values() if f.kind is FactKind.CONTENT_VOLUME)
    label_page = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_PAGE)

    assert pageref.source_location.start == _B08_SOURCE.index("\\pageref")
    assert volume.source_location.start == _B08_SOURCE.index("\\newpage")
    assert label_page.source_location.start == _B08_SOURCE.index("\\label")
    for fact_id in cycle:
        span = graph.facts[fact_id].source_location
        assert span.file_id == "doc.tex"
        assert span.end > span.start


def test_b05_table_of_contents_is_not_classified_amplifying() -> None:
    r"""A classifier that flags every document containing a table of
    contents is worthless. This is the guard against the most likely way
    for the analysis to fail while appearing to work."""
    _graph, result = _pipeline(_B05_SOURCE)

    assert result.state is not State.AMPLIFYING
    assert result.amplifying_components == ()
    # docs/IR.md's exists/value split makes an ordinary generated-list
    # document acyclic by construction (see test_analysis_classify.py), so
    # this lands CERTIFIED; NON-CONVERGENCE.md itself only requires "not
    # amplifying", which holds either way.
    assert result.state is State.CERTIFIED


def test_width_sensitive_page_reference_does_not_claim_certified_bound() -> None:
    source = (_CORPUS / "b11_width" / "main.tex").read_text(encoding="utf-8")
    graph, result = _pipeline(source)

    assert result.state is State.UNKNOWN
    assert result.predicted_runs is None
    assert any(
        graph.facts[fact_id].source_location.start == source.index(r"\pageref")
        for fact_id in result.opaque_fact_ids
    )


def test_float_placement_with_page_reference_does_not_claim_certified_bound() -> None:
    source = (_CORPUS / "b12_float" / "main.tex").read_text(encoding="utf-8")
    graph, result = _pipeline(source)

    assert result.state is State.UNKNOWN
    assert result.predicted_runs is None
    assert any(
        graph.facts[fact_id].source_location.start == source.index(r"\pageref")
        for fact_id in result.opaque_fact_ids
    )


def test_varioref_page_feedback_does_not_claim_certified_bound() -> None:
    source = (_CORPUS / "b13_varioref" / "main.tex").read_text(encoding="utf-8")
    graph, result = _pipeline(source)

    assert result.state is State.UNKNOWN
    assert result.predicted_runs is None
    assert any(
        graph.facts[fact_id].source_location.start == source.index(r"\vpageref")
        for fact_id in result.opaque_fact_ids
    )


def test_forward_references_with_arabic_numbering_remain_certified() -> None:
    source = r"See \ref{target}, page \pageref{target}. Later\section{Target}\label{target}"
    _graph, result = _pipeline(source)

    assert result.state is State.CERTIFIED


def test_roman_numbering_page_reference_has_unmodelled_width_feedback() -> None:
    source = r"\pagenumbering{roman}\label{target}See page \pageref{target}."
    graph, result = _pipeline(source)

    assert result.state is State.UNKNOWN
    assert any(
        graph.facts[fact_id].source_location.start == source.index(r"\pageref")
        for fact_id in result.opaque_fact_ids
    )


def test_roman_numbering_without_page_reference_remains_certified() -> None:
    _graph, result = _pipeline(r"\pagenumbering{Roman}\label{a}See \ref{a}.")

    assert result.state is State.CERTIFIED


def test_varioref_short_form_still_has_unmodelled_page_dependent_text() -> None:
    source = r"\usepackage{varioref}\label{target}See \vref{target}."
    graph, result = _pipeline(source)

    assert result.state is State.UNKNOWN
    assert any(
        graph.facts[fact_id].source_location.start == source.index(r"\vref")
        for fact_id in result.opaque_fact_ids
    )


def test_backward_page_reference_and_isolated_float_remain_certified() -> None:
    for source in (
        r"\label{target}See page \pageref{target}.",
        r"\begin{figure}\caption{Static image}\end{figure}",
    ):
        _graph, result = _pipeline(source)
        assert result.state is State.CERTIFIED
