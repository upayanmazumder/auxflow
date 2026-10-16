#!/usr/bin/env bash
# Baseline C'' -- same-run read-then-written comparison. Tectonic's
# `is_rerun_needed` oracle: compare the state a run *read* at its start
# against the state it *wrote* by its end; if identical, stability is known
# within that run, with no need to even contemplate a further run. Costs
# exactly N executions, the same count as C' (docs/EVALUATION.md), but the
# evidence is available one run earlier in wall-clock terms than C's.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
max_runs="${1:?usage: readwrite.sh MAX_RUNS}"

start_ms=$(now_ms)
runs=0
while [ "$runs" -lt "$max_runs" ]; do
    runs=$((runs + 1))
    read_state=$(state_hash)
    run_pdflatex "$runs"
    if [ "$runs" -eq 1 ]; then
        maybe_run_bibtool
    fi
    written_state=$(state_hash)
    if [ "$read_state" = "$written_state" ]; then
        emit_result "$runs" "CONVERGED" "$start_ms"
        exit 0
    fi
done
emit_result "$runs" "CAP_EXCEEDED" "$start_ms"
