#!/usr/bin/env bash
# Baseline A -- fixed schedule. No source analysis, no state inspection.
# Always three engine passes, with bibtex/biber after the first if the
# document asks for one. Reports CONVERGED unconditionally: that is the
# point of this baseline -- it never knows whether three was correct.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

start_ms=$(now_ms)
run_pdflatex 1
maybe_run_bibtool
run_pdflatex 2
run_pdflatex 3
emit_result 3 "CONVERGED" "$start_ms"
