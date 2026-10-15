r"""Phase 8 (sub-issue #43): the condensation DAG in forward topological order."""

from __future__ import annotations

from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.parser.spans import Span

_SPAN = Span("synthetic.tex", 0, 1)


def _fact(fact_id: int) -> Fact:
    return Fact(fact_id, FactKind.OPAQUE, None, "value", "engine", None, _SPAN)


def _arg(fact_ids: range, edges: list[tuple[int, int]]) -> ARG:
    facts = {i: _fact(i) for i in fact_ids}
    dep_edges = [DepEdge(src, dst, 1, DepType.LAYOUT, "synthetic") for src, dst in edges]
    return ARG(facts=facts, edges=dep_edges)


def test_bridge_between_two_cycles_yields_predecessor_first_topological_order() -> None:
    # cycle A: {0,1}; bridge 1 -> 2; cycle B: {2,3}. A is the predecessor.
    arg = _arg(range(4), [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2)])
    cond = build_condensation(arg, tarjan(arg))

    assert len(cond.components) == 2
    a_index = cond.component_of[0]
    b_index = cond.component_of[2]
    assert cond.component_of[1] == a_index
    assert cond.component_of[3] == b_index
    assert a_index != b_index
    assert a_index < b_index  # predecessor (A) appears before successor (B)
    assert cond.edges == ((a_index, b_index),)


def test_no_intra_component_edges_remain_in_the_condensation() -> None:
    arg = _arg(range(4), [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2)])
    cond = build_condensation(arg, tarjan(arg))
    for source, destination in cond.edges:
        assert source != destination


def test_three_chained_components_are_in_full_topological_order() -> None:
    # A={0} -> B={1,2} -> C={3}
    arg = _arg(range(4), [(0, 1), (1, 2), (2, 1), (2, 3)])
    cond = build_condensation(arg, tarjan(arg))

    assert len(cond.components) == 3
    a, b, c = cond.component_of[0], cond.component_of[1], cond.component_of[3]
    assert cond.component_of[2] == b
    assert a < b < c
    assert set(cond.edges) == {(a, b), (b, c)}


def test_disconnected_graph_has_no_condensation_edges() -> None:
    arg = _arg(range(2), [])
    cond = build_condensation(arg, tarjan(arg))
    assert len(cond.components) == 2
    assert cond.edges == ()


def test_every_fact_is_assigned_to_exactly_one_component() -> None:
    arg = _arg(range(5), [(0, 1), (1, 0), (2, 3), (3, 4)])
    cond = build_condensation(arg, tarjan(arg))
    assert set(cond.component_of) == {0, 1, 2, 3, 4}
    assert sum(len(c) for c in cond.components) == 5
    assert len(set().union(*cond.components)) == 5
