r"""Phase 8 (sub-issue #42): iterative Tarjan SCC over the ARG.

docs/STATIC-ANALYSIS.md section 3: output in reverse topological order --
for an edge `u -> v`, `v`'s component is emitted before `u`'s.
"""

from __future__ import annotations

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


def test_dag_with_no_cycles_yields_one_singleton_component_per_node() -> None:
    # 0 -> 1 -> 2, a pure chain: three trivial, singleton components.
    arg = _arg(range(3), [(0, 1), (1, 2)])
    components = tarjan(arg)
    assert sorted(components) == [(0,), (1,), (2,)]
    # reverse topological order: for edge u->v, v's component before u's.
    index = {c[0]: i for i, c in enumerate(components)}
    assert index[2] < index[1] < index[0]


def test_two_node_cycle_is_returned_as_one_component() -> None:
    arg = _arg(range(2), [(0, 1), (1, 0)])
    components = tarjan(arg)
    assert len(components) == 1
    assert set(components[0]) == {0, 1}


def test_self_loop_is_a_non_trivial_single_member_component() -> None:
    arg = _arg(range(1), [(0, 0)])
    components = tarjan(arg)
    assert components == [(0,)]


def test_bridge_between_two_cycles_preserves_reverse_topological_order() -> None:
    # cycle A: {0,1}; bridge 1 -> 2; cycle B: {2,3}.
    arg = _arg(range(4), [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2)])
    components = tarjan(arg)
    member_of = {member: frozenset(c) for c in components for member in c}
    assert member_of[0] == member_of[1] == frozenset({0, 1})
    assert member_of[2] == member_of[3] == frozenset({2, 3})
    index = {frozenset(c): i for i, c in enumerate(components)}
    # edge 1 -> 2 crosses components: {2,3}'s component must be emitted first.
    assert index[frozenset({2, 3})] < index[frozenset({0, 1})]


def test_disconnected_components_are_all_returned() -> None:
    arg = _arg(range(4), [(0, 1), (1, 0), (2, 3)])
    components = tarjan(arg)
    actual = sorted(tuple(sorted(c)) for c in components)
    expected = sorted(tuple(sorted(s)) for s in ({0, 1}, {2}, {3}))
    assert actual == expected


def test_known_three_cycle_plus_tail_partition() -> None:
    # 0 -> 1 -> 2 -> 0 (a 3-cycle), plus 2 -> 3 (tail, trivial component).
    arg = _arg(range(4), [(0, 1), (1, 2), (2, 0), (2, 3)])
    components = tarjan(arg)
    actual = sorted(tuple(sorted(c)) for c in components)
    expected = sorted(tuple(sorted(s)) for s in ({0, 1, 2}, {3}))
    assert actual == expected
    index = {frozenset(c): i for i, c in enumerate(components)}
    assert index[frozenset({3})] < index[frozenset({0, 1, 2})]


def test_long_chain_completes_without_recursion_error() -> None:
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    arg = _arg(range(n), edges)
    components = tarjan(arg)  # would raise RecursionError if implemented recursively
    assert len(components) == n
    assert all(len(c) == 1 for c in components)
    index = {c[0]: i for i, c in enumerate(components)}
    # reverse topological: later nodes in the chain emitted first.
    for i in range(n - 1):
        assert index[i + 1] < index[i]
