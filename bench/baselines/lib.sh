# Shared TeX-invocation and normalisation helpers, sourced by every baseline
# script under bench/baselines/. Keeping the mechanics here means each
# baseline's own file is just its stopping-condition logic, matching
# bench/README.md's "a reviewer can read in a few lines exactly what was
# executed" rule -- the scripts differ ONLY in when they decide to stop,
# not in how pdflatex or bibtex/biber are invoked.
#
# Every baseline script is called as:  baseline.sh MAX_RUNS
# with JOBNAME exported by the caller and the current directory already
# containing the staged corpus document (main.tex, and ../shared/ present).
# Each script prints exactly one JSON line to stdout on exit.

set -euo pipefail

NORMSTATE=/opt/auxflow/bench/harness/normstate.py
JOBNAME="${JOBNAME:-main}"
EMPTY_HASH="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

export TEXINPUTS=".:../shared:${TEXINPUTS:-}"
# Deterministic timestamps even if the caller forgot to set one (run.py
# always does; this is a self-sufficiency fallback per
# bench/baselines/README.md's "every script must set deterministic
# timestamp variables").
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1735689600}"
export FORCE_SOURCE_DATE=1

run_pdflatex() {
    pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape \
      -jobname="$JOBNAME" main.tex > "run_${1}.log" 2>&1 || true
}

# Runs bibtex or biber exactly once, right after the first engine pass, iff
# the aux/bcf file asks for one -- docs/PROJECT.md D5: the external tool
# runs after run 1.
maybe_run_bibtool() {
    if [ -f "${JOBNAME}.bcf" ]; then
        biber "$JOBNAME" > bibtool.log 2>&1 || true
    elif [ -f "${JOBNAME}.aux" ] && grep -q '\\bibdata' "${JOBNAME}.aux" 2>/dev/null; then
        bibtex "$JOBNAME" > bibtool.log 2>&1 || true
    fi
}

state_hash() {
    python3 "$NORMSTATE" . "$JOBNAME"
}

now_ms() {
    python3 -c 'import time; print(time.time()*1000)'
}

# emit_result RUNS STATUS START_MS
emit_result() {
    end_ms=$(now_ms)
    python3 - "$1" "$2" "$end_ms" "$3" <<'PY'
import json, sys
runs, status, end_ms, start_ms = sys.argv[1:5]
print(json.dumps({
    "runs": int(runs),
    "status": status,
    "wall_clock_ms": float(end_ms) - float(start_ms),
}))
PY
}
