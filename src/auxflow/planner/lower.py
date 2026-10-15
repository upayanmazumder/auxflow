r"""Lower analysis results to a linear, justified build plan."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

from auxflow.analysis.classify import Classification, State
from auxflow.analysis.stable_pass import StablePass
from auxflow.ast import Forest
from auxflow.ir.graph import ARG
from auxflow.ir.model import Fact, FactKind
from auxflow.parser.diagnostics import Diagnostic
from auxflow.planner import (
    CONSERVATIVE_DEFAULT_ENGINE_RUNS,
    MAX_RUNS_UNDER_FORCE,
    assert_safety_invariant,
)
from auxflow.planner import Classification as PlanClassification
from auxflow.planner.model import BuildPlan, Step

MODEL_VERSION = "arg-0.1"


def _location(fact: Fact) -> str:
    span = fact.source_location
    return f"{span.file_id}:{span.start}-{span.end}"


def build_plan(
    forest: Forest,
    entry: str,
    graph: ARG,
    components: list[tuple[int, ...]],
    classification: Classification,
    stable_pass: StablePass,
    *,
    analysis_ms: float,
    force: bool = False,
    spellcheck: bool = False,
) -> BuildPlan:
    """Apply reachable-file, dead-tool, index, and engine-run rules in order.

    The caller supplies analysis time because the plan does not rerun analysis.
    Spell-check is optional. Its binary is not required for normal builds.
    """
    state = classification.state
    state_name = cast(PlanClassification, state.name)
    stats: dict[str, int | float] = {
        "V": len(graph.facts),
        "E": len(graph.edges),
        "sccs": len(components),
        "analysis_ms": analysis_ms,
    }
    diagnostics: list[Diagnostic] = []
    if state is State.AMPLIFYING:
        fact_id = classification.amplifying_components[0][0]
        diagnostics.append(
            Diagnostic(
                graph.facts[fact_id].source_location,
                "AMPLIFYING CYCLE -- this document may not converge.",
                severity="warning",
            )
        )
        if not force:
            return BuildPlan(
                state_name, None, [], MAX_RUNS_UNDER_FORCE, "cap", diagnostics, stats, MODEL_VERSION
            )

    jobname = Path(entry).stem
    steps: list[Step] = []
    reachable = forest.reachable_from(entry)
    # 1. Optional per-file tooling scans only files reachable from entry.
    if spellcheck:
        for file_id in sorted(reachable & forest.documents.keys()):
            steps.append(
                Step("spellcheck", [file_id], jobname, f"reachable source file {file_id}", False)
            )

    facts = [fact for fact in graph.facts.values() if fact.source_location.file_id in reachable]
    # 2. Both a citation and a bibliography are necessary for bibtex.
    citations = [fact for fact in facts if fact.kind is FactKind.CITE_USE]
    bibliography = next(
        (fact for fact in facts if fact.kind is FactKind.BBL and fact.component == "exists"), None
    )
    bibliography_step: Step | None = None
    if citations and bibliography is not None:
        bibliography_step = Step(
            "bibtex",
            [],
            jobname,
            f"{len(citations)} CITE_USE facts and \\bibliography at {_location(bibliography)}",
            False,
        )
    # 3. Index support is optional. No index facts are lowered by the current subset.
    index = next((fact for fact in facts if fact.kind is FactKind.INDEX_ENTRY), None)
    index_step: Step | None = None
    if index is not None:
        index_step = Step("makeindex", [], jobname, f"INDEX_ENTRY at {_location(index)}", False)

    # 4. Only CERTIFIED plans use the derived count. Every other executable
    # state uses the conservative engine floor, including forced AMPLIFYING.
    stop_condition: Literal["planned_count", "aux_fixpoint", "cap"]
    if state is State.CERTIFIED:
        assert classification.predicted_runs is not None
        run_count = classification.predicted_runs
        stop_condition = "planned_count"
    else:
        run_count = CONSERVATIVE_DEFAULT_ENGINE_RUNS
        stop_condition = "cap" if state is State.AMPLIFYING else "aux_fixpoint"

    for run in range(1, run_count + 1):
        if state is State.CERTIFIED and run == run_count:
            reason = f"run {run}: CERTIFIED bound P={run_count - 1} so runs=P+1"
        else:
            bound = "derived bound" if state is State.CERTIFIED else "conservative default"
            reason = f"run {run}: {state.name} {bound}"
        steps.append(Step("pdflatex", [entry], jobname, reason, run == run_count))
        if run == 1:
            if bibliography_step is not None:
                steps.append(bibliography_step)
            if index_step is not None:
                steps.append(index_step)

    assert_safety_invariant(state_name, [step.tool for step in steps])
    return BuildPlan(
        state_name,
        classification.predicted_runs,
        steps,
        max(MAX_RUNS_UNDER_FORCE, run_count),
        stop_condition,
        diagnostics,
        stats,
        MODEL_VERSION,
    )
