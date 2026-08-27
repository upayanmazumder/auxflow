# Research questions

## Primary

> **RQ0.** Can a static, instance-level dependency analysis of a document's cross-reference
> structure distinguish convergent from potentially non-convergent compilations, and bound the
> required number of engine runs, before any execution — and how does the resulting
> classification compare, in accuracy and in executions consumed, against dynamic convergence
> detection?

Two halves, deliberately. The *classification* half is the contribution; the *comparison* half
is what makes it measurable rather than a matter of opinion.

## Secondary

**RQ1 — unnecessary executions.** How many engine executions does each convergence-detection
mechanism consume beyond the ground-truth requirement, and is the predicted one-execution gap
for consecutive-state comparison observed in practice?

*Testable by:* executions-to-certify per baseline against *N\**. The gap for baseline C should be
exactly one, and is most visible on the document with no auxiliary facts at all.

**RQ2 — diagnostic latency.** For a document whose cross-reference structure may not converge,
how many executions are performed before a tool reports the cause?

*Testable by:* executions before a cause is reported, on the amplifying document. Expected: zero
for static analysis, at least the retry cap for dynamic tools. The interesting part is not the
count but whether a *cause* is reported at all.

**RQ3 — static versus dynamic information content.** What can each mechanism know, and when?
Specifically, is engine-warning detection unsound on documents whose generated state changes
without any reference changing?

*Testable by:* comparing baseline B against ground truth on the table-of-contents document.
A single counterexample settles it, and one is expected.

**RQ4 — behaviour across dependency structures.** How do prediction accuracy and classification
vary with the structure present — plain, backward, forward, chained, generated-state, external
tool, multiple lists, amplifying, opaque?

*Testable by:* per-document prediction error and classification against expectation. This is the
question the corpus is designed around; each document isolates one structure.

**RQ5 — precision versus verification cost.** What is the trade-off between static precision and
the runtime verification needed to compensate for imprecision? Does combining them (baseline E)
cost more than dynamic detection alone (baseline C)?

*Testable by:* executions and wall clock for D, C and E across the corpus, with analysis latency
reported separately.

**RQ6 — where the abstraction breaks.** Assumption A2 states that resolving a reference does not
alter pagination. On which documents does it fail, and how is the failure visible?

*Testable by:* prediction misses recorded by the executor. Each is a located instance of A2
failing. A null result here is informative; a positive result is more interesting.

## Variables

**Independent.** Document shape; convergence-detection mechanism (A–E); presence and type of
feedback cycle; whether the document conforms to the declared subset.

**Dependent.** Predicted run count; ground-truth run count; classification label; executions to
certify; unnecessary executions; static analysis latency; graph size (facts, edges, components,
taint-set size); classification false positives and false negatives; diagnosis latency;
end-to-end wall clock.

**Controlled.** Container image digest; engine version; deterministic timestamp variables;
engine flags; CPU pinning; repetition count; working-directory hygiene between runs; the
normalisation exclusion list.

## What would falsify the project's premise

Stated so that a negative outcome is recognisable rather than explained away.

- **The classifier cannot separate benign from amplifying feedback.** If the table-of-contents
  document is classified amplifying, or the loop document is not, the central contribution does
  not work. This is checked at gate 1, in week 6.
- **Prediction is systematically wrong.** If certified bounds routinely fall below ground truth,
  assumption A2 is too weak to support the analysis and the guarantee must be withdrawn.
- **The classification carries no useful information.** If every realistic document lands in
  `UNKNOWN`, the subset is too narrow to be interesting, even if everything works as specified.

Any of these is a reportable result. None is a reason to adjust the methodology after seeing the
data.

## Relationship to the hypotheses

| Hypothesis | Question | Primary metric |
|---|---|---|
| H1 classification | RQ0, RQ4 | false negatives on the corpus |
| H2 bound | RQ0, RQ6 | prediction error against *N\** |
| H3 execution economy | RQ1, RQ5 | executions to certify |
| H4 diagnosis latency | RQ2 | executions before a cause is reported |

Full hypothesis statements in [PROJECT.md](PROJECT.md).
