"""`Span`: the mandatory source-location record on every AST node.

docs/COMPILER-PIPELINE.md section 3: "a mandatory Span(file_id, start, end)
on every node". Spans are load-bearing -- the diagnostics in
docs/NON-CONVERGENCE.md are worthless without them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    file_id: str
    start: int
    end: int
