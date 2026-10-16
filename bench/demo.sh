#!/usr/bin/env bash
# Rehearsed end-to-end demonstration (phase 16 acceptance criterion).
#
# Runs the full pipeline -- tokens/ast/check/graph/classify/plan --explain
# -- on b08_cycle, the headline AMPLIFYING case, then ties the static
# verdict to the published measurement evidence: 10/10 baseline-D
# repetitions agree, the ground-truth sweep shows eight genuinely distinct
# auxiliary states (real divergence, not a stale assumption), and two
# independent tools (latexmk, Typst) refuse to converge on the same
# document via unrelated implementations.
#
# Then repeats the static-analysis step on b11_width, a declared false
# negative: static analysis says CERTIFIED, expected.json said in advance
# that this was expected to be wrong, and the ground-truth sweep shows
# real period-two state alternation forever.
#
# Prerequisites: `pip install -e .`, `docker build -t auxflow-bench:v1 -f
# bench/Dockerfile .`, and bench/results/published/{groundtruth,
# reference_tools}.json already generated (bench/harness/groundtruth.py,
# bench/harness/reference_tools.py).
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/.."

section() { printf '\n=== %s ===\n' "$1"; }

section "1/8  auxflow tokens (lexer, b08_cycle)"
auxflow tokens bench/corpus/b08_cycle/main.tex 2>/dev/null | head -5

section "2/8  auxflow ast (parser, b08_cycle)"
auxflow ast bench/corpus/b08_cycle/main.tex | head -12

section "3/8  auxflow check (semantic diagnostics, b08_cycle)"
auxflow check bench/corpus/b08_cycle/main.tex && echo "(no diagnostics -- clean)"

section "4/8  auxflow graph (ARG as DOT, b08_cycle)"
auxflow graph bench/corpus/b08_cycle/main.tex 2>/dev/null | head -8

section "5/8  auxflow classify (AMPLIFYING cycle with named facts and spans)"
auxflow classify bench/corpus/b08_cycle/main.tex || true

section "6/8  auxflow plan --explain --force (bounded conservative plan under the cap)"
auxflow plan --explain --force bench/corpus/b08_cycle/main.tex

section "7/8  Measurement evidence for the AMPLIFYING verdict (bench/results/published/)"
python3 - <<'PY'
import json
recs = [json.loads(l) for l in open("bench/results/published/results.jsonl")]
d = [r for r in recs if r["document"] == "b08_cycle" and r["baseline"] == "D"]
print(f"baseline D (static analysis): {len(d)}/10 repetitions, "
      f"classification={set(r['classification'] for r in d)}")

gt = json.load(open("bench/results/published/groundtruth.json"))
row = next(r for r in gt["results"] if r["document"] == "b08_cycle")
hashes = [x["state_hash"][:8] for x in row["per_run"]]
print(f"ground truth: {row['status']}; 8 distinct real-engine state hashes: {hashes}")
assert len(set(hashes)) == 8, "expected eight genuinely distinct states"

ref = json.load(open("bench/results/published/reference_tools.json"))
rrow = next(r for r in ref["results"] if r["document"] == "b08_cycle")
latexmk = next(t for t in rrow["tools"] if t["tool"] == "latexmk")
print(f"latexmk (independent tool): converged={latexmk['converged']}, "
      f"pdflatex_passes={latexmk['pdflatex_passes']}")
typst = ref["typst_ports"]["b08_cycle"]
print(f"Typst (independent implementation): converged={typst['converged']}, {typst['result']!r}")
PY

section "8/8  Declared false negative (b11_width): static says CERTIFIED, measured reality oscillates"
auxflow classify bench/corpus/b11_width/main.tex
python3 - <<'PY'
import json
expected = json.load(open("bench/corpus/b11_width/expected.json"))
print(f"expected.json (written before implementation): "
      f"declared_false_negative={expected['declared_false_negative']}, "
      f"mechanism={expected['mechanism']!r}")
gt = json.load(open("bench/results/published/groundtruth.json"))
row = next(r for r in gt["results"] if r["document"] == "b11_width")
hashes = [x["state_hash"][:8] for x in row["per_run"]]
print(f"ground truth: {row['status']}")
print(f"real engine states, period-2 forever: {hashes}")
assert hashes[0::2] == [hashes[0]] * 4 and hashes[1::2] == [hashes[1]] * 4, \
    "expected a clean period-2 alternation"
PY

printf '\nDemonstration complete: both the headline AMPLIFYING case and a declared\nfalse negative reproduced start-to-finish from committed sources alone.\n'
