#!/usr/bin/env python3
r"""Compute ground-truth N* per corpus member (docs/EVALUATION.md).

N* is the smallest k <= MAX such that the normalised auxiliary state and
the extracted text layer both equal their MAX-run reference value; else
`divergent(MAX)`. Independent of any baseline or AuxFlow prediction: the
sweep inside the container (groundtruth_incontainer.py) performs MAX
unconditional engine passes with no stopping rule of its own.

Usage: python3 bench/harness/groundtruth.py --out bench/results/published/groundtruth.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))

from container import DEFAULT_IMAGE, image_digest, run_in_container  # noqa: E402
from stage import corpus_members, stage  # noqa: E402

MAX_RUNS = 8
SOURCE_DATE_EPOCH = "1735689600"


def compute_one(document: str, image: str) -> dict[str, object]:
    root = stage(document)
    try:
        code, stdout, stderr, wall_ms = run_in_container(
            root,
            f"corpus/{document}",
            [
                "python3",
                "/opt/auxflow/bench/harness/groundtruth_incontainer.py",
                "--jobname",
                "main",
                "--max-runs",
                str(MAX_RUNS),
            ],
            image=image,
            env={
                "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
                "FORCE_SOURCE_DATE": "1",
                "TEXINPUTS": ".:../shared:",
            },
            timeout=300,
        )
        if code != 0:
            return {
                "document": document,
                "n_star": None,
                "status": "tool_error",
                "stderr": stderr[-2000:],
            }
        payload = json.loads(stdout.strip().splitlines()[-1])
        runs = payload["runs"]
        ref = runs[-1]

        def _matches(record: dict[str, object]) -> bool:
            state_match = record["state_hash"] == ref["state_hash"]
            text_match = record["text_hash"] == ref["text_hash"]
            return state_match and text_match

        # A match at k==MAX proves nothing -- comparing the reference state
        # to itself is trivial, not evidence of an earlier fixpoint -- so
        # only k<MAX counts (MAX==1 is the sole degenerate exception).
        candidate = None
        for record in runs:
            if record["k"] >= MAX_RUNS and MAX_RUNS > 1:
                break
            if _matches(record):
                candidate = record["k"]
                break

        # A match at k is only genuine evidence of a fixpoint if EVERY run
        # from k through MAX also matches -- a single coincidental match
        # (e.g. the even-numbered state of a period-2 oscillator landing on
        # the same phase as an even MAX) is not convergence. This
        # strengthens the literal adopted definition
        # (docs/EVALUATION.md: smallest N with A_N = A_MAX and T_N = T_MAX)
        # against exactly that false-positive, which real measurement on
        # this corpus's declared oscillating members (b11-b14) surfaced.
        n_star = None
        oscillating = False
        if candidate is not None:
            if all(_matches(record) for record in runs if record["k"] >= candidate):
                n_star = candidate
            else:
                oscillating = True

        if oscillating:
            status = (
                f"oscillating, not stable through run {MAX_RUNS} "
                "(ground-truth definition's single-endpoint match was a phase coincidence)"
            )
        else:
            status = f"N*={n_star}" if n_star is not None else f"divergent({MAX_RUNS})"
        return {
            "document": document,
            "n_star": n_star if n_star is not None else f"divergent({MAX_RUNS})",
            "oscillating": oscillating,
            "status": status,
            "max_runs": MAX_RUNS,
            "per_run": runs,
            "wall_clock_ms": wall_ms,
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--document", default="all")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    documents = corpus_members() if args.document == "all" else [args.document]
    digest = image_digest(args.image)

    def _one(document: str) -> dict[str, object]:
        print(f"groundtruth: {document}", file=sys.stderr)
        return compute_one(document, args.image)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(_one, documents))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {"image_digest": digest, "max_runs": MAX_RUNS, "results": results},
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    for result in results:
        print(f"{result['document']}: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
