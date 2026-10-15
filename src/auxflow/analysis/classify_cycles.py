r"""Per-component cycle classification. docs/STATIC-ANALYSIS.md section 3.

Only non-trivial components are classified: `|C| > 1`, or `|C| == 1` with a
self-loop (an edge whose source and destination are the same fact). A
trivial singleton with no self-loop is acyclic and gets no label.
"""

from __future__ import annotations

from enum import Enum, auto

from auxflow.ir.graph import ARG
from auxflow.ir.model import DepType


class Label(Enum):
    AMPLIFYING = auto()
    UNKNOWN_CYCLE = auto()
    BENIGN = auto()


def classify_components(arg: ARG, components: list[tuple[int, ...]]) -> dict[int, Label]:
    """Fact id -> Label, for every fact in a non-trivial component.

    A fact in a trivial (acyclic, non-self-looping) singleton component has
    no entry. O(V + E): one pass bucketing each edge by its endpoints'
    shared component (if any), then one pass per component over its own
    bucketed edges and members.
    """
    component_of: dict[int, int] = {
        fact_id: index for index, component in enumerate(components) for fact_id in component
    }
    internal_edges: dict[int, list[DepType]] = {}
    for edge in arg.edges:
        source_component = component_of[edge.source]
        if source_component == component_of[edge.destination]:
            internal_edges.setdefault(source_component, []).append(edge.dependency_type)

    labels: dict[int, Label] = {}
    for index, component in enumerate(components):
        edge_types = internal_edges.get(index, [])
        if len(component) <= 1 and not edge_types:
            continue  # a trivial singleton with no self-loop is acyclic

        if DepType.STRUCTURAL in edge_types:
            label = Label.AMPLIFYING
        elif any(arg.facts[member].opaque for member in component):
            label = Label.UNKNOWN_CYCLE
        else:
            label = Label.BENIGN

        for member in component:
            labels[member] = label

    return labels
