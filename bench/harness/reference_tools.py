#!/usr/bin/env python3
r"""Record latexmk/latexrun/Tectonic verdicts for every corpus member
(docs/EVALUATION.md "Reference implementations to run alongside"): a
cross-check for RQ6, not a baseline.

Usage: python3 bench/harness/reference_tools.py --out bench/results/published/reference_tools.json
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

SOURCE_DATE_EPOCH = "1735689600"


def compute_one(document: str, image: str) -> dict[str, object]:
    root = stage(document)
    try:
        code, stdout, stderr, _wall_ms = run_in_container(
            root,
            f"corpus/{document}",
            [
                "python3",
                "/opt/auxflow/bench/harness/reference_tools_incontainer.py",
                "--jobname",
                "main",
            ],
            image=image,
            env={
                "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
                "FORCE_SOURCE_DATE": "1",
                "TEXINPUTS": ".:../shared:",
            },
            timeout=240,
        )
        if code != 0:
            return {"document": document, "status": "tool_error", "stderr": stderr[-2000:]}
        payload = json.loads(stdout.strip().splitlines()[-1])
        return {"document": document, "status": "ok", "tools": payload["results"]}
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
        print(f"reference_tools: {document}", file=sys.stderr)
        return compute_one(document, args.image)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(_one, documents))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"image_digest": digest, "results": results}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    for result in results:
        print(f"{result['document']}: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
