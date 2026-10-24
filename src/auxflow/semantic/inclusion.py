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


def _graphics_exists(directories: tuple[Path, ...], name: str) -> bool:
    for directory in directories:
        path = directory / name
        if path.is_file():
            return True
        if not path.suffix and any(path.with_suffix(ext).is_file() for ext in _GRAPHICS_SUFFIXES):
            return True
    return False


def _graphics_directories(source: str, parents: dict[str, list[str]]) -> tuple[Path, ...]:
    """Search the entry document's directory, then the including file's directory."""
    roots: list[Path] = []
    seen = {source}
    pending = [source]
    while pending:
        file_id = pending.pop()
        includers = parents.get(file_id, ())
        if not includers:
            roots.append(Path(file_id).parent)
        for parent in includers:
            if parent not in seen:
                seen.add(parent)
                pending.append(parent)
    return tuple(dict.fromkeys((*roots, Path(source).parent)))


def check_inclusions(forest: Forest) -> list[Diagnostic]:
    """Check file existence and report the source edge that closes each cycle."""
    diagnostics: list[Diagnostic] = []
    parents: dict[str, list[str]] = {}
    for edge in forest.edges:
        parents.setdefault(edge.target, []).append(edge.source)
    for edge in forest.edges:
        if not Path(edge.target).is_file():
            diagnostics.append(Diagnostic(edge.span, f"unresolvable inclusion: {edge.target}"))
    for file_id, document in forest.documents.items():
        directories = _graphics_directories(file_id, parents)
        for node in walk(document):
            if isinstance(node, MacroCall) and node.name == "\\includegraphics":
                name = _graphics_name(node)
                if name and not _graphics_exists(directories, name):
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
