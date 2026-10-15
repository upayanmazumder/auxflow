r"""The condensation: the DAG of strongly connected components.

docs/STATIC-ANALYSIS.md section 4 consumes this in topological order
(predecessors before successors) to compute stable_pass as a longest path.
`tarjan` emits components in reverse topological order (sinks first), so
the condensation reverses that list once -- an O(V) list reversal, not a
second graph traversal -- to produce the forward order phase 10 needs.
"""

from __future__ import annotations

from dataclasses import dataclass

from auxflow.ir.graph import ARG


@dataclass(frozen=True)
class Condensation:
    components: tuple[tuple[int, ...], ...]
    """Components in topological order: for a condensation edge `A -> B`,
    `A` (the predecessor) appears before `B`."""

    component_of: dict[int, int]
    """Fact id -> index into `components`."""

    edges: tuple[tuple[int, int], ...]
    """Deduplicated inter-component edges `(source_index, destination_index)`.
    Never contains a self-edge: an edge whose endpoints fall in the same
    component is intra-component, not part of the condensation."""


def build_condensation(arg: ARG, components: list[tuple[int, ...]]) -> Condensation:
    """Build the condensation from `tarjan`'s reverse-topological output."""
    forward_order = list(reversed(components))
    component_of: dict[int, int] = {
        fact_id: index for index, component in enumerate(forward_order) for fact_id in component
    }

    seen_edges: set[tuple[int, int]] = set()
    for edge in arg.edges:
        source = component_of[edge.source]
        destination = component_of[edge.destination]
        if source != destination:
            seen_edges.add((source, destination))

    return Condensation(
        components=tuple(forward_order),
        component_of=component_of,
        edges=tuple(sorted(seen_edges)),
    )
