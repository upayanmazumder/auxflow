# Runtime verification

Separate from the static analysis, and deliberately so. The analysis predicts; verification
checks. There is no feedback path from verification back into the analysis within a single
invocation.

## Why not engine warnings

The obvious implementation — run until the engine stops asking to be re-run — is **unsound**.

LaTeX emits a rerun warning when *references* have changed. It does not emit one when a
generated list such as a table of contents has changed. A document with a table of contents and
no cross-references produces no warning after the first run, yet at that point the output is
missing its entire table of contents.

Independent confirmation: the `rerunfilecheck` package exists specifically to add checksum-based
detection of auxiliary-file changes that base LaTeX does not report. A mechanism whose gap
needed a package written to fill it is not a sound oracle.

Preliminary measurements of this behaviour are in
[`research/preliminary-measurements.md`](../research/preliminary-measurements.md).

Engine warnings are therefore retained **only as evaluation baseline B**, precisely because
demonstrating their unsoundness is a result.

## What state is observed

After each engine run, the auxiliary state consists of the files the engine and its companion
tools write and read back: the main auxiliary file, generated list files (contents, figures,
tables), the bibliography body, and the index if present.

Raw file comparison is rejected: it is sensitive to line ordering and to records irrelevant to
convergence. Instead the state is **normalised**.

## Normalisation

Parse each auxiliary file into a set of canonical records:

| Source | Canonical record |
|---|---|
| label definition | `("label", key, number, page)` |
| contents entry | `("toc", level, title_text, page)` |
| figure list entry | `("lof", number, caption_text, page)` |
| table list entry | `("lot", number, caption_text, page)` |
| bibliography item | `("bib", key, formatted_text)` |

Discard ordering, whitespace, comments, and any record kind on a documented exclusion list. The
result is a **set**, compared by equality.

The exclusion list must be small, committed, and justified per entry. It is the obvious place
for an evaluation to go quietly wrong, so every exclusion needs a written reason.

## When it is observed

After every engine run in the plan, and after every extension run. Observation is cheap relative
to a run — parsing a few auxiliary files against a typesetting pass — so there is no reason to
sample.

## How stability is determined

```
run 1
state_prev <- normalise(aux_files)
for k in 2 .. max_runs:
    run k
    state_curr <- normalise(aux_files)
    if state_curr == state_prev:
        return CONVERGED at k
    state_prev <- state_curr
return CAP_EXCEEDED
```

Two properties of this loop matter for the evaluation:

1. It is **sound** in the sense the engine warning is not: it observes the state directly rather
   than trusting the engine to report a change.
2. It **costs one execution beyond the last productive run**. To conclude that *A_N* is the
   fixpoint it must compare *A_N* with *A_{N+1}*, which requires performing run *N+1*. The
   information "nothing changed" does not exist until the redundant run has been paid for.

Point 2 is the structural gap that static analysis addresses, and it is worth exactly one
execution — no more. Do not inflate it.

## Relationship to practical build tools

Established build tools for multi-pass documents already use checksum comparison over auxiliary
files. `latexmk` documents this directly: it examines file contents by checksum to decide
whether another run is needed, and caps iteration with a configurable maximum.

AuxFlow's verifier is therefore **not novel** and is not claimed to be. It is a faithful
reimplementation of standard practice, included so that:

- the executor can confirm or refute a static prediction;
- baseline C in [EVALUATION.md](EVALUATION.md) is measured with exactly the same normalisation
  as AuxFlow, making the comparison fair.

Reimplementing rather than shelling out to an existing tool is a deliberate choice: it removes a
confounder, since the baseline and the verifier then differ only in whether a static prediction
was available.

## How static and dynamic complement each other

| | Static analysis | Runtime verification |
|---|---|---|
| Available | before any execution | only after execution |
| Cost | milliseconds | one engine run per observation |
| Covers | modelled constructs only | whatever actually happened |
| Fails by | over-approximating, or classifying unknown | costing an extra run |
| Answers | *what should happen, and why* | *what did happen* |

They are complementary rather than competing. The analysis supplies a plan and an explanation;
verification supplies the ground for trusting it on a document outside the model. The
combination — baseline E — is the configuration a real user would want, and it is expected to
match baseline C on execution count while adding an explanation and an early diagnosis for the
non-convergent case.

## Extension policy

If the planned runs complete and the state is still changing, the executor performs additional
runs up to `max_runs`, and records a **prediction miss** with the document, the predicted count,
and the observed count.

Prediction misses are reported, never suppressed. Under assumption A2 they should not occur for
certified documents; each one is evidence about where A2 breaks, which is a finding rather than
an embarrassment.

## What verification does not do

- It does not modify the plan for future invocations. Any model improvement is offline and
  deliberate.
- It does not judge output correctness, only auxiliary-state stability. Ground truth for the
  evaluation additionally requires rendered-output stability; see [EVALUATION.md](EVALUATION.md).
- It does not detect non-convergence in the sense of a proof. Reaching the cap is evidence, not
  a demonstration.
