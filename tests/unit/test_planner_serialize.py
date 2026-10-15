"""BuildPlan serialization preserves the documented plan and diagnostics."""

from __future__ import annotations

import json

import pytest

from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.spans import Span
from auxflow.planner.model import BuildPlan, Step
from auxflow.planner.serialize import from_json, to_json


def test_documented_certified_plan_serializes_and_round_trips() -> None:
    steps = [
        Step("pdflatex", [], "main", "run 1: emit LABEL_*, TOC_ENTRY, CITE_USE facts", False),
        Step("bibtex", [], "main", r"12 CITE_USE facts and \bibliography at main.tex:214", False),
        Step("pdflatex", [], "main", "run 2: BBL.exists (stable_pass 1) consumed", False),
        Step(
            "pdflatex",
            [],
            "main",
            "run 3: LIST_EXTENT(toc) (stable_pass 3) after the bibliography entry was added",
            False,
        ),
        Step(
            "pdflatex",
            [],
            "main",
            "run 4: PAGEREF_USE consumes LABEL_PAGE; P=3 so runs=P+1",
            True,
        ),
    ]
    plan = BuildPlan(
        "CERTIFIED",
        4,
        steps,
        6,
        "planned_count",
        [],
        {"V": 148, "E": 331, "sccs": 0, "analysis_ms": 41},
        "arg-0.1",
    )

    payload = json.loads(to_json(plan))
    assert payload == {
        "classification": "CERTIFIED",
        "predicted_runs": 4,
        "max_runs": 6,
        "stop_condition": "planned_count",
        "model_version": "arg-0.1",
        "arg_stats": {"V": 148, "E": 331, "sccs": 0, "analysis_ms": 41},
        "steps": [
            {
                "tool": "pdflatex",
                "args": [],
                "jobname": "main",
                "reason": "run 1: emit LABEL_*, TOC_ENTRY, CITE_USE facts",
                "verify_after": False,
            },
            {
                "tool": "bibtex",
                "args": [],
                "jobname": "main",
                "reason": r"12 CITE_USE facts and \bibliography at main.tex:214",
                "verify_after": False,
            },
            {
                "tool": "pdflatex",
                "args": [],
                "jobname": "main",
                "reason": "run 2: BBL.exists (stable_pass 1) consumed",
                "verify_after": False,
            },
            {
                "tool": "pdflatex",
                "args": [],
                "jobname": "main",
                "reason": "run 3: LIST_EXTENT(toc) (stable_pass 3) after the "
                "bibliography entry was added",
                "verify_after": False,
            },
            {
                "tool": "pdflatex",
                "args": [],
                "jobname": "main",
                "reason": "run 4: PAGEREF_USE consumes LABEL_PAGE; P=3 so runs=P+1",
                "verify_after": True,
            },
        ],
        "diagnostics": [],
    }
    assert from_json(to_json(plan)) == plan


def test_amplifying_diagnostics_preserve_severity_and_span_after_json_round_trip() -> None:
    diagnosis = Diagnostic(Span("chapter.tex", 73, 84), "may not converge", "warning")
    plan = BuildPlan("AMPLIFYING", None, [], 6, "cap", [diagnosis], {"V": 3}, "arg-0.1")

    decoded = from_json(to_json(plan))

    assert decoded == plan
    assert json.loads(to_json(plan))["diagnostics"] == [
        {
            "span": {"file_id": "chapter.tex", "start": 73, "end": 84},
            "message": "may not converge",
            "severity": "warning",
        }
    ]


def test_step_without_a_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="requires a reason"):
        Step("pdflatex", [], "main", "", True)
