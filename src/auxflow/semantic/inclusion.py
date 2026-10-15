r"""File dependency diagnostics from the inclusion graph and AST forest."""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import Forest, walk
from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.nodes import MacroCall, Text

_GRAPHICS_SUFFIXES = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


def _graphics_name(call: MacroCall) -> str | None:
    arguments = [arg for arg in call.args if arg.kind == "mandatory"]
    if not arguments:
        return None
    content = arguments[-1].content
    if not content or not all(isinstance(node, Text) for node in content):
        return None
    return "".join(node.text for node in content if isinstance(node, Text))


def _graphics_exists(source: str, name: str) -> bool:
    path = Path(source).parent / name
    if path.is_file():
        return True
    return not path.suffix and any(path.with_suffix(ext).is_file() for ext in _GRAPHICS_SUFFIXES)


def check_inclusions(forest: Forest) -> list[Diagnostic]:
    """Check file existence and report the source edge that closes each cycle."""
    diagnostics: list[Diagnostic] = []
    for edge in forest.edges:
        if not Path(edge.target).is_file():
            diagnostics.append(Diagnostic(edge.span, f"unresolvable inclusion: {edge.target}"))
    for file_id, document in forest.documents.items():
        for node in walk(document):
            if isinstance(node, MacroCall) and node.name == "\\includegraphics":
                name = _graphics_name(node)
                if name and not _graphics_exists(file_id, name):
                    diagnostics.append(Diagnostic(node.span, f"missing graphics file: {name}"))
    for cycle in forest.cycles:
        source, target = cycle[-1], cycle[0]
        closing = next(
            edge for edge in forest.edges if edge.source == source and edge.target == target
        )
        diagnostics.append(
            Diagnostic(closing.span, f"inclusion cycle: {' -> '.join((*cycle, target))}")
        )
    return diagnostics
