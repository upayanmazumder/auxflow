"""Phase 7: instance-level facts and lagged ARG dependencies."""

from auxflow.ir.graph import ARG, lower
from auxflow.ir.model import Component, DepEdge, DepType, Fact, FactKind

__all__ = ["ARG", "Component", "DepEdge", "DepType", "Fact", "FactKind", "lower"]
