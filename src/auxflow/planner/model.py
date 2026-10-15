"""The JSON-compatible contract between analysis and execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from auxflow.parser.diagnostics import Diagnostic
from auxflow.planner import Classification


@dataclass(frozen=True)
class Step:
    tool: str
    args: list[str]
    jobname: str
    reason: str
    verify_after: bool

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError("every plan step requires a reason")


@dataclass(frozen=True)
class BuildPlan:
    classification: Classification
    predicted_runs: int | None
    steps: list[Step]
    max_runs: int
    stop_condition: Literal["planned_count", "aux_fixpoint", "cap"]
    diagnostics: list[Diagnostic]
    arg_stats: dict[str, int | float]
    model_version: str
