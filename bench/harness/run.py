#!/usr/bin/env python3
r"""Execute one (document, baseline) pair, repeated, and emit JSONL.

Usage:
    python3 bench/harness/run.py --corpus bench/corpus --baseline all \
        --reps 10 --out bench/results/2026-10-16

Baselines A, B, C, C', C'' run entirely inside the pinned container (one
`docker run` per repetition, per docs/EVALUATION.md's isolation rule) via
the shell scripts in bench/baselines/. Baseline D is static analysis alone
and never touches a container. Baseline E runs the static analysis on the
host (identical to D) and, unless the plan was refused, executes the
resulting plan inside one container via plan_incontainer.py.

One JSONL record per repetition, carrying every field EVALUATION.md's
metrics table and the "image digest, document identifier, baseline,
repetition index" requirement from bench/README.md names.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR.parent.parent / "src"))

from analyze import analyze  # noqa: E402
from container import DEFAULT_IMAGE, image_digest, run_in_container  # noqa: E402
from stage import corpus_members, stage  # noqa: E402

from auxflow.planner.serialize import to_json  # noqa: E402

BASELINE_SCRIPTS = {
    "A": "fixed.sh",
    "B": "warning.sh",
    "C": "checksum.sh",
    "C'": "inputs.sh",
    "C''": "readwrite.sh",
}
DYNAMIC_BASELINES = (*BASELINE_SCRIPTS.keys(), "E")
ALL_BASELINES = (*BASELINE_SCRIPTS.keys(), "D", "E")
MAX_RUNS = 8
# A deterministic build date so engine timestamps never vary between runs.
# docs/EVALUATION.md: "SOURCE_DATE_EPOCH and FORCE_SOURCE_DATE set for every
# run. Omitting them has already produced a spurious 'output differs'
# result during preparatory work."
SOURCE_DATE_EPOCH = "1735689600"  # 2025-01-01T00:00:00Z


def _record(**fields: object) -> dict[str, object]:
    base = {
        "image_digest": None,
        "document": None,
        "baseline": None,
        "repetition": None,
        "classification": None,
        "predicted_runs": None,
        "executions_to_certify": None,
        "status": None,
        "static_analysis_latency_ms": None,
        "end_to_end_wall_clock_ms": None,
        "graph_facts": None,
        "graph_edges": None,
        "scc_count": None,
        "taint_set_size": None,
        "prediction_miss": None,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    base.update(fields)
    return base


def run_dynamic_baseline(
    document: str, baseline: str, repetition: int, image: str
) -> dict[str, object]:
    script = BASELINE_SCRIPTS[baseline]
    root = stage(document)
    try:
        code, stdout, _stderr, wall_ms = run_in_container(
            root,
            f"corpus/{document}",
            ["bash", f"/opt/auxflow/bench/baselines/{script}", str(MAX_RUNS)],
            image=image,
            env={
                "JOBNAME": "main",
                "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
                "FORCE_SOURCE_DATE": "1",
                "TEXINPUTS": ".:../shared:",
            },
        )
        if code != 0:
            return _record(
                image_digest=image_digest(image),
                document=document,
                baseline=baseline,
                repetition=repetition,
                status="tool_error",
                end_to_end_wall_clock_ms=wall_ms,
            )
        payload = json.loads(stdout.strip().splitlines()[-1])
        return _record(
            image_digest=image_digest(image),
            document=document,
            baseline=baseline,
            repetition=repetition,
            executions_to_certify=payload["runs"],
            status=payload["status"],
            end_to_end_wall_clock_ms=wall_ms,
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def run_baseline_d(document: str, main_tex: Path, repetition: int) -> dict[str, object]:
    result = analyze(str(main_tex))
    state = result.classification.state.name
    external = "CERTIFIED" if state in {"CERTIFIED", "BENIGN_CYCLIC"} else state
    return _record(
        document=document,
        baseline="D",
        repetition=repetition,
        classification=external,
        predicted_runs=result.classification.predicted_runs,
        executions_to_certify=0,
        status="CONVERGED" if external != "UNKNOWN" else "static_only",
        static_analysis_latency_ms=result.analysis_ms,
        end_to_end_wall_clock_ms=result.analysis_ms,
        graph_facts=result.graph_facts,
        graph_edges=result.graph_edges,
        scc_count=result.scc_count,
        taint_set_size=result.taint_set_size,
    )


def run_baseline_e(document: str, repetition: int, image: str) -> dict[str, object]:
    root = stage(document)
    try:
        main_tex = root / "corpus" / document / "main.tex"
        result = analyze(str(main_tex))
        state = result.classification.state.name
        external = "CERTIFIED" if state in {"CERTIFIED", "BENIGN_CYCLIC"} else state
        plan = result.plan
        if external == "AMPLIFYING" and not plan.steps:
            return _record(
                document=document,
                baseline="E",
                repetition=repetition,
                classification=external,
                predicted_runs=None,
                executions_to_certify=0,
                status="amplifying_refused",
                static_analysis_latency_ms=result.analysis_ms,
                end_to_end_wall_clock_ms=result.analysis_ms,
                graph_facts=result.graph_facts,
                graph_edges=result.graph_edges,
                scc_count=result.scc_count,
                taint_set_size=result.taint_set_size,
            )
        container_steps = [
            step if step.tool != "pdflatex" else replace(step, args=["main.tex"])
            for step in plan.steps
        ]
        container_plan = replace(plan, steps=container_steps)
        plan_path = root / "corpus" / document / "_plan.json"
        plan_path.write_text(to_json(container_plan), encoding="utf-8")
        strict_flag = ["--strict"] if external == "UNKNOWN" else []
        code, stdout, _stderr, wall_ms = run_in_container(
            root,
            f"corpus/{document}",
            ["python3", "/opt/auxflow/bench/harness/plan_incontainer.py", "_plan.json",
             *strict_flag],
            image=image,
            env={
                "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
                "FORCE_SOURCE_DATE": "1",
                "TEXINPUTS": ".:../shared:",
            },
        )
        report = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else {}
        return _record(
            image_digest=image_digest(image),
            document=document,
            baseline="E",
            repetition=repetition,
            classification=external,
            predicted_runs=plan.predicted_runs,
            executions_to_certify=report.get("runs"),
            status=report.get("status", "tool_error" if code != 0 else None),
            static_analysis_latency_ms=result.analysis_ms,
            end_to_end_wall_clock_ms=result.analysis_ms + wall_ms,
            graph_facts=result.graph_facts,
            graph_edges=result.graph_edges,
            scc_count=result.scc_count,
            taint_set_size=result.taint_set_size,
            prediction_miss=report.get("prediction_miss"),
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _run_one(
    document: str, baseline: str, repetition: int, corpus_dir: str, image: str
) -> dict[str, object]:
    print(f"{document} {baseline} rep={repetition}", file=sys.stderr)
    main_tex = Path(corpus_dir) / document / "main.tex"
    if baseline == "D":
        return run_baseline_d(document, main_tex, repetition)
    if baseline == "E":
        return run_baseline_e(document, repetition, image)
    return run_dynamic_baseline(document, baseline, repetition, image)


def _existing_counts(out_path: Path) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    if not out_path.exists():
        return counts
    with out_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            key = (record["document"], record["baseline"])
            counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default=str(HARNESS_DIR.parent / "corpus"))
    parser.add_argument("--baseline", default="all")
    parser.add_argument("--document", default="all")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.jsonl"

    lock_path = out_dir / ".run.lock"
    if lock_path.exists():
        pid = lock_path.read_text(encoding="utf-8").strip()
        if pid.isdigit() and Path(f"/proc/{pid}").exists():
            print(
                f"refusing to start: pid {pid} is already writing {out_path} "
                f"(remove {lock_path} if that is stale)",
                file=sys.stderr,
            )
            return 1
    lock_path.write_text(str(os.getpid()), encoding="utf-8")
    try:
        return _run_matrix(args, out_path)
    finally:
        lock_path.unlink(missing_ok=True)


def _run_matrix(args: argparse.Namespace, out_path: Path) -> int:
    baselines = list(ALL_BASELINES) if args.baseline == "all" else [args.baseline]
    documents = corpus_members() if args.document == "all" else [args.document]

    digest = image_digest(args.image) if any(b != "D" for b in baselines) else None
    print(f"image: {args.image} ({digest})", file=sys.stderr)

    existing = _existing_counts(out_path) if args.resume else {}
    tasks = []
    for document in documents:
        for baseline in baselines:
            already = existing.get((document, baseline), 0)
            for repetition in range(already, args.reps):
                tasks.append((document, baseline, repetition))
    print(f"{len(tasks)} tasks remaining (resume={args.resume})", file=sys.stderr)

    write_lock = threading.Lock()
    with (
        out_path.open("a", encoding="utf-8") as handle,
        ThreadPoolExecutor(max_workers=args.workers) as pool,
    ):
        futures = [
            pool.submit(_run_one, document, baseline, repetition, args.corpus, args.image)
            for document, baseline, repetition in tasks
        ]
        for future in as_completed(futures):
            record = future.result()
            with write_lock:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
