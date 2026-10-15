"""Phase 7: instance-level facts and lagged ARG dependencies."""

from auxflow.ir.graph import ARG, lower
from auxflow.ir.model import Component, DepEdge, DepType, Fact, FactKind
from auxflow.ir.serialize import from_json, to_dot, to_json

__all__ = [
    "ARG",
    "Component",
    "DepEdge",
    "DepType",
    "Fact",
    "FactKind",
    "from_json",
    "lower",
    "to_dot",
    "to_json",
]
