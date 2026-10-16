#!/usr/bin/env bash
# Baseline C -- checksum / consecutive-output comparison. latexmk's and
# ConTeXt's oracle. Costs N+1 executions: comparison starts only after run 1
# has produced an output to compare run 2 against (docs/EVALUATION.md).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
max_runs="${1:?usage: checksum.sh MAX_RUNS}"

start_ms=$(now_ms)
run_pdflatex 1
maybe_run_bibtool
prev=$(state_hash)

runs=1
while [ "$runs" -lt "$max_runs" ]; do
    runs=$((runs + 1))
    run_pdflatex "$runs"
    curr=$(state_hash)
    if [ "$curr" = "$prev" ]; then
        emit_result "$runs" "CONVERGED" "$start_ms"
        exit 0
    fi
    prev="$curr"
done
emit_result "$runs" "CAP_EXCEEDED" "$start_ms"
