r"""Phase 9 (sub-issue #46): the monotonic taint worklist loop."""

from __future__ import annotations

from auxflow.analysis.taint import propagate_taint
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.parser.spans import Span

_SPAN = Span("synthetic.tex", 0, 1)


def _fact(fact_id: int, component: str = "value") -> Fact:
    return Fact(fact_id, FactKind.OPAQUE, None, component, "engine", None, _SPAN)


def _arg(facts: dict[int, Fact], edges: list[tuple[int, int]]) -> ARG:
    dep_edges = [DepEdge(src, dst, 1, DepType.LAYOUT, "synthetic") for src, dst in edges]
    return ARG(facts=facts, edges=dep_edges)


def test_taint_propagates_forward_along_value_edges_only() -> None:
    facts = {
        0: _fact(0),
        1: _fact(1),
        2: _fact(2, component="exists"),  # not a value component: not reachable by taint
        3: _fact(3),
    }
    arg = _arg(facts, [(0, 1), (1, 2), (1, 3)])

    taint, push_count = propagate_taint(arg, {0})

    assert taint == {0, 1, 3}
    assert 2 not in taint  # 2 has component "exists", excluded by the g.component == "value" guard
    assert push_count == len(taint)


def test_each_fact_is_pushed_at_most_once_even_with_multiple_paths() -> None:
    # 0 -> 1, 0 -> 2, 1 -> 3, 2 -> 3: fact 3 is reachable via two paths.
    facts = {i: _fact(i) for i in range(4)}
    arg = _arg(facts, [(0, 1), (0, 2), (1, 3), (2, 3)])

    taint, push_count = propagate_taint(arg, {0})

    assert taint == {0, 1, 2, 3}
    assert push_count == 4  # fact 3 pushed once despite two incoming edges
    assert push_count <= len(arg.facts)


def test_taint_grows_monotonically_as_seeds_are_added() -> None:
    facts = {i: _fact(i) for i in range(3)}
    arg = _arg(facts, [(0, 1), (1, 2)])

    small_taint, _ = propagate_taint(arg, {0})
    large_taint, _ = propagate_taint(arg, {0, 2})

    assert small_taint <= large_taint


def test_cyclic_value_edge_graph_terminates_without_looping_forever() -> None:
    # 0 -> 1 -> 2 -> 0: a pure cycle among value-component facts.
    facts = {i: _fact(i) for i in range(3)}
    arg = _arg(facts, [(0, 1), (1, 2), (2, 0)])

    taint, push_count = propagate_taint(arg, {0})

    assert taint == {0, 1, 2}
    assert push_count == 3  # each fact pushed exactly once despite the cycle


def test_empty_seed_set_propagates_nothing() -> None:
    facts = {i: _fact(i) for i in range(2)}
    arg = _arg(facts, [(0, 1)])

    taint, push_count = propagate_taint(arg, set())

    assert taint == set()
    assert push_count == 0
