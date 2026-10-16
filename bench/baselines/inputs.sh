#!/usr/bin/env bash
# Baseline C' -- consecutive-input comparison. latexrun's oracle: if the
# inputs to run k (the aux state run k-1 produced, or nothing before run 1)
# equal the inputs to run k-1, run k is guaranteed redundant and need not be
# performed. Costs exactly N executions (docs/EVALUATION.md) because the
# comparison baseline starts at the empty pre-run-1 state, one run earlier
# than baseline C's.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
max_runs="${1:?usage: inputs.sh MAX_RUNS}"

start_ms=$(now_ms)
prev="$EMPTY_HASH"

run_pdflatex 1
maybe_run_bibtool
curr=$(state_hash)
if [ "$curr" = "$prev" ]; then
    emit_result 1 "CONVERGED" "$start_ms"
    exit 0
fi
prev="$curr"

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
