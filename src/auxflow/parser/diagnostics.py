"""`Diagnostic`: a structured, span-attributed error or warning record.

docs/ARCHITECTURE.md's data contracts table: "Diagnostic | semantic, analysis
| report | structured record with Span". Phase 3 needs the minimal shape --
span plus message -- to report parse errors without raising
(docs/IMPLEMENTATION-PLAN.md phase 3: "Recovery on malformed input is
required"). Later phases may extend this; they must not narrow it.
"""

from __future__ import annotations

from dataclasses import dataclass

from auxflow.parser.spans import Span


@dataclass(frozen=True)
class Diagnostic:
    span: Span
    message: str
