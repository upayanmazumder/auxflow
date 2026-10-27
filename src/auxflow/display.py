"""Human-facing source locations shared by the CLI and the diagnostic reports.

Spans store character offsets. People read `path:line:col`, and paths under the
current directory read better when relative. Machine-readable output (plans, ARG
JSON, DOT) keeps absolute paths and offsets and never goes through this module.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from auxflow.parser.spans import Span


def offset_to_line_col(text: str, offset: int) -> tuple[int, int]:
    """1-indexed `(line, col)` of character `offset` in `text`, matching the
    lexer's own `Token.line`/`Token.col` convention."""
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    return line, offset - line_start + 1


def display_path(file_id: str) -> str:
    """`file_id` relative to the current directory, or unchanged when it is outside it."""
    try:
        relative = os.path.relpath(file_id)
    except ValueError:  # a different drive on Windows
        return file_id
    if relative == ".." or relative.startswith(f"..{os.sep}"):
        return file_id
    return relative


class Locator:
    """Turn spans into `path:line:col`, reading each source file at most once."""

    def __init__(self, sources: Mapping[str, str] | None = None) -> None:
        self._sources = dict(sources or {})

    def _text(self, file_id: str) -> str:
        if file_id not in self._sources:
            try:
                self._sources[file_id] = Path(file_id).read_text(encoding="utf-8")
            except OSError:
                self._sources[file_id] = ""
        return self._sources[file_id]

    def line_col(self, span: Span) -> tuple[int, int]:
        return offset_to_line_col(self._text(span.file_id), span.start)

    def at(self, span: Span) -> str:
        line, col = self.line_col(span)
        return f"{display_path(span.file_id)}:{line}:{col}"
