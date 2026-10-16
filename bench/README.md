# Benchmark corpus and measurement harness

Corpus design is specified in [../docs/BENCHMARKS.md](../docs/BENCHMARKS.md); the measurement
protocol and ground-truth definition in [../docs/EVALUATION.md](../docs/EVALUATION.md). This
file covers organisation and operation.

**Results are not committed under `results/` itself** (regenerated, not source); the published
set lives under `results/published/` once a measurement run has been promoted there.

## Organisation

```
bench/
  Dockerfile    pinned evaluation environment (TeX Live + reference tools + auxflow)
  corpus/       fifteen documents, sources only, one directory each
    shared/     shared bibliography database and document class
  baselines/    the convergence-detection mechanisms under comparison
  harness/      execution, normalisation, ground truth, reporting
  results/      JSONL output; regenerated, not committed
    published/  result sets deliberately promoted for the report
```

Each corpus directory contains `main.tex`, `expected.json` and a one-paragraph `README.md`
stating which mechanism the document exists to exercise.

Build artifacts are gitignored. A corpus directory should contain sources only; if it contains
an auxiliary or output file, something has run in the wrong place.

## Environment requirements

- A TeX engine with the standard tooling, supplied by `bench/Dockerfile`, a container image
  pinned by digest (`python:3.12-slim-bookworm` base; resolved open decision D10 in
  [../docs/PROJECT.md](../docs/PROJECT.md)). Build it with
  `docker build -t auxflow-bench:v1 -f bench/Dockerfile .` from the repo root. It includes
  `latexmk`, `latexrun`, `tectonic`, `typst`, `biber`, `labelschanged`, and `auxflow` itself
  (pip-installed, so baseline scripts and the ground-truth sweep share identical normalisation
  with the host).
- No engine is needed for anything other than the harness. Every compiler command up to and
  including `auxflow plan` runs without one. Baseline D never touches the container at all.
- The harness sets `SOURCE_DATE_EPOCH` itself rather than relying on the environment.

## Baselines

| Script | Mechanism | Notes |
|---|---|---|
| `baselines/fixed.sh` | Fixed schedule (A) | The conventional sequence; no source analysis |
| `baselines/warning.sh` | Engine-warning detection (B) | Included **because it is unsound**; the gap against ground truth is a result |
| `baselines/checksum.sh` | Consecutive-output comparison (C) | `latexmk`'s and ConTeXt's oracle; costs *N*+1 executions |
| `baselines/inputs.sh` | Consecutive-input comparison (C′) | `latexrun`'s oracle; costs *N* executions |
| `baselines/readwrite.sh` | Same-run read-then-written comparison (C″) | Tectonic's oracle; costs *N* executions, available one run earlier than C′ in wall-clock terms |

Baselines are shell scripts so that a reviewer can read in a few lines exactly what was
executed; `baselines/lib.sh` holds only the shared pdflatex/bibtex invocation mechanics, never
the stopping-condition logic itself. Each script calls `harness/normstate.py` (pip-installed
into the container alongside `auxflow`) for its state fingerprint, so every baseline compares
exactly the canonical records `auxflow.runtime.normalize` defines.

The two AuxFlow configurations — static analysis alone (D), and static analysis with runtime
verification (E) — are driven through `harness/analyze.py` and `harness/plan_incontainer.py`
rather than through shell scripts, reusing the same code path `auxflow classify`/`plan`/`run`
use.

## Running

```
docker build -t auxflow-bench:v1 -f bench/Dockerfile .
python3 bench/harness/groundtruth.py --out bench/results/published/groundtruth.json
python3 bench/harness/run.py --corpus bench/corpus --baseline all --reps 10 \
    --out bench/results/$(date -I)
python3 bench/harness/report.py bench/results/$(date -I) \
    --groundtruth bench/results/published/groundtruth.json > bench/results/$(date -I)/summary.md
```

`run.py` emits one JSONL record per repetition, each carrying the image digest, document
identifier, baseline, repetition index and every metric. `report.py` regenerates all tables from
that JSONL, so no figure in the report is produced by hand.

## Ground truth

Computed by `harness/groundtruth.py`, independently of any AuxFlow prediction.

The adopted criterion is the smallest run count at which both the normalised auxiliary state and
the extracted text layer match an eight-run reference. PDF byte equality is recorded as a
secondary column and is **not** ground truth — it has already been observed to be too strict,
flagging a difference where the auxiliary files were identical.

Ground truth is generated once per corpus revision, committed under `results/published/`, and
regenerated whenever a corpus document changes.

## Repetition and reporting

- At least ten repetitions per (document, baseline).
- Median, p95 and interquartile range. Point estimates are not reported for timings.
- One container per repetition; CPU pinned; no concurrent measurement.
- Cold conditions are primary: fresh working directory, no auxiliary files.
- Per-document results only. **No corpus-wide mean** — it measures corpus composition rather
  than the system.

## Rules

1. No number appears in this repository without a script that regenerates it.
2. `expected.json` is hand-derived before implementation and is never back-filled from program
   output.
3. Documents where AuxFlow provides no benefit are reported with the same prominence as those
   where it does.
4. Analysis latency is reported as overhead, never netted out of an end-to-end figure.
5. The list of record kinds excluded during normalisation is committed, small, and justified per
   entry. It is the easiest place for an evaluation to go quietly wrong.
