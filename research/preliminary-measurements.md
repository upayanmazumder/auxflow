# Preliminary measurements

Observations taken during project scoping, before this repository existed.

> **These numbers are not reproducible as recorded and must not be cited.** They were taken in a
> locally available container image containing a TeX distribution, a bibliography tool and a
> spell checker. The image was not pinned, not published, and is not identified here because
> identifying it would not make the results reproducible. `latexmk` was **not installed**, so
> the state-comparison baseline was never timed.
>
> They are recorded because they motivated specific design decisions, and because the
> *qualitative* findings are what the corpus is built to re-test. Every one must be reproduced
> under the protocol in [../docs/EVALUATION.md](../docs/EVALUATION.md) before appearing in a
> report.

Documents were synthetic, roughly corresponding to corpus members `b01`–`b10`. The final corpus
differs, so the numbers will differ too.

---

## M1 — Three oracles disagree

`MEASURED`. For each document: the smallest run count producing output byte-identical to a
six-run reference (`TRUE`), what the engine's rerun warning reported (`WARN`), and what
normalised state comparison reported (`STATE`).

| document shape | TRUE | WARN | STATE |
|---|---|---|---|
| plain, no references | 1 | 1 | **2** |
| backward reference | 2 | 2 | 2 |
| forward reference | 2 | 2 | 2 |
| table of contents, 40 sections | **3** | **1** | 3 |
| contents + bibliography + page references | **4** | 4 | 4 |
| long table | 2 | 2 | 2 |
| deep reference cascade | 3 | 3 | 3 |
| multi-chapter document | 3 | 3 | 3 |
| loop bounded by a page reference | none within 6 | 6 | 6 |

**Findings that drove the design:**

- The engine's warning **under-detects**: it reported 1 for a document needing 3. Section E1
  below confirms the consequence. This is why runtime verification uses state comparison
  ([../docs/RUNTIME-VERIFICATION.md](../docs/RUNTIME-VERIFICATION.md)) and why engine warnings
  are retained only as an evaluation baseline.
- State comparison **over-detects** on the trivial case: it reported 2 where 1 sufficed, because
  it must observe one unchanged transition before it can certify. This is the structural
  one-execution gap the project measures.
- The conventional fixed schedule performs three runs, so it **under-provisions** the
  bibliography document (which needed four) and **over-provisions** the plain one (which needed
  one). Fixed schedules are wrong in both directions.

## E1 — The engine warning is unsound

`MEASURED`. Table-of-contents document, one run:

```
rerun signal present after pass 1 : NO
toc file written in pass 1        : 41 lines
state fixpoint reached after      : 3 passes
pass-1 output vs converged output : DIFFERENT (35806 vs 37489 bytes)
```

The engine reported nothing to do while the output was missing its entire table of contents.
This is a documented limitation rather than a defect — base LaTeX warns when *references* have
changed, not when generated lists have — and the existence of a package written specifically to
add checksum detection is independent confirmation.

Re-test as corpus member `b05`.

## E3 — Byte comparison is too strict for ground truth

`MEASURED`. For the bibliography document, a three-run build produced a PDF differing from the
converged one (48733 vs 48736 bytes), but a direct comparison of the auxiliary files showed
**zero differing label records**. The difference was internal document structure, not content.

This is why ground truth is defined by normalised auxiliary state plus extracted text, and why
byte equality is reported only as a secondary column
([../docs/EVALUATION.md](../docs/EVALUATION.md)).

An earlier attempt to demonstrate an incorrect fixed-schedule output produced a false positive
that was traced to non-deterministic timestamps. Deterministic timestamp variables are
consequently mandatory for every comparison, as a correctness control rather than as hygiene.

## M2 — Where a saving would come from, and where it would not

`MEASURED`. Fixed schedule against a minimal plan, single repetition each, unpinned environment.
**Treat as directional only** — subsequent single-shot repeats varied by more than ten percent.

| document shape | fixed | minimal | difference |
|---|---|---|---|
| plain | 261 ms | 127 ms | +51% |
| backward reference | 282 ms | 187 ms | +33% |
| long table | 255 ms | 192 ms | +24% |
| contents + bibliography | 513 ms | 410 ms | +20% |
| forward reference | 297 ms | 272 ms | +8% |
| table of contents | 425 ms | 454 ms | −6% |
| deep cascade | 350 ms | 378 ms | −8% |
| multi-chapter document | 731 ms | 830 ms | −13% |

**The finding that matters, and it is unfavourable:** any saving is concentrated on documents
requiring fewer than three runs. Where the true requirement equals the conventional three, there
is no saving and the differences are within noise. On the most realistic document the measured
difference was negative.

Two consequences for this project:

1. **No performance improvement is claimed anywhere.** The evaluation measures whether one
   exists; preliminary evidence suggests it concentrates where it is least valuable, on
   documents that were already cheap.
2. The contribution is positioned as **classification and diagnosis**, not speed.

A third observation: the corpus contained no unreachable files, so dead-file elimination had
nothing to eliminate and was never measured. The final corpus must include them or the claim is
dropped.

## Reproduction requirements

Before any of the above is used:

1. Pin a public container image by digest; ensure `latexmk` is present.
2. Author the corpus in `bench/corpus/` with hand-written expectations.
3. Ten or more repetitions; report median, p95 and interquartile range.
4. Ground truth per the adopted criterion, not byte equality.
5. Commit the harness output; regenerate every table from it.
