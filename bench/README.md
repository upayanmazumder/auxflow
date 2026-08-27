# Benchmark corpus and measurement harness

Corpus design is specified in [../docs/BENCHMARKS.md](../docs/BENCHMARKS.md); the measurement
protocol and ground-truth definition in [../docs/EVALUATION.md](../docs/EVALUATION.md). This
file covers organisation and operation.

**No results are recorded in this directory yet, and none should be invented.** Any number that
appears here must be regenerable by `harness/run.py`.

## Organisation

```
bench/
  corpus/       ten documents, sources only, one directory each
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

- A TeX engine with the standard tooling, supplied by a **container image pinned by digest**.
  The image must include `latexmk` so that an external cross-check of the state-comparison
  baseline is possible. Selecting and pinning the image is open decision D10 in
  [../docs/PROJECT.md](../docs/PROJECT.md) and must be closed before the first measurement.
- No engine is needed for anything other than the harness. Every compiler command up to and
  including `auxflow plan` runs without one.
- The harness sets deterministic timestamp variables itself rather than relying on the
  environment.

## Baselines

| Script | Mechanism | Notes |
|---|---|---|
| `baselines/fixed.sh` | Fixed schedule | The conventional sequence; no source analysis |
| `baselines/warning.sh` | Engine-warning detection | Included **because it is unsound**; the gap against ground truth is a result |
| `baselines/checksum.sh` | Normalised state comparison | Standard practice; costs one execution beyond the last productive run |

Baselines are shell scripts so that a reviewer can read in a few lines exactly what was
executed. They share the harness's normalisation so that they differ only in the mechanism under
study.

The two AuxFlow configurations — static analysis alone, and static analysis with runtime
verification — are driven through the harness rather than through shell scripts.

## Running

Not yet implemented. The intended interface:

```
python harness/run.py --corpus corpus --baseline all --reps 10 --out results/$(date -I)
python harness/report.py results/<dir> > results/<dir>/summary.md
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
- Cold conditions are primary: fresh working directory, no auxiliary files, one discarded run
  first to warm the engine's format cache.
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
