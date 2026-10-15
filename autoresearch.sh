#!/usr/bin/env bash
# AuxFlow autoresearch benchmark entrypoint.
#
# Workload: score the machine-readable implementation plan
# (bench/plan/implementation-plan.yaml) against ground truth transcribed from
# docs/IMPLEMENTATION-PLAN.md and docs/SCOPE.md. The optimisation target is a
# faithful, complete GitHub rollout (project, milestones, phase issues,
# sub-issues) ready to post with `gh`.
#
# Deterministic: pure function of the committed files. No network, no clock,
# no randomness. Emits one `METRIC <name>=<value>` line per metric.
#
# Primary metric: plan_defects  (LOWER is better; 0 == faithful, complete plan)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PLAN="bench/plan/implementation-plan.yaml"
VALIDATOR="bench/plan/validate_plan.py"

if [[ ! -f "$PLAN" ]]; then
  echo "autoresearch: plan artifact missing: $PLAN" >&2
  exit 1
fi
if [[ ! -f "$VALIDATOR" ]]; then
  echo "autoresearch: validator missing: $VALIDATOR" >&2
  exit 1
fi

PYTHONHASHSEED=0 python3 "$VALIDATOR" "$PLAN"
