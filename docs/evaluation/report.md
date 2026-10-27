---
title: "Report"
parent: "Evaluation"
nav_order: 3
---

# Evaluation report

Every number in this report traces to a committed script and a results file under
`bench/results/published/`. Protocol in [EVALUATION.md](/evaluation/methodology.html); corpus design in
[BENCHMARKS.md](/evaluation/benchmarks.html); harness in [../bench/harness/](https://github.com/upayanmazumder/auxflow/tree/main/bench/harness/).

**No performance improvement is promised.** The experiments determine whether one exists.

**Update, 2026-10-24.** The published results below were measured before a classifier change.
The current classifier reports `b11_width`, `b12_float` and `b13_varioref` as UNKNOWN, not
CERTIFIED, so they are no longer false negatives of the static analysis. The published numbers
and `expected.json` files are historical and were not regenerated.

## Environment

- Image: `bench/Dockerfile` built from `python:3.12-slim-bookworm`
  (`sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258`), TeX Live from the
  Debian bookworm apt archive, `latexmk` 4.79, `biber` 2.18, `latexrun` (pinned commit
  `38ff6ec2815654513c91f64bdf2a5760c85da26e`), Tectonic 0.15.0, Typst 0.11.0.
- Built image digest recorded in every result: `sha256:5ce7c46493cbe5574c643e9fcd1c990d50ec19b41245162f55b5a057b977efc6`.
- One container per repetition, `--cpus=1`, `--network=none`, `SOURCE_DATE_EPOCH`/`FORCE_SOURCE_DATE`
  fixed. Ten repetitions per (document, baseline); 15 documents x 7 baselines = 105 combinations,
  1050 records total in `bench/results/published/results.jsonl`.
- Ground truth: `bench/harness/groundtruth.py`, MAX=8 unconditional engine passes per document,
  independent of every baseline and of AuxFlow's own prediction. Published in
  `bench/results/published/groundtruth.json`.

## Gate 1 — classification separation

From `bench/plan/implementation-plan.yaml` and `docs/AGENT-PROMPT.md`: `b08` must classify
AMPLIFYING with its three facts and correct spans; `b05` must not; `b11`-`b13` must be
misclassified *exactly as predicted* (declared false negatives); `b07` and `b15` must be UNKNOWN.

| Check | Result |
|---|---|
| `b08_cycle` observed AMPLIFYING | **PASS** |
| `b05_toc` not AMPLIFYING | **PASS** (CERTIFIED) |
| `b11_width` / `b12_float` / `b13_varioref` match their declared false negative (CERTIFIED) | **PASS**, all three |
| `b07_footnote` / `b15_ibid` UNKNOWN | **PASS**, both |

**Gate 1: PASS.** Regenerate with `python3 bench/harness/report.py bench/results/published --groundtruth bench/results/published/groundtruth.json`.

## Gate 2 — EC1

> On the benchmark corpus, for every document classified CERTIFIED with predicted bound *N*, the
> ground-truth run count *N\** satisfies *N ≥ N\** (`docs/STATIC-ANALYSIS.md`).

| Document | Predicted N | N* | N ≥ N* |
|---|---|---|---|
| `b01_plain` | 1 | 1 | yes |
| `b02_backref` | 2 | 2 | yes |
| `b03_fwdref` | 2 | 2 | yes |
| `b04_chain` | 3 | 2 | yes |
| `b05_toc` | 3 | 3 | yes |
| `b06_bib` | 4 | 3 | yes |
| `b09_thesis` | 4 | 3 | yes |
| `b11_width` | 2 | divergent(8) | **no — declared** |
| `b12_float` | 2 | divergent(8) | **no — declared** |
| `b13_varioref` | 2 | divergent(8) | **no — declared** |

**Gate 2 (EC1): PASS** — the only three violations are exactly the three documents declared as
false negatives before implementation (`expected.json`'s `declared_false_negative: true`). No
*undeclared* EC1 violation occurred anywhere in the corpus. `b07`/`b15`/`b10`/`b08`/`b14` are
excluded from this table because EC1 is defined only over CERTIFIED documents.

## Mechanism-coverage table

Full table: `bench/results/published/summary.md`. Every one of the fifteen documents classified
exactly as `expected.json` predicted; the three declared false negatives were misclassified
exactly as predicted, not discovered.

## Oracle-comparison table — executions to certify

| Document | N* | A (fixed) | B (warning) | C (checksum) | C′ (inputs) | C″ (read/write) | D (static) | E (static+verify) |
|---|---|---|---|---|---|---|---|---|
| `b01_plain` | 1 | 3 | 1 | 2 | 2 | 2 | **0** | 2 |
| `b02_backref`–`b04_chain` | 2 | 3 | 2 | 2 | 2 | 2 | **0** | 2 |
| `b05_toc` | 3 | 3 | 1 | 3 | 3 | 3 | **0** | 3 |
| `b06_bib` | 3 | 3 | 3 | 3 | 3 | 3 | **0** | 3 |
| `b07_footnote` | 2 | 3 | 2 | 2 | 2 | 2 | **0** | 0 (refused, opaque) |
| `b08_cycle` | divergent(8) | 3 (**wrong**) | 8 (capped) | 8 (capped) | 8 (capped) | 8 (capped) | **0** | 0 (refused, amplifying) |
| `b09_thesis` | 3 | 3 | 3 | 3 | 3 | 3 | **0** | 3 |
| `b10_random` | divergent(8) | 3 (**wrong**) | 1 (**false CONVERGED**) | 8 (capped) | 8 (capped) | 8 (capped) | **0** | 0 (refused, opaque) |
| `b11_width`/`b12_float`/`b13_varioref` | divergent(8) | 3 (**wrong**) | 8 (capped) | 8 (capped) | 8 (capped) | 8 (capped) | **0** | 6 (capped — caught!) |
| `b14_ifthen` | oscillating | 3 (**wrong**) | 8 (capped) | 8 (capped) | 8 (capped) | 8 (capped) | **0** | 0 (refused, amplifying) |
| `b15_ibid` | 3 | 3 | 1 | 3 | 3 | 3 | **0** | 0 (refused, opaque) |

Full distributions (median/p95/IQR across ten repetitions; identical in every cell here because
this corpus is deterministic except `b10_random`) are in `bench/results/published/summary.md`.
Regenerated figure: `bench/results/published/figures/executions.png`.

### Baseline A is silently wrong on every non-convergent document

Baseline A (fixed schedule) reports its unconditional three runs as done, with no way to know
whether three was enough. It is "correct" by coincidence on seven documents and silently wrong on
the six genuinely or declaredly non-convergent ones (`b08`, `b10`, `b11`–`b14`). This is the
expected, designed-in failure mode of a schedule that never looks at the document.

### Baseline B is unsound in both measured directions

- **Misses a real change** on `b10_random`: the engine never emits a rerun warning for a changing
  opaque random value with no cross-reference, so B reports `CONVERGED` after one run on every one
  of ten repetitions, while ground truth is `divergent(8)`. This is baseline B's documented
  false-negative direction, measured directly.
- **Costs nothing extra** on `b01_plain`/`b05_toc`/`b15_ibid`, converging at 1 run where C/C′/C″
  need 2–3 — but only because those documents happen not to trigger a second warning, not because
  B is sound; `b10_random` shows the same "no second warning" signature on a genuinely unstable
  document.

### Baseline E is the only dynamic baseline that catches the declared false negatives *as* false negatives

For `b11_width`, `b12_float` and `b13_varioref`, AuxFlow's static analysis (baseline D) wrongly
certifies the document — exactly as declared. But baseline E (static plan **plus** runtime
verification) does not silently accept that prediction: its executor keeps extending past the
predicted bound because the auxiliary state keeps changing, and correctly reports
`cap_exceeded` at the conservative 6-run ceiling on **all ten repetitions of all three
documents**. This is the central result for `docs/RUNTIME-VERIFICATION.md`'s design: static
analysis alone is wrong on these three documents, and the combination (E) is not.

### A genuine, measured prediction-timing artifact on the trivial document

`b01_plain` — zero facts, predicted *N*=1 — still needs 2 executions under baseline E, producing
a recorded `prediction_miss(predicted=1, observed=2)` on every repetition. Cause: pdfTeX's own
kernel writes `\gdef\@abspage@last{1}` to every `.aux` file regardless of document content, so the
auxiliary state is never literally the empty set the executor's single-run shortcut requires; the
runtime verifier must still perform one confirming run to observe two identical states. This is
not a bug in AuxFlow's prediction — the static model prediction `N=1` *is* the correct ground
truth (*N\**=1, confirmed independently) — it is a structural property of any consecutive-state
comparison detector applied to a kernel that always emits one content-free bookkeeping record.
Documented for completeness; not claimed as a flaw.

### The ground-truth criterion needed strengthening to survive real period-2 oscillation

The literal adopted criterion (smallest *N* with *Â_N = Â_MAX* and *T_N = T_MAX*, MAX=8) accepts
a single coincidental match: for a genuinely period-2 oscillating document with an even MAX, the
even-numbered states all share one phase, so the smallest even *k* < MAX trivially matches
*Â_MAX* even though the document never actually stabilises. Measured directly: before this was
caught, `b11_width`/`b12_float`/`b13_varioref`/`b14_ifthen` each reported a spurious finite
*N\**=2. `bench/harness/groundtruth.py` now additionally requires every run from the candidate
*k* through MAX to match, which correctly reclassifies all four as oscillating (recorded in
`groundtruth.json`'s `status` field; the `n_star` field keeps the coarser `divergent(8)` label
used above, since no finite bound is valid either way). This is a strengthening of the documented
definition, implemented and disclosed, not a silent deviation from it.

## External cross-check (RQ6): what shipping tools say about the same corpus

`bench/harness/reference_tools.py`, `bench/results/published/reference_tools.json`.

| | `latexmk` 4.79 | `latexrun` | Tectonic 0.15.0 |
|---|---|---|---|
| `b01`–`b07`, `b09` (genuinely CERTIFIED) | converges | converges | converges (`b01` only; see note) |
| `b08_cycle` | **fails to converge** | **fails to converge** | **fails to converge** ("TeX rerun seems needed, but stopping at 6 passes") |
| `b10_random` | **fails to converge** | **fails to converge** | network-blocked (see note) |
| `b11_width`, `b12_float`, `b13_varioref` | **fail to converge, all three** | **fail to converge, all three** | network-blocked |
| `b14_ifthen` | **fails to converge** | **fails to converge** | network-blocked |
| `b15_ibid` | converges | **fails to converge** | network-blocked (biblatex bundle version mismatch) |

**The headline cross-check result:** `latexmk` and `latexrun` — real, independently-implemented,
widely deployed tools — themselves fail to converge on `b11_width`, `b12_float` and
`b13_varioref`, the exact three documents AuxFlow's static analysis wrongly certifies. This is
concrete, measured, cross-tool confirmation that the declared-false-negative mechanism is a real
non-convergence phenomenon in these documents, not a corpus-authoring artifact invented for this
project.

**Note on Tectonic's offline coverage.** Only `b01_plain` and `b08_cycle` compile fully offline
against the image's build-time-primed bundle; every other document needs a network lookup against
Tectonic's own file index for packages/fonts outside the primer set, which `--network=none`
(required for reproducibility) blocks. `b09_thesis` additionally cannot find the repo-local
`auditthesis.cls` because Tectonic's sandboxed bundle does not read local `TEXINPUTS`. This is a
disclosed limitation of the cross-check's offline coverage, not a claim about Tectonic's
correctness. Where Tectonic *did* run (`b08_cycle`), its own independent 6-pass iteration cap
agrees with the AMPLIFYING verdict.

**Typst, hand-ported** (`bench/harness/typst-ports/`, mechanism ports, not literal translations —
Typst has no `\pageref`/`\forloop` syntax):

- `b08_cycle`'s loop, ported: Typst's compiler itself refuses with `error: loop seems to be
  infinite`, via its own internal relayout-until-fixpoint bound — a third, independently
  implemented tool reaching the AMPLIFYING verdict.
- `b14_ifthen`'s page-conditioned size, ported: Typst compiles cleanly (2 pages, no error).
  Typst's internal relayout finds a genuine fixpoint that LaTeX's single-pass `.aux`
  write-then-reread model cannot see in one pass — direct evidence *for* AuxFlow's own documented
  over-approximation on this member ("a true positive obtained by over-approximation... nothing
  changes the *quantity* of content, only its size", `docs/BENCHMARKS.md`).
- `b11_width`, `b12_float`, `b13_varioref` are **not ported**: no Typst analogue exists for
  LaTeX's stale-first-pass line-break width feedback, its `[!t]` float-placement heuristic, or
  `varioref`'s package-specific text selection. See `bench/harness/typst-ports/README.md`.

## Analysis latency and graph size

From baseline D (`bench/results/published/results.jsonl`, `static_analysis_latency_ms`,
`graph_facts`, `graph_edges`, `scc_count`): every document's static analysis — parse through
classification through plan — completes in **under 10ms**, including the 91-fact, 73-edge
`b09_thesis` realistic case (9.65ms median). This is shown as overhead in its own right, not
netted against any engine saving.

## Threats to validity

Unchanged from the pre-registered list in [EVALUATION.md](/evaluation/methodology.html): corpus size (fifteen
documents, mostly synthetic), single machine, synthetic non-convergence (`b08` is a known
constructed example), assumption A2 (measured via prediction misses, not provably bounded), and
author bias (`expected.json` written before implementation). Two measured, specific instances
worth naming explicitly:

- The `\@abspage@last` prediction-timing artifact on `b01_plain` (above) shows assumption A2's
  "converges within predicted *N*, confirmed" clause is sensitive to kernel bookkeeping the static
  model does not and should not model — it does not affect *N\** itself, only how many executions
  the *verifier* needs to confirm it.
- Tectonic's offline coverage in the cross-check is incomplete (above); the `latexmk`/`latexrun`
  cross-check is complete across all fifteen documents and is the primary external confirmation.

## End-to-end demonstration

`bench/demo.sh` runs the full pipeline — `tokens`/`ast`/`check`/`graph`/`classify`/
`plan --explain` on `bench/corpus/b08_cycle/main.tex`, then ties the static AMPLIFYING verdict to
the published measurement evidence (10/10 baseline-D repetitions agree; ground truth shows eight
genuinely distinct real-engine states; `latexmk` and Typst independently fail to converge on the
same document), then repeats the static step on `b11_width` and confirms its declared false
negative against the real engine's period-2 state alternation. Verified running end to end:

```
$ auxflow run --force bench/corpus/b08_cycle/main.tex
[... 6 pdflatex passes, 1 -> 2 -> 3 -> 4 -> 5 -> 6 pages, "Label(s) may have
changed" every pass ...]
{"message": "suspected non-convergence: auxiliary state changed through run 6",
 "prediction_miss": null, "runs": 6, "status": "cap_exceeded", "stop_condition": "cap"}
$ bash bench/demo.sh
...
baseline D (static analysis): 10/10 repetitions, classification={'AMPLIFYING'}
ground truth: divergent(8); 8 distinct real-engine state hashes: [...]
latexmk (independent tool): converged=False, pdflatex_passes=5
Typst (independent implementation): converged=False, 'error: loop seems to be infinite'
...
ground truth: oscillating, not stable through run 8 (...)
real engine states, period-2 forever: ['add8c2c1', '72beb0e4', 'add8c2c1', '72beb0e4', ...]

Demonstration complete: both the headline AMPLIFYING case and a declared
false negative reproduced start-to-finish from committed sources alone.
```

Page count in the forced `b08_cycle` run grows by exactly one per pass (1, 2, 3, 4, 5, 6) — the
monotone divergence the static analysis predicted, observed directly, capped at the conservative
6-run ceiling rather than run forever.


## Reproducing this report

```
docker build -t auxflow-bench:v1 -f bench/Dockerfile .
python3 bench/harness/groundtruth.py --out bench/results/published/groundtruth.json
python3 bench/harness/reference_tools.py --out bench/results/published/reference_tools.json
python3 bench/harness/run.py --corpus bench/corpus --baseline all --reps 10 --workers 2 \
    --out bench/results/published
python3 bench/harness/report.py bench/results/published \
    --groundtruth bench/results/published/groundtruth.json \
    --figure bench/results/published/figures/executions.png \
    > bench/results/published/summary.md
```

Every table above regenerates byte-identically from the committed JSONL (deterministic corpus,
`b10_random` excepted by design — its ten repetitions agree on *classification* and *status*, not
on the opaque random value itself, which is the point of that corpus member).
