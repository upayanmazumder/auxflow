"""Phase 7 ARG model invariants."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from auxflow.ir import DepEdge, DepType, Fact, FactKind
from auxflow.parser import Span


def test_fact_requires_non_null_source_span_and_preserves_instance_identity() -> None:
    fields = dict(
        fact_id=7,
        kind=FactKind.LABEL_PAGE,
        key="sec:intro",
        component="value",
        producer="engine",
        consumer=None,
    )
    with pytest.raises(TypeError):
        Fact(**fields)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Fact(**fields, source_location=None)  # type: ignore[arg-type]

    fact = Fact(**fields, source_location=Span("main.tex", 5, 20))  # type: ignore[arg-type]
    assert fact.fact_id == 7
    assert fact.source_location.file_id == "main.tex"
    assert fact.dependencies == ()
    assert fact.stable_pass is None
    with pytest.raises(FrozenInstanceError):
        fact.fact_id = 8  # type: ignore[misc]


def test_dependency_edge_preserves_lag_type_and_reason() -> None:
    edge = DepEdge(7, 8, 1, DepType.AUX_ROUNDTRIP, "ref reads the previous run")
    assert edge.source == 7
    assert edge.destination == 8
    assert edge.pass_lag == 1
    assert edge.dependency_type is DepType.AUX_ROUNDTRIP
    assert edge.reason == "ref reads the previous run"
