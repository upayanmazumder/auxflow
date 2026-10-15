#!/usr/bin/env python3
"""Deterministic validator and scorer for the AuxFlow implementation plan.

The plan artifact (``implementation-plan.yaml``) is the machine-readable form of
the GitHub hierarchy to post: a project, milestones, phase issues, and
sub-issues. This script scores that artifact against ground truth taken from
``docs/IMPLEMENTATION-PLAN.md`` and ``docs/SCOPE.md``.

The score is a single defect total. Each missing, wrong, or thin field adds
defect points. A faithful, complete plan drives the total toward zero. The
computation is pure: no network, no clock, no randomness. Running it twice on
the same input yields the same numbers.

Output (stdout):
    METRIC plan_defects=<float>
    METRIC phase_coverage_pct=<float>
    METRIC dependency_accuracy_pct=<float>
    METRIC subissue_count=<int>
    METRIC scope_coverage_pct=<float>
    METRIC quality_score=<float>

Exit code 0 when the artifact parses and scores. Non-zero only on a hard
failure (missing file, invalid YAML, malformed top-level shape).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

# --------------------------------------------------------------------------
# Ground truth. Transcribed verbatim from docs/IMPLEMENTATION-PLAN.md table and
# docs/SCOPE.md. The phase id, name fragment, hours, depends-on set, and risk
# are the authoritative facts a faithful GitHub plan must reproduce.
# --------------------------------------------------------------------------

# phase id -> (name fragment that must appear in the issue title, hours,
#              frozenset of prerequisite phase ids, risk label)
PHASES: dict[int, tuple[str, int, frozenset[int], str]] = {
    1: ("Project and tooling setup", 6, frozenset(), "LOW"),
    2: ("Lexer", 14, frozenset({1}), "LOW"),
    3: ("Parser", 22, frozenset({2}), "HIGH"),
    4: ("AST and inclusion resolution", 12, frozenset({3}), "MED"),
    5: ("Symbol tables", 12, frozenset({4}), "LOW"),
    6: ("Semantic analysis", 10, frozenset({5}), "LOW"),
    7: ("IR generation", 14, frozenset({6}), "MED"),
    8: ("SCC analysis", 6, frozenset({7}), "LOW"),
    9: ("Taint analysis", 8, frozenset({8}), "MED"),
    10: ("Stable-pass fixpoint", 8, frozenset({8}), "LOW"),
    11: ("Classification and diagnostics", 10, frozenset({9, 10}), "MED"),
    12: ("Build planner", 10, frozenset({11}), "MED"),
    13: ("Runtime verification", 12, frozenset({12}), "MED"),
    14: ("Benchmark harness", 14, frozenset({13}), "MED"),
    15: ("Evaluation", 12, frozenset({14}), "MED"),
    16: ("Documentation and report", 12, frozenset({15}), "LOW"),
}

VALID_RISKS = {"LOW", "MED", "HIGH"}

# Minimum structure a credible GitHub rollout needs.
MIN_MILESTONES = 6
REQUIRED_PROJECT_FIELDS = {"Status", "Phase", "Risk", "Estimate"}
MIN_SUBISSUES_PER_PHASE = 3
MIN_BODY_CHARS = 80
# Each sub-issue must carry enough detail for an implementation subagent to act
# without reading anything else: an acceptance-criteria body of real length.
MIN_SUBISSUE_BODY_CHARS = 60

# MUST BUILD items 1..16 from docs/SCOPE.md: a keyword that, if present somewhere
# in the plan's issue/sub-issue text, counts the scope item as covered.
SCOPE_KEYWORDS: dict[int, tuple[str, ...]] = {
    1: ("category-code", "lexer", "tokens"),
    2: ("recursive-descent", "parser", "argument-signature"),
    3: ("ast", "inclusion graph", "cycle detection"),
    4: ("symbol table",),
    5: ("semantic", "diagnostic", "check"),
    6: ("auxiliary reference graph", "exists/value", "arg", "graph"),
    7: ("taint", "structural edge"),
    8: ("tarjan", "scc"),
    9: ("stable-pass", "fixpoint", "condensation"),
    10: ("classifier", "classify", "four-state"),
    11: ("build-plan", "build planner", "safety invariant", "plan --explain"),
    12: ("executor", "auxiliary-state", "run"),
    13: ("corpus", "expectations"),
    14: ("harness", "baseline", "ground-truth"),
    15: ("mechanism-coverage", "coverage table"),
    16: ("oracle-comparison", "oracle"),
}

# Authoritative totals and gating facts (docs/IMPLEMENTATION-PLAN.md).
# The per-phase hours sum to this; a plan that mis-sums has a transcription bug.
TOTAL_HOURS = sum(hours for _, hours, _, _ in PHASES.values())  # 182

# Named checkpoints and decision gates. A credible rollout surfaces each one as
# a milestone or a labelled issue so the two go/no-go decisions are visible.
CHECKPOINTS: tuple[str, ...] = ("CP1", "CP2", "CP3", "CP4", "CP5", "CP6")
GATES: tuple[str, ...] = ("Gate 1", "Gate 2")

# Exact CLI subcommand each phase must deliver (docs/IMPLEMENTATION-PLAN.md
# deliverables, docs/SCOPE.md MUST-BUILD). A faithful issue names its command.
CLI_SUBCOMMANDS: dict[int, str] = {
    2: "auxflow tokens",
    4: "auxflow ast",
    5: "auxflow symbols",
    6: "auxflow check",
    7: "auxflow graph",
    11: "auxflow classify",
    12: "auxflow plan",
    13: "auxflow run",
}

# The eight rows of the docs/IMPLEMENTATION-PLAN.md risk register. A faithful
# rollout carries each one so its mitigation is tracked, not lost. Each tuple is
# a set of keywords; one hit in the plan's risk_register counts the row covered.
RISK_REGISTER: tuple[tuple[str, ...], ...] = (
    ("parser scope creep", "scope creep"),
    ("tarjan", "stack overflow", "recursion"),
    ("arg collapsing", "fixed lattice", "instance-level"),
    ("benign-cycle", "benign cycle", "d7"),
    ("ground-truth criterion", "ground truth", "pdf byte", "d6"),
    ("evaluation squeezed", "evaluation", "two-week margin", "week 8"),
    ("infrastructure", "displacing"),
    ("assumption a2", "a2", "prediction miss"),
)

# The seven-step cut order from docs/SCOPE.md. A 5-day solo plan must state what
# it drops first; each prefix removal leaves a coherent project. One keyword hit
# in the plan's `deferred` section counts the step represented.
CUT_ORDER: tuple[tuple[str, ...], ...] = (
    ("event-driven worker", "worker scaling"),
    ("distributed execution", "scheduling metadata"),
    ("index", "long-table"),
    ("incremental invalidation", "includeonly"),
    ("dead-file", "dead file"),
    ("per-fact stability", "stability report"),
    ("explained-plan", "explain detail", "plan dump"),
)


class HardError(Exception):
    """Unrecoverable problem: the artifact cannot be scored at all."""


def load_plan(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise HardError(f"plan artifact not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise HardError(f"plan artifact is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise HardError("plan artifact top level must be a mapping")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def text_of(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def detect_cycle(adj: dict[int, set[int]]) -> bool:
    """Return True if the dependency graph has a cycle. Iterative DFS."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = dict.fromkeys(adj, WHITE)
    for start in adj:
        if color[start] != WHITE:
            continue
        stack: list[tuple[int, bool]] = [(start, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                color[node] = BLACK
                continue
            if color[node] == GREY:
                continue
            color[node] = GREY
            stack.append((node, True))
            for nxt in adj.get(node, set()):
                if nxt not in color:
                    continue
                if color[nxt] == GREY:
                    return True
                if color[nxt] == WHITE:
                    stack.append((nxt, False))
    return False


def score(plan: dict[str, Any]) -> dict[str, float]:
    defects = 0.0

    project = plan.get("project") if isinstance(plan.get("project"), dict) else {}
    milestones = as_list(plan.get("milestones"))
    issues = as_list(plan.get("issues"))

    # --- top-level presence -------------------------------------------------
    if not project:
        defects += 10
    if not milestones:
        defects += 10
    if not issues:
        defects += 10

    # --- index the phase issues --------------------------------------------
    milestone_keys = {
        text_of(m.get("key")) or text_of(m.get("title"))
        for m in milestones
        if isinstance(m, dict)
    }
    milestone_keys.discard("")

    by_phase: dict[int, dict[str, Any]] = {}
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        phase_id = issue.get("phase")
        if isinstance(phase_id, int) and phase_id in PHASES:
            by_phase.setdefault(phase_id, issue)

    covered_phases = 0
    dep_checked = 0
    dep_correct = 0
    subissue_count = 0
    cli_covered = 0
    acceptance_covered = 0

    for pid, (name_frag, hours, deps, risk) in PHASES.items():
        issue = by_phase.get(pid)
        if issue is None:
            defects += 8  # whole phase missing
            continue
        covered_phases += 1

        title = text_of(issue.get("title"))
        if name_frag.lower() not in title.lower():
            defects += 2

        if issue.get("hours") != hours:
            defects += 1

        if text_of(issue.get("risk")).upper() != risk:
            defects += 1

        # dependency set must match the authoritative DAG exactly
        got_deps = {d for d in as_list(issue.get("depends_on")) if isinstance(d, int)}
        dep_checked += 1
        if got_deps == set(deps):
            dep_correct += 1
        else:
            defects += 3

        if text_of(issue.get("milestone")) not in milestone_keys:
            defects += 2

        if not [lbl for lbl in as_list(issue.get("labels")) if text_of(lbl)]:
            defects += 1

        if len(text_of(issue.get("body"))) < MIN_BODY_CHARS:
            defects += 2

        subs = [s for s in as_list(issue.get("sub_issues")) if isinstance(s, dict)]
        good_subs = [s for s in subs if text_of(s.get("title"))]
        subissue_count += len(good_subs)
        if len(good_subs) < MIN_SUBISSUES_PER_PHASE:
            defects += 2 * (MIN_SUBISSUES_PER_PHASE - len(good_subs))
        # Each named sub-issue must carry acceptance-level detail so an
        # implementation subagent can execute it in isolation.
        for sub in good_subs:
            if len(text_of(sub.get("body"))) < MIN_SUBISSUE_BODY_CHARS:
                defects += 1
            if not [lbl for lbl in as_list(sub.get("labels")) if text_of(lbl)]:
                defects += 0.5

        # Phase text blob: body plus every sub-issue title and body.
        phase_blob = "\n".join(
            [text_of(issue.get("body"))]
            + [text_of(s.get("title")) + " " + text_of(s.get("body")) for s in good_subs]
        ).lower()

        # Executable issues state acceptance criteria explicitly.
        if "accept" in text_of(issue.get("body")).lower():
            acceptance_covered += 1
        else:
            defects += 1

        # The phase must name the exact CLI subcommand it ships, where one exists.
        wanted_cli = CLI_SUBCOMMANDS.get(pid)
        if wanted_cli is not None:
            if wanted_cli in phase_blob:
                cli_covered += 1
            else:
                defects += 1

    # --- milestones ---------------------------------------------------------
    good_milestones = [
        m
        for m in milestones
        if isinstance(m, dict) and text_of(m.get("title"))
    ]
    if len(good_milestones) < MIN_MILESTONES:
        defects += 2 * (MIN_MILESTONES - len(good_milestones))
    for m in good_milestones:
        if not text_of(m.get("description")):
            defects += 1
        if not [p for p in as_list(m.get("phases")) if isinstance(p, int)]:
            defects += 1

    # --- schedule coverage: every phase scheduled exactly once --------------
    phase_assignment: dict[int, int] = {}
    for m in good_milestones:
        for p in as_list(m.get("phases")):
            if isinstance(p, int) and p in PHASES:
                phase_assignment[p] = phase_assignment.get(p, 0) + 1
    for pid in PHASES:
        count = phase_assignment.get(pid, 0)
        if count == 0:
            defects += 2  # phase never placed on the calendar
        elif count > 1:
            defects += 1 * (count - 1)  # phase double-booked across milestones

    # --- checkpoints and decision gates must be visible ---------------------
    milestone_blob = "\n".join(
        text_of(m.get("title")) + "\n" + text_of(m.get("description"))
        for m in good_milestones
    )
    plan_blob = (
        milestone_blob
        + "\n"
        + "\n".join(
            text_of(i.get("title")) + "\n" + text_of(i.get("body"))
            for i in issues
            if isinstance(i, dict)
        )
    ).lower()
    for marker in (*CHECKPOINTS, *GATES):
        if marker.lower() not in plan_blob:
            defects += 1

    # --- total-effort anchor: the per-phase hours must sum to the doc total --
    if covered_phases == len(PHASES):
        plan_hours = sum(
            issue["hours"]
            for issue in by_phase.values()
            if isinstance(issue.get("hours"), int)
        )
        if plan_hours != TOTAL_HOURS:
            defects += 3

    # --- risk register: the eight documented risks must be carried -----------
    register = as_list(plan.get("risk_register"))
    register_blob = "\n".join(
        " ".join(
            text_of(entry.get(k))
            for k in ("risk", "likelihood", "impact", "mitigation")
        )
        for entry in register
        if isinstance(entry, dict)
    ).lower()
    risk_covered = 0
    for keywords in RISK_REGISTER:
        if any(kw in register_blob for kw in keywords):
            risk_covered += 1
        else:
            defects += 1
    # Every carried entry needs a mitigation, else it is a label not a plan.
    for entry in register:
        if isinstance(entry, dict) and not text_of(entry.get("mitigation")):
            defects += 0.5

    # --- deferred scope and cut order (5-day reality) -----------------------
    deferred = plan.get("deferred") if isinstance(plan.get("deferred"), dict) else {}
    deferred_blob = yaml.safe_dump(deferred, allow_unicode=True).lower()
    cut_covered = 0
    for keywords in CUT_ORDER:
        if any(kw in deferred_blob for kw in keywords):
            cut_covered += 1
        else:
            defects += 1
    if not [x for x in as_list(deferred.get("should")) if text_of(x)]:
        defects += 2  # SHOULD-BUILD items (17-22) not represented
    if not [x for x in as_list(deferred.get("stretch")) if text_of(x)]:
        defects += 2  # STRETCH items (23-28) not represented

    # --- dependency graph integrity ----------------------------------------
    adj: dict[int, set[int]] = {}
    for pid, issue in by_phase.items():
        got = {d for d in as_list(issue.get("depends_on")) if isinstance(d, int)}
        for d in got:
            if d not in PHASES:
                defects += 3  # dangling dependency
        adj[pid] = {d for d in got if d in PHASES}
    if detect_cycle(adj):
        defects += 10

    # --- project shape ------------------------------------------------------
    fields = {text_of(f) for f in as_list(project.get("fields"))}
    for required in REQUIRED_PROJECT_FIELDS:
        if required not in fields:
            defects += 1
    if not [v for v in as_list(project.get("views")) if text_of(v)]:
        defects += 1

    # --- scope coverage -----------------------------------------------------
    haystack_parts: list[str] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        haystack_parts.append(text_of(issue.get("title")))
        haystack_parts.append(text_of(issue.get("body")))
        for s in as_list(issue.get("sub_issues")):
            if isinstance(s, dict):
                haystack_parts.append(text_of(s.get("title")))
                haystack_parts.append(text_of(s.get("body")))
    haystack = "\n".join(haystack_parts).lower()
    scope_hits = 0
    for keywords in SCOPE_KEYWORDS.values():
        if any(kw in haystack for kw in keywords):
            scope_hits += 1
        else:
            defects += 0.5
    scope_coverage_pct = 100.0 * scope_hits / len(SCOPE_KEYWORDS)

    phase_coverage_pct = 100.0 * covered_phases / len(PHASES)
    dependency_accuracy_pct = 100.0 * dep_correct / dep_checked if dep_checked else 0.0
    cli_coverage_pct = 100.0 * cli_covered / len(CLI_SUBCOMMANDS)
    acceptance_coverage_pct = 100.0 * acceptance_covered / len(PHASES)
    risk_coverage_pct = 100.0 * risk_covered / len(RISK_REGISTER)
    cut_order_coverage_pct = 100.0 * cut_covered / len(CUT_ORDER)
    quality_score = max(0.0, 100.0 - defects)

    return {
        "plan_defects": round(defects, 3),
        "phase_coverage_pct": round(phase_coverage_pct, 2),
        "dependency_accuracy_pct": round(dependency_accuracy_pct, 2),
        "subissue_count": float(subissue_count),
        "scope_coverage_pct": round(scope_coverage_pct, 2),
        "cli_coverage_pct": round(cli_coverage_pct, 2),
        "acceptance_coverage_pct": round(acceptance_coverage_pct, 2),
        "risk_coverage_pct": round(risk_coverage_pct, 2),
        "cut_order_coverage_pct": round(cut_order_coverage_pct, 2),
        "quality_score": round(quality_score, 3),
    }


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    plan_path = Path(argv[1]) if len(argv) > 1 else here / "implementation-plan.yaml"
    try:
        plan = load_plan(plan_path)
        metrics = score(plan)
    except HardError as exc:
        print(f"validate_plan: {exc}", file=sys.stderr)
        return 1

    for name in (
        "plan_defects",
        "phase_coverage_pct",
        "dependency_accuracy_pct",
        "subissue_count",
        "scope_coverage_pct",
        "cli_coverage_pct",
        "acceptance_coverage_pct",
        "risk_coverage_pct",
        "cut_order_coverage_pct",
        "quality_score",
    ):
        value = metrics[name]
        if name == "subissue_count":
            print(f"METRIC {name}={int(value)}")
        else:
            print(f"METRIC {name}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
