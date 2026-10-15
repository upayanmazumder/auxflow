r"""Multi-file forest assembly and the inclusion graph.

docs/LANGUAGE-SUBSET.md: `\input{f}` (no page break) and `\include{f}`
(implicit page break) build the inclusion graph. The parser (phase 3)
produces these as ordinary `MacroCall(name="\input"|"\include", args=(...))`
nodes via the argument-signature table -- it does not construct a dedicated
`Include` node, since recognising which macro names carry multi-file
semantics is this phase's responsibility, not the parser's.

Cycle detection is the standard DFS white/grey/black colouring: white
(unvisited), grey (on the current DFS path), black (fully explored). A grey
node reached again closes a cycle.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from auxflow.ast.visitor import walk
from auxflow.parser.nodes import Document, MacroCall, Text

_INCLUDE_MACROS: dict[str, str] = {"\\input": "input", "\\include": "include"}


@dataclass(frozen=True)
class InclusionEdge:
    source: str
    target: str
    kind: str  # "input" | "include"


@dataclass(frozen=True)
class Forest:
    documents: dict[str, Document]
    edges: tuple[InclusionEdge, ...]
    cycles: tuple[tuple[str, ...], ...]

    def includer_of(self, file_id: str) -> str | None:
        """The file_id of whichever document first `\\input`/`\\include`s
        `file_id`, or None if it is never included (a root)."""
        for edge in self.edges:
            if edge.target == file_id:
                return edge.source
        return None

    def reachable_from(self, file_id: str) -> frozenset[str]:
        """Every file_id transitively reachable from `file_id` via
        inclusion edges, `file_id` itself included."""
        seen = {file_id}
        stack = [file_id]
        while stack:
            current = stack.pop()
            for edge in self.edges:
                if edge.source == current and edge.target not in seen:
                    seen.add(edge.target)
                    stack.append(edge.target)
        return frozenset(seen)


def _target_of(call: MacroCall) -> str | None:
    if not call.args:
        return None
    return "".join(n.text for n in call.args[0].content if isinstance(n, Text))


def inclusion_edges(file_id: str, document: Document) -> list[InclusionEdge]:
    """Resolve each inclusion against its source file, adding .tex when absent."""
    edges: list[InclusionEdge] = []
    for node in walk(document):
        if isinstance(node, MacroCall) and node.name in _INCLUDE_MACROS:
            target = _target_of(node)
            if target:
                filename = target if Path(target).suffix else f"{target}.tex"
                resolved = os.path.normpath(os.path.join(os.path.dirname(file_id), filename))
                edges.append(
                    InclusionEdge(source=file_id, target=resolved, kind=_INCLUDE_MACROS[node.name])
                )
    return edges


def _find_edges(documents: dict[str, Document]) -> list[InclusionEdge]:
    edges: list[InclusionEdge] = []
    for file_id, document in documents.items():
        edges.extend(inclusion_edges(file_id, document))
    return edges


def _detect_cycles(file_ids: list[str], edges: list[InclusionEdge]) -> list[tuple[str, ...]]:
    white, grey, black = 0, 1, 2
    color: dict[str, int] = dict.fromkeys(file_ids, white)
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        adjacency.setdefault(edge.source, []).append(edge.target)

    cycles: list[tuple[str, ...]] = []
    path: list[str] = []

    def visit(node: str) -> None:
        color[node] = grey
        path.append(node)
        for neighbour in adjacency.get(node, ()):
            color.setdefault(neighbour, white)
            if color[neighbour] == white:
                visit(neighbour)
            elif color[neighbour] == grey:
                start = path.index(neighbour)
                cycles.append(tuple(path[start:]))
        path.pop()
        color[node] = black

    for file_id in list(file_ids):
        if color.get(file_id, white) == white:
            visit(file_id)

    return cycles


def build_forest(documents: dict[str, Document]) -> Forest:
    edges = _find_edges(documents)
    cycles = _detect_cycles(list(documents.keys()), edges)
    return Forest(documents=dict(documents), edges=tuple(edges), cycles=tuple(cycles))
