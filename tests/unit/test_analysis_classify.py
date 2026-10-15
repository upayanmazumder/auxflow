r"""Phase 11 (sub-issue #51): the four-state document classifier."""

from __future__ import annotations

from auxflow.analysis.classify import State, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import lower
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.parser.spans import Span
from auxflow.semantic.resolve import declare, resolve

_SPAN = Span("synthetic.tex", 0, 1)


def _pipeline(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    condensation = build_condensation(graph, components)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, condensation, labels)
    return classify(graph, components, labels, stable_pass)


def test_certified_state_with_n_equal_to_p_plus_one() -> None:
    result = _pipeline("\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}.")

    assert result.state is State.CERTIFIED
    assert result.predicted_runs == 2  # P=1 (REF_USE excluded), N=P+1=2
    assert result.amplifying_components == ()
    assert result.opaque_fact_ids == ()


def test_table_of_contents_is_certified_not_benign_cyclic() -> None:
    r"""docs/IR.md: "With the split, ordinary documents are acyclic." The
    exists/value split makes an ordinary generated-list document CERTIFIED,
    not cyclic at all -- it is the genuine amplifying case (a value
    reaching a content-generating construct) that forms a cycle."""
    result = _pipeline("\\tableofcontents\\section{First}\\label{x}")

    assert result.state is State.CERTIFIED
    assert result.predicted_runs == 3
    assert result.amplifying_components == ()
    assert result.opaque_fact_ids == ()


def test_benign_cyclic_state_on_a_synthetic_pure_layout_cycle() -> None:
    r"""No currently modelled construct produces a real pre-taint cycle
    (the exists/value split is specifically designed to prevent that), so
    BENIGN_CYCLIC -- like phases 8 and 10's own BENIGN tests -- is
    exercised on a synthetic ARG, matching the established pattern."""
    facts = {
        0: Fact(0, FactKind.OPAQUE, None, "value", "engine", None, _SPAN),
        1: Fact(1, FactKind.OPAQUE, None, "value", "engine", None, _SPAN),
    }
    edges = [
        DepEdge(0, 1, 1, DepType.LAYOUT, "cycle edge"),
        DepEdge(1, 0, 1, DepType.LAYOUT, "cycle edge"),
    ]
    arg = ARG(facts=facts, edges=edges)
    components = tarjan(arg)
    labels = classify_components(arg, components)
    condensation = build_condensation(arg, components)
    stable_pass = compute_stable_pass(arg, condensation, labels)

    result = classify(arg, components, labels, stable_pass)

    assert result.state is State.BENIGN_CYCLIC
    assert result.predicted_runs == 4  # stable_pass 3 (base 1 + |C| 2), N = P+1 = 4
    assert result.amplifying_components == ()
    assert result.opaque_fact_ids == ()


def test_amplifying_state_for_forloop_bounded_by_pageref() -> None:
    result = _pipeline(
        "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\\label{l}"
    )

    assert result.state is State.AMPLIFYING
    assert result.predicted_runs is None
    assert len(result.amplifying_components) == 1
    assert len(result.amplifying_components[0]) == 3  # PAGEREF_USE, CONTENT_VOLUME, LABEL_PAGE
    assert result.opaque_fact_ids == ()


def test_unknown_state_for_unmodelled_package() -> None:
    result = _pipeline("\\usepackage{exotic}\\label{a}")

    assert result.state is State.UNKNOWN
    assert result.predicted_runs is None
    assert result.amplifying_components == ()
    assert len(result.opaque_fact_ids) >= 1


def test_amplifying_takes_precedence_over_an_unrelated_opaque_fact() -> None:
    result = _pipeline(
        "\\usepackage{exotic}"
        "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\\label{l}"
    )

    assert result.state is State.AMPLIFYING
