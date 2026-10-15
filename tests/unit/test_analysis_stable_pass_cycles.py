r"""Phase 10 (sub-issue #49): condensation walk, BENIGN heuristic and
unbounded (AMPLIFYING/UNKNOWN_CYCLE) propagation."""

from __future__ import annotations

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


def _fact(fact_id: int, opaque: bool = False) -> Fact:
    return Fact(fact_id, FactKind.OPAQUE, None, "value", "engine", None, _SPAN, opaque=opaque)


def _pipeline(arg: ARG):
    components = tarjan(arg)
    condensation = build_condensation(arg, components)
    labels = classify_components(arg, components)
    return compute_stable_pass(arg, condensation, labels)


def test_amplifying_cycle_example_assigns_none_to_all_three_facts() -> None:
    document = parse(
        tokenize(
            "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\\label{l}",
            file_id="main.tex",
        ),
        file_id="main.tex",
    ).document
    forest = build_forest({"main.tex": document})
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)

    result = _pipeline(graph)

    volume = next(f for f in graph.facts.values() if f.kind is FactKind.CONTENT_VOLUME)
    label_page = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_PAGE)
    page_use = next(f for f in graph.facts.values() if f.kind is FactKind.PAGEREF_USE)
    assert result[volume.fact_id] is None
    assert result[label_page.fact_id] is None
    assert result[page_use.fact_id] is None


def test_benign_two_cycle_with_a_stable_pass_one_predecessor_yields_four() -> None:
    # predecessor(0) -> A(1) <-> B(2): a pure LAYOUT/AUX_ROUNDTRIP 2-cycle
    # fed by one bounded predecessor with stable_pass 1.
    facts = {0: _fact(0), 1: _fact(1), 2: _fact(2)}
    edges = [
        DepEdge(0, 1, 1, DepType.AUX_ROUNDTRIP, "predecessor feeds the cycle"),
        DepEdge(1, 2, 1, DepType.LAYOUT, "cycle edge"),
        DepEdge(2, 1, 1, DepType.LAYOUT, "cycle edge"),
    ]
    arg = ARG(facts=facts, edges=edges)

    result = _pipeline(arg)

    assert result[0] == 1
    assert result[1] == result[2] == 4  # base (1 + pred's 1 = 2) + |C| (2) = 4


def test_unknown_cycle_with_an_opaque_member_is_also_unbounded() -> None:
    facts = {0: _fact(0, opaque=True), 1: _fact(1)}
    edges = [
        DepEdge(0, 1, 1, DepType.LAYOUT, "cycle edge"),
        DepEdge(1, 0, 1, DepType.LAYOUT, "cycle edge"),
    ]
    arg = ARG(facts=facts, edges=edges)

    result = _pipeline(arg)

    assert result[0] is None
    assert result[1] is None


def test_benign_cycle_base_is_one_with_no_predecessors() -> None:
    facts = {0: _fact(0), 1: _fact(1)}
    edges = [
        DepEdge(0, 1, 1, DepType.LAYOUT, "cycle edge"),
        DepEdge(1, 0, 1, DepType.LAYOUT, "cycle edge"),
    ]
    arg = ARG(facts=facts, edges=edges)

    result = _pipeline(arg)

    assert result[0] == result[1] == 3  # base (1 + max(default=0)) + |C| (2) = 3


def test_benign_cycle_ignores_an_unbounded_predecessor_in_its_base() -> None:
    # An AMPLIFYING singleton self-loop (3) feeds the benign cycle {1,2}, but
    # the heuristic base only counts BOUNDED predecessors (docs/STATIC-ANALYSIS.md
    # section 4: "max(stable_pass[g] for g in preds(C) if bounded, default 0)").
    facts = {0: _fact(0), 1: _fact(1), 2: _fact(2), 3: _fact(3)}
    edges = [
        DepEdge(3, 3, 1, DepType.STRUCTURAL, "self-loop, amplifying"),
        DepEdge(0, 1, 1, DepType.AUX_ROUNDTRIP, "bounded predecessor"),
        DepEdge(3, 1, 1, DepType.AUX_ROUNDTRIP, "unbounded predecessor"),
        DepEdge(1, 2, 1, DepType.LAYOUT, "cycle edge"),
        DepEdge(2, 1, 1, DepType.LAYOUT, "cycle edge"),
    ]
    arg = ARG(facts=facts, edges=edges)

    result = _pipeline(arg)

    assert result[3] is None
    assert result[0] == 1
    assert result[1] == result[2] == 4  # base (1 + 0's 1 = 2) + |C| (2) = 4, 3 excluded
