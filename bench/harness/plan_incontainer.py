#!/usr/bin/env python3
r"""Execute a serialised BuildPlan inside the pinned container (baseline E).

Baseline D (static analysis alone) needs no container at all -- it is the
BuildPlan computation itself, run on the host, zero engine executions. This
driver covers the second half of baseline E: given the plan the host already
computed, perform the engine runs and runtime verification, reusing
auxflow.runtime.execute.execute verbatim rather than re-implementing the
stop/extend loop a second time.

Usage: plan_incontainer.py PLAN_JSON_PATH [--strict]
Prints the ExecReport as one JSON line to stdout.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from auxflow.planner.serialize import from_json
from auxflow.runtime.execute import execute


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    if len(args) != 1:
        print("usage: plan_incontainer.py PLAN_JSON_PATH [--strict]", file=sys.stderr)
        return 2
    plan = from_json(Path(args[0]).read_text(encoding="utf-8"))
    report = execute(plan, Path.cwd(), strict=strict)
    print(json.dumps(asdict(report), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
