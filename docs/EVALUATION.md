# Evaluation methodology

Fixed before any measurement is taken, so that the protocol cannot be adjusted to suit results.

**No performance improvement is promised anywhere in this repository.** The experiments
determine whether one exists. Preliminary evidence suggests savings concentrate on documents
that are already cheap, which is the least valuable place to win; that is reported as a finding,
not hidden.

## Baselines

| | Baseline | What it observes | When it knows | Executions to certify a document needing *N* runs |
|---|---|---|---|---|
| **A** | Fixed schedule | nothing | never | always 3, plus tools |
| **B** | Engine-warning detection | rerun warnings in the engine log | after each run | *N*, but **unsound** — misses generated-list changes |
| **C** | Checksum / state-based detection | normalised auxiliary state | after each run | ***N + 1*** |
| **D** | AuxFlow static analysis | source only | **before any run** | **0** |
| **E** | AuxFlow static plus runtime verification | source, then state | before, confirmed after | *N*, plus 1 only on a prediction miss |

Baselines B and C are implemented inside this repository rather than delegated to an external
tool, so that B, C and E share identical normalisation and differ only in the mechanism under
study. Delegating C to an existing tool would introduce differences in file handling and
iteration caps that confound the comparison.

Baseline B is included **because** it is unsound. Demonstrating the gap between B and C is one
of the results.

### Why baseline C costs an extra execution

C concludes stability by observing that a transition changed nothing. To establish that state
*A_N* is the fixpoint it must compare *A_N* against *A_{N+1}*, which requires performing run
*N+1*. The information does not exist until the redundant run has been paid for.

This is a structural property of consecutive-state comparison, not a defect in any particular
tool, and the gap is exactly one execution.

## Ground truth

Choosing this correctly matters more than any other decision in the evaluation.

### Candidate criteria, assessed

| Criterion | Verdict |
|---|---|
| PDF byte equality | **Rejected as primary — too strict.** Preliminary measurement found a document whose three-run and converged outputs differed byte-wise while their auxiliary files were identical, the difference lying in internal document structure rather than content. Byte equality yields an upper bound on the requirement, not the requirement. |
| Raw auxiliary file equality | **Rejected** — sensitive to line ordering and to records irrelevant to convergence. |
| Rendered text equality alone | **Rejected** — necessary but insufficient; misses page-number changes that leave extracted text order intact. |
| Engine warnings | **Rejected outright** — measured unsound. Never ground truth. |
| **Normalised auxiliary-state equality plus rendered-text equality** | **Adopted.** |

### Definition

Let *Â_k* be the normalised auxiliary state after run *k*, as defined in
[RUNTIME-VERIFICATION.md](RUNTIME-VERIFICATION.md), and let *T_k* be the extracted text layer of
the rendered output.

> **Ground truth *N\**** is the smallest *N* such that
> (a) *Â_N = Â_MAX*, and
> (b) *T_N = T_MAX*,
> where MAX is a reference run count of 8.
> If no such *N ≤ MAX* exists, *N\** is recorded as `divergent(MAX)`.

Condition (a) is the fixpoint. Condition (b) guards against auxiliary state that has settled
while output has not.

PDF byte equality is reported as a **secondary column**, never as ground truth, and the
documents where it disagrees with *N\** are shown explicitly — that disagreement is evidence for
the methodology.

This remains **open decision D6** until the corpus is authored and the exclusion list for
normalisation is settled. It must be closed before any ground truth is generated.

## Metrics

| Metric | Definition |
|---|---|
| Ground-truth run count | *N\** as above |
| Predicted run count | from the build plan; blank when unbounded |
| Prediction error | predicted − *N\**; separated into over- and under-prediction |
| Executions to certify | engine runs consumed by each baseline before it can assert completion |
| Unnecessary executions | executions beyond *N\** |
| Classification | assigned state versus the hand-written expectation |
| False negative | a potentially non-convergent document classified convergent. **The metric that matters most.** |
| False positive | a convergent document classified amplifying |
| Static analysis latency | wall time from source to plan, engine excluded |
| Graph size | fact count, edge count, SCC count, taint-set size |
| Non-convergence detection latency | executions performed before the cause is reported. Zero for AuxFlow; at least the retry cap for dynamic tools |
| End-to-end wall clock | total, including analysis overhead |

Analysis latency is reported as overhead in its own right and is never netted out of the
end-to-end figure.

## Protocol

- **Environment.** A public TeX Live container image, pinned by digest and recorded in the
  results file. The image must contain `latexmk` so that an external cross-check of baseline C
  is possible. Selecting and pinning it is **open decision D10**.
- **Repetitions.** At least ten per (document, baseline). Report **median, p95 and
  interquartile range**. Preliminary single-shot measurements varied by more than ten percent
  between runs, so any claimed difference below roughly twenty percent requires the
  distribution to be shown.
- **Cold and warm.** Cold: a fresh working directory with no auxiliary files, preceded by one
  discarded run to warm the engine's format cache. Warm: auxiliary files from a previous
  converged build present. Cold is primary; warm is reported only for incremental stretch work.
- **Isolation.** One container per repetition, CPU pinned, no concurrent measurement.
- **Determinism.** `SOURCE_DATE_EPOCH` and `FORCE_SOURCE_DATE` set for every run. Omitting them
  has already produced a spurious "output differs" result during preparatory work; this is a
  correctness control, not hygiene.

## Reporting rules

1. **Per document, always. No corpus-wide mean.** A mean over a benchmark corpus measures the
   corpus composition and can be moved arbitrarily by adding simple documents.
2. **Report losses as prominently as wins.** The realistic document is expected to show no
   saving. It appears in the same table, same font.
3. **Analysis overhead is shown, not absorbed.**
4. **Every number traces to a committed script** and a results file under `bench/results/`.
5. **Distributions, not point estimates**, for any timing claim.

## Experiments that would be misleading

Listed so they are not run by accident.

1. Reporting a mean speed-up across the corpus. Meaningless and gameable.
2. Comparing only against the fixed schedule. That is a straw man; baseline C must appear in
   every table.
3. Counting the missing-table-of-contents case as a win over baseline C. Baseline C handles it
   correctly; only baseline B fails.
4. Quoting wall-clock differences on documents where predicted equals ground truth. Measured
   differences there are noise.
5. Any output comparison without deterministic timestamps.
6. Claiming a dead-file-elimination benefit on a corpus containing no unreachable files. The
   corpus must contain them or the claim is dropped.
7. Tuning the benign-cycle bound until it matches the corpus. That is fitting to the test set.

## Threats to validity

- **Corpus size.** Ten documents, mostly synthetic. Findings are illustrative of mechanisms, not
  statistically representative of real-world documents.
- **Single machine.** Timing is not portable.
- **Synthetic non-convergence.** The amplifying case is a known constructed example, not one
  observed in the wild.
- **Assumption A2.** Its violations are precisely what prediction misses measure, so the
  evaluation can detect them but cannot rule them out in general.
- **Author bias.** The expectations file is written before implementation specifically to reduce
  the temptation to back-fill it from program output.
