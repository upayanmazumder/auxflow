#!/usr/bin/env bash
# Baseline B -- engine-warning detection. Unsound in both directions
# (docs/EVALUATION.md): misses a changed generated list with no
# cross-reference, and can fire on an already-stable active-character
# caption (M9). Included because that gap against the C family is a result.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
max_runs="${1:?usage: warning.sh MAX_RUNS}"

start_ms=$(now_ms)
run_pdflatex 1
maybe_run_bibtool

runs=1
while [ "$runs" -lt "$max_runs" ]; do
    if ! grep -qiE 'rerun to get|label\(s\) may have changed' "run_${runs}.log"; then
        emit_result "$runs" "CONVERGED" "$start_ms"
        exit 0
    fi
    runs=$((runs + 1))
    run_pdflatex "$runs"
done
if ! grep -qiE 'rerun to get|label\(s\) may have changed' "run_${runs}.log"; then
    emit_result "$runs" "CONVERGED" "$start_ms"
else
    emit_result "$runs" "CAP_EXCEEDED" "$start_ms"
fi
