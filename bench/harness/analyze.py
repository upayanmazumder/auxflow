"""Static-analysis entry point shared by baselines D and E.

Runs the identical pipeline `auxflow classify`/`auxflow plan` uses, via
public auxflow APIs plus auxflow.cli._load_forest (the exact multi-file
\\input/\\include loader the CLI itself uses -- re-deriving it would risk a
second, drifting implementation), so the host measures the exact same code
path a real invocation would -- not a re-derived approximation -- while
exposing every intermediate statistic (taint-set size included) that
EVALUATION.md's "Graph size" metric asks for and that BuildPlan.arg_stats
does not carry.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from auxflow.analysis.classify import Classification, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.cli import _load_forest
from auxflow.ir import ARG, lower
from auxflow.planner.lower import build_plan
from auxflow.planner.model import BuildPlan
from auxflow.semantic.resolve import declare, resolve


@dataclass(frozen=True)
class AnalysisResult:
    plan: BuildPlan
    classification: Classification
    graph_facts: int
    graph_edges: int
    scc_count: int
    taint_set_size: int
    analysis_ms: float


def analyze(path: str, *, force: bool = False) -> AnalysisResult:
    """Parse, lower, classify and plan one document; time only the analysis."""
    started = perf_counter()
    root = str(Path(path).absolute())
    forest, _parse_diagnostics = _load_forest(root)

    tables = resolve(forest, declare(forest))
    graph: ARG = lower(forest, tables)
    seeds = seed_facts(graph)
    taint, _push_count = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, build_condensation(graph, components), labels)
    classification = classify(graph, components, labels, stable_pass)

    analysis_ms = (perf_counter() - started) * 1000
    plan = build_plan(
        forest,
        root,
        graph,
        components,
        classification,
        stable_pass,
        analysis_ms=analysis_ms,
        force=force,
    )
    return AnalysisResult(
        plan=plan,
        classification=classification,
        graph_facts=len(graph.facts),
        graph_edges=len(graph.edges),
        scc_count=len(components),
        taint_set_size=len(taint),
        analysis_ms=analysis_ms,
    )
