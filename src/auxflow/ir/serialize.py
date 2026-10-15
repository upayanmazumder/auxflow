"""ARG serialisation: JSON for tests, Graphviz DOT for inspection."""

from __future__ import annotations

import json

from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.parser.spans import Span

_COMPONENT_FILL = {"exists": "#cfe8ff", "value": "#fff3cf"}
_EDGE_COLOR = {
    DepType.AUX_ROUNDTRIP: "#1f77b4",
    DepType.TOOL: "#2ca02c",
    DepType.LAYOUT: "#7f7f7f",
    DepType.STRUCTURAL: "#d62728",
}


def _fact_payload(fact: Fact) -> dict[str, object]:
    return {
        "fact_id": fact.fact_id,
        "kind": fact.kind.name,
        "key": fact.key,
        "component": fact.component,
        "producer": fact.producer,
        "consumer": fact.consumer,
        "source_location": {
            "file_id": fact.source_location.file_id,
            "start": fact.source_location.start,
            "end": fact.source_location.end,
        },
        "stable_pass": fact.stable_pass,
        "dependencies": list(fact.dependencies),
        "opaque": fact.opaque,
        "metadata": dict(fact.metadata),
    }


def to_json(arg: ARG) -> str:
    """Canonical JSON form: facts by id, edges by (source, destination, type)."""
    payload = {
        "facts": [_fact_payload(arg.facts[fact_id]) for fact_id in sorted(arg.facts)],
        "edges": [
            {
                "source": edge.source,
                "destination": edge.destination,
                "pass_lag": edge.pass_lag,
                "dependency_type": edge.dependency_type.name,
                "reason": edge.reason,
            }
            for edge in sorted(
                arg.edges,
                key=lambda e: (
                    e.source,
                    e.destination,
                    e.dependency_type.name,
                    e.pass_lag,
                ),
            )
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def from_json(text: str) -> ARG:
    """Rebuild an ARG from `to_json` output, preserving every field."""
    payload = json.loads(text)
    facts: dict[int, Fact] = {}
    for entry in payload["facts"]:
        location = entry["source_location"]
        facts[entry["fact_id"]] = Fact(
            fact_id=entry["fact_id"],
            kind=FactKind[entry["kind"]],
            key=entry["key"],
            component=entry["component"],
            producer=entry["producer"],
            consumer=entry["consumer"],
            source_location=Span(location["file_id"], location["start"], location["end"]),
            stable_pass=entry["stable_pass"],
            dependencies=tuple(entry["dependencies"]),
            opaque=entry["opaque"],
            metadata=dict(entry["metadata"]),
        )
    edges = [
        DepEdge(
            source=entry["source"],
            destination=entry["destination"],
            pass_lag=entry["pass_lag"],
            dependency_type=DepType[entry["dependency_type"]],
            reason=entry["reason"],
        )
        for entry in payload["edges"]
    ]
    return ARG(facts=facts, edges=edges)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def to_dot(arg: ARG) -> str:
    """DOT with node fill by component and edge colour by dependency type."""
    lines = [
        "digraph arg {",
        "  rankdir=LR;",
        '  node [shape=box, style=filled, fontname="monospace"];',
    ]
    for fact_id in sorted(arg.facts):
        fact = arg.facts[fact_id]
        label = fact.kind.name
        if fact.key:
            label += f"\n{fact.key}"
        label += f"\n[{fact.component}]"
        if fact.stable_pass is not None:
            label += f"\npass {fact.stable_pass}"
        if fact.opaque:
            label += "\nOPAQUE"
        lines.append(
            f'  f{fact_id} [label="{_escape(label)}", '
            f'fillcolor="{_COMPONENT_FILL.get(fact.component, "#eeeeee")}"];'
        )
    for edge in sorted(
        arg.edges,
        key=lambda e: (e.source, e.destination, e.dependency_type.name, e.pass_lag),
    ):
        style = ", penwidth=2" if edge.dependency_type is DepType.STRUCTURAL else ""
        colour = _EDGE_COLOR[edge.dependency_type]
        lines.append(
            f"  f{edge.source} -> f{edge.destination} "
            f'[label="{edge.dependency_type.name} lag {edge.pass_lag}", '
            f'color="{colour}", fontcolor="{colour}"{style}];'
        )
    lines.append("}")
    return "\n".join(lines) + "\n"
