"""JSON serialisation for the compiler-to-executor BuildPlan contract."""

from __future__ import annotations

import json
from dataclasses import asdict

from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.spans import Span
from auxflow.planner.model import BuildPlan, Step


def to_json(plan: BuildPlan) -> str:
    """Serialize a plan with its step reasons and diagnostic source spans."""
    return json.dumps(asdict(plan), indent=2, sort_keys=True)


def from_json(text: str) -> BuildPlan:
    """Restore a plan without rerunning static analysis."""
    payload = json.loads(text)
    diagnostics = [
        Diagnostic(Span(**entry["span"]), entry["message"], entry["severity"])
        for entry in payload["diagnostics"]
    ]
    return BuildPlan(
        classification=payload["classification"],
        predicted_runs=payload["predicted_runs"],
        steps=[Step(**entry) for entry in payload["steps"]],
        max_runs=payload["max_runs"],
        stop_condition=payload["stop_condition"],
        diagnostics=diagnostics,
        arg_stats=payload["arg_stats"],
        model_version=payload["model_version"],
    )
