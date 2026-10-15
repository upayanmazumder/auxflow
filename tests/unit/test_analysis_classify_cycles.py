r"""Phase 8 (sub-issue #44): classify each non-trivial SCC."""

from __future__ import annotations

from auxflow.analysis.classify_cycles import Label, classify_components
from auxflow.analysis.scc import tarjan
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.parser.spans import Span

_SPAN = Span("synthetic.tex", 0, 1)


def _fact(fact_id: int, *, opaque: bool = False) -> Fact:
    return Fact(fact_id, FactKind.OPAQUE, None, "value", "engine", None, _SPAN, opaque=opaque)


def _arg(facts: dict[int, Fact], edges: list[tuple[int, int, DepType]]) -> ARG:
    dep_edges = [DepEdge(src, dst, 1, kind, "synthetic") for src, dst, kind in edges]
    return ARG(facts=facts, edges=dep_edges)


def test_structural_edged_cycle_is_amplifying() -> None:
    facts = {i: _fact(i) for i in range(3)}
    arg = _arg(
        facts,
        [
            (0, 1, DepType.AUX_ROUNDTRIP),
            (1, 2, DepType.LAYOUT),
            (2, 0, DepType.STRUCTURAL),
        ],
    )
    labels = classify_components(arg, tarjan(arg))
    assert labels == {0: Label.AMPLIFYING, 1: Label.AMPLIFYING, 2: Label.AMPLIFYING}


def test_opaque_member_cycle_is_unknown_cycle() -> None:
    facts = {0: _fact(0, opaque=True), 1: _fact(1)}
    arg = _arg(facts, [(0, 1, DepType.LAYOUT), (1, 0, DepType.LAYOUT)])
    labels = classify_components(arg, tarjan(arg))
    assert labels == {0: Label.UNKNOWN_CYCLE, 1: Label.UNKNOWN_CYCLE}


def test_pure_aux_roundtrip_and_layout_cycle_is_benign() -> None:
    facts = {0: _fact(0), 1: _fact(1)}
    arg = _arg(facts, [(0, 1, DepType.AUX_ROUNDTRIP), (1, 0, DepType.LAYOUT)])
    labels = classify_components(arg, tarjan(arg))
    assert labels == {0: Label.BENIGN, 1: Label.BENIGN}


def test_self_loop_is_classified_as_a_non_trivial_single_member_component() -> None:
    facts = {0: _fact(0)}
    arg = _arg(facts, [(0, 0, DepType.STRUCTURAL)])
    labels = classify_components(arg, tarjan(arg))
    assert labels == {0: Label.AMPLIFYING}


def test_acyclic_singleton_with_no_self_loop_is_not_classified() -> None:
    facts = {0: _fact(0), 1: _fact(1)}
    arg = _arg(facts, [(0, 1, DepType.LAYOUT)])
    labels = classify_components(arg, tarjan(arg))
    assert labels == {}


def test_structural_edge_takes_precedence_over_opacity() -> None:
    # A cycle with both an opaque member and a STRUCTURAL edge must be
    # AMPLIFYING, not UNKNOWN_CYCLE: per the spec's if/elif/else order.
    facts = {0: _fact(0, opaque=True), 1: _fact(1)}
    arg = _arg(facts, [(0, 1, DepType.STRUCTURAL), (1, 0, DepType.LAYOUT)])
    labels = classify_components(arg, tarjan(arg))
    assert labels == {0: Label.AMPLIFYING, 1: Label.AMPLIFYING}


def test_multiple_independent_cycles_are_classified_separately() -> None:
    facts = {i: _fact(i, opaque=(i == 2)) for i in range(4)}
    arg = _arg(
        facts,
        [
            (0, 1, DepType.STRUCTURAL),
            (1, 0, DepType.LAYOUT),  # cycle A: amplifying
            (2, 3, DepType.LAYOUT),
            (3, 2, DepType.LAYOUT),  # cycle B: opaque member 2 -> unknown
        ],
    )
    labels = classify_components(arg, tarjan(arg))
    assert labels == {
        0: Label.AMPLIFYING,
        1: Label.AMPLIFYING,
        2: Label.UNKNOWN_CYCLE,
        3: Label.UNKNOWN_CYCLE,
    }
