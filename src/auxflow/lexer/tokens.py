"""The lexer's output type. See docs/COMPILER-PIPELINE.md section 1."""

from __future__ import annotations

from dataclasses import dataclass

from auxflow.lexer.catcode import CatCode


@dataclass(frozen=True)
class Token:
    catcode: CatCode
    text: str
    file_id: str
    line: int
    col: int
    offset: int
