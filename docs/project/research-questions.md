---
title: "Research questions"
parent: "Project"
nav_order: 2
---

# Research questions

Revised after the prior-art audit of 2026-08-27. Two of the four original hypotheses were falsified
by the audit before any measurement was taken; they are recorded here as struck rather than deleted,
because the reason they were wrong is more useful than the fact that they were.

Evidence for every claim of prior art in this document is in
[`research/sources/`](https://github.com/upayanmazumder/auxflow/tree/main/research/sources/), indexed by
[`research/prior-art-log.md`](https://github.com/upayanmazumder/auxflow/blob/main/research/prior-art-log.md), and summarised in
[RELATED-WORK.md](/project/related-work.html).

## Primary

> **RQ0.** For a declared subset of LaTeX, can a static influence analysis over an instance-level
> graph of auxiliary fact instances decide whether the preconditions of classical fixed-graph
> fixpoint theory hold for a document — and for which published non-convergence mechanisms does that
> decision succeed, for which does it fail, and how does it compare against the convergence oracles
> deployed in current tools?

Three parts, deliberately. The *decision* half is the only place a contribution can live, and even
there it is contingent (see G1 in [RELATED-WORK.md](/project/related-work.html) section 12). The *mechanism
coverage* half is the part the audit showed to be genuinely unoccupied. The *comparison* half is
what makes the whole thing measurable.

**What changed.** The previous RQ0 asked whether static analysis could "distinguish convergent from
potentially non-convergent compilations, and bound the required number of engine runs". Both halves
are anticipated: bounding rounds from graph structure is Hecht and Ullman 1975 and Bochmann 1976;
classifying cycles by a semantic property of the circulating values is Farrow 1986 and, for the
content-generating case specifically, Krishnan and Van Wyk 2012. The surviving question is narrower
and is framed in the vocabulary of the prior work rather than around it.

## Secondary

**RQ1 — mechanism coverage.** For each published mechanism of LaTeX non-convergence, does a
dependency-based static criterion over the declared subset detect it?

*Why it matters:* this is contribution G3 and it is the least contingent thing the project has. The
nine mechanisms are enumerated in [RELATED-WORK.md](/project/related-work.html) section 7.3. Four of them (M3,
M4, M6, M7) are **known in advance** to be undetectable by AuxFlow's criterion, because they are
cycles through the `.value` component that [IR.md](/reference/ir.html)'s `exists`/`value` split severs by
construction.

*Testable by:* one corpus member per mechanism, with the expected classification hand-written before
implementation, including the four expected false negatives. A run that reproduces the predicted
coverage table is the result; a run that does not is a more interesting result.

*Falsified if:* the coverage table cannot be predicted in advance, i.e. the analysis fails in ways
the model does not anticipate.

**RQ2 — oracle disagreement.** How do the five deployed convergence oracles differ in verdict, in
soundness direction, and in executions consumed?

The oracles, all sourced from manuals and source code, are: the engine's own rerun warning;
consecutive-run output checksum comparison (`latexmk`, ConTeXt); consecutive-run *input* comparison
(latexrun); same-run read-then-written comparison (Tectonic); and layout-iteration hash comparison
(Typst).

*Why it matters:* this is contribution G2 and nothing comparable was found in the literature. It is
also cheap.

*Testable by:* verdict and executions-to-certify per oracle per corpus member, against ground truth.
Specific expectations, each with a sourced reason to expect it:
- The engine warning has **false negatives** on documents whose generated lists change without any
  reference changing. `rerunfilecheck`'s own documentation states the gap.
- The engine warning has **false positives** on documents with active characters in captions or
  section names. `labelschanged`'s documentation states this.
- Output-comparison detectors consume one execution beyond the last productive one.
- Input-comparison and read-then-written detectors do **not**. This is the correction to the
  falsified H3.

**RQ3 — where the abstraction breaks, and how visibly.** Assumption A2 states that resolving a
reference does not alter pagination. A2 is false. On which documents does its failure change the
*verdict* rather than merely the predicted count?

*Why it matters:* A2 is the load-bearing unsound assumption. The audit established that it fails for
a published class, so the interesting question is no longer *whether* it fails but whether its
failure is detectable from the outside.

*Testable by:* prediction misses and misclassifications recorded by the executor, per document. Each
is a located instance of A2 failing. The four expected false negatives from RQ1 are the primary
cases.

**RQ4 — prediction accuracy against ground truth.** For documents the analysis classifies as
bounded, how does the computed bound compare to the experimentally determined run count?

*Testable by:* predicted minus *N\**, separated into over- and under-prediction, per document. No
minimality is claimed: minimum-pass assignment is NP-complete (Räihä and Ukkonen 1981), so an
over-prediction is expected behaviour and not a defect.

**RQ5 — precision versus verification cost.** What does static analysis plus runtime verification
cost relative to dynamic detection alone, and relative to the best dynamic detector rather than the
worst?

*Why it revised:* the previous form compared against baseline C only. Since latexrun and Tectonic
already avoid the redundant execution, comparing only against output-comparison would be a strawman.

*Testable by:* executions and wall clock for the full baseline set across the corpus, with analysis
latency reported separately and never netted out.

**RQ6 — diagnostic value relative to what already ships.** For a document that does not converge,
what does AuxFlow report that Typst, `labelschanged` and Tectonic do not?

*Why it matters:* the audit found that naming the offending facts is anticipated at least six times,
and that Typst ships byte spans and per-iteration value histories today. The only remaining
differences are that AuxFlow reports a *dependency chain* and reports it *without executing*. Both
must be demonstrated, not asserted.

*Testable by:* side-by-side diagnostic output on the amplifying corpus member, with executions
consumed recorded for each tool. Expected: zero for AuxFlow, five for Typst (it always runs five
iterations), the cap for `latexmk`.

## Variables

**Independent.** Document shape and which non-convergence mechanism it isolates;
convergence-detection mechanism; presence and type of feedback; whether the document conforms to the
declared subset.

**Dependent.** Classification label; mechanism-coverage outcome (detected / expected false negative
/ unexpected false negative); predicted run count; ground-truth run count *N\**; prediction error;
executions to certify; unnecessary executions; static analysis latency; graph size (facts, edges,
components, taint-set size); diagnosis content and diagnosis latency; end-to-end wall clock.

**Controlled.** Container image digest; engine version; deterministic timestamp variables
(`SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE` — a correctness control, not hygiene: the `latexmk` manual
documents an unbounded rerun loop caused by a generated file carrying its own creation time); engine
flags; CPU pinning; repetition count; working-directory hygiene between runs; the normalisation
exclusion list.

## Hypotheses

Restated. The full statements live in [PROJECT.md](/project/specification.html); the mapping and the audit outcome
are here.

| Hypothesis | Question | Primary metric | Audit status |
|---|---|---|---|
| **H1′** For documents in the declared subset whose instability arises from a *modelled* mechanism, the classifier separates benign from amplifying feedback with no false negatives; for the four unmodelled mechanisms it produces false negatives, and the corpus contains one of each | RQ1 | mechanism-coverage table | **restated.** The original "zero false negatives" form is falsified in advance by M3, M4, M6 and M7 |
| **H2** For documents acyclic after abstraction, the computed bound is at least the ground-truth run count | RQ4 | prediction error against *N\** | unchanged, and still the most likely to fail |
| ~~**H3** Static classification certifies a run count using strictly fewer executions than any consecutive-state comparison detector, the gap being exactly one~~ | ~~RQ2~~ | — | **FALSIFIED by the audit.** latexrun compares tool *inputs* and Tectonic compares files the engine read and then rewrote *within* one run; both reach *N*, not *N+1*. latexrun's README states AuxFlow's own argument and then engineers around it |
| **H3′** The one-execution gap is a property of *output*-comparison detectors specifically, and is observed for `latexmk` and ConTeXt but not for latexrun or Tectonic | RQ2 | executions to certify, per oracle | **new**, and now the honest form |
| ~~**H4** For non-convergent documents, AuxFlow reports the responsible facts whereas dynamic tools report only after exhausting a retry cap~~ | ~~RQ6~~ | — | **FALSIFIED in its second half.** Typst reports the fact, a byte span and the full per-iteration value history; `labelschanged` reports the offending label instances with before and after values; Tectonic names the file |
| **H4′** AuxFlow reports a *dependency chain* rather than an endpoint, and does so having performed zero engine executions | RQ6 | diagnosis content and executions consumed before a cause is reported | **new** |

All four surviving hypotheses are falsifiable. H2 in particular may fail; see [SCOPE.md](https://github.com/upayanmazumder/auxflow/blob/main/docs/SCOPE.md)
and [EVALUATION.md](/evaluation/methodology.html) for why that is a result rather than a failure.

## What would falsify the project's premise

Stated so that a negative outcome is recognisable rather than explained away.

- **The classifier cannot separate benign from amplifying feedback among the modelled mechanisms.**
  If the table-of-contents document is classified amplifying, or Gaspar's loop document is not, the
  central contribution does not work. Checked at gate 1.
- **The unmodelled mechanisms cannot be predicted in advance.** If M3, M4, M6 or M7 produce
  classifications other than the ones this document predicts, the model is not merely incomplete but
  wrong about its own incompleteness. That is worse than a false negative.
- **Prediction is systematically wrong.** If certified bounds routinely fall below ground truth,
  assumption A2 is too weak to support the analysis and the guarantee must be withdrawn.
- **The classification carries no useful information.** If every realistic document lands in
  `UNKNOWN`, the subset is too narrow to be interesting even if everything works as specified.
- **The oracles do not disagree.** If all five deployed oracles agree on every corpus member, G2
  collapses and one of the three surviving contributions is gone. The `rerunfilecheck` and
  `labelschanged` documentation both predict disagreement, so this is unlikely — but it is the
  falsification condition and it must be stated.
- **Krishnan and Van Wyk 2012 or Söderberg and Hedin 2013, read in full, already provide G1.** This
  is a literature risk rather than an experimental one, and it is the highest-priority thing to
  resolve. If either does, the project retains G2 and G3 and must be repositioned again.

Any of these is a reportable result. None is a reason to adjust the methodology after seeing the
data.

## Questions the audit closed

Recorded so they are not re-asked.

- *Does any existing tool statically derive the number of engine runs for a document?* **No.**
  SOURCED negative, six recorded web queries plus arXiv and DBLP, ~70 sources examined.
- *Does any existing tool report a cause when a build fails to converge?* **Yes** — Typst,
  `labelschanged` and Tectonic. **No** — `latexmk` and ConTeXt, which report only that a cap was
  reached.
- *Is dynamic detection necessarily one execution behind?* **No.** latexrun and Tectonic are not.
- *Is the static-versus-dynamic dependency gap already studied?* **Yes, emphatically.** It is the
  organising axis of Mokhov, Mitchell and Peyton Jones, ICFP 2018.
- *Is deriving an iteration count from graph structure novel?* **No.** Hecht and Ullman 1975;
  Bochmann 1976; and a granted, active US patent.
- *Is the observation that non-convergence is undecidable novel?* **No.** It is in `latexmk`'s
  shipped source and is proved via Rice's theorem in Mädje's 2022 thesis.
