# Future infrastructure

**Nothing in this document is implemented, and nothing in it is required.** It is recorded so
that the design is on file and so that the reasoning about *why it is not being built now* is
explicit rather than forgotten.

> **The compiler is complete without any of this.** Delete this document and the project loses
> nothing gradeable. That property is enforced by the layering in
> [ARCHITECTURE.md](ARCHITECTURE.md): the build plan is serialisable JSON, so distribution is a
> deployment question rather than a compiler question.

## Why it is deferred

1. **It is not the contribution.** The research question concerns what static analysis can
   determine. Distributing the resulting work does not bear on that.
2. **It has the worst effort-to-value ratio in the project.** Cluster work consumes time in
   configuration rather than in anything defensible.
3. **It is the failure mode that sinks comparable projects.** Infrastructure is visible and
   satisfying to build, and it displaces the analysis work that is actually being assessed.
4. **The economics are unproven.** Distribution pays off when per-item cost varies widely.
   Preliminary observation suggests the spread across the corpus is modest, and the expensive
   documents are precisely the ones the analysis cannot speed up.

## Sketch

```
   document source
         |
         v
   AuxFlow compiler          static analysis, classification, build plan
         |
         v
   work item = { source reference, BuildPlan, classification }
         |
         v
   execution queue
         |
         v
   worker pool                each worker executes one plan with verification
         |
         v
   optional container orchestration
         |
         v
   optional event-driven scaling on queue state
```

The only compiler-derived information crossing into this layer is the build plan and the
classification. That is deliberate: it keeps the interface narrow and serialisable.

## Stretch levels

### S1 — distributed execution

Independent documents execute concurrently. The compiler is unchanged; the plan is already the
unit of work.

*What is compiler-derived:* the plan itself.
*Value:* modest. Independent documents are embarrassingly parallel and this demonstrates nothing
about the analysis.

### S2 — classification-derived routing

Attach the classification to the work item and route on it: documents classified as potentially
non-convergent go to a bounded lane, or are rejected before consuming a worker; unknown-classified
documents are given a longer cap.

*What is compiler-derived:* the convergence classification, and the derived run count.

*Value:* this is the only level where the compiler's output does something a queue could not
work out for itself. It is also more defensible than attaching a predicted cost, because a
classification is a structural statement rather than a performance prediction — and because cost
prediction from content is patent-encumbered ground (see [PATENT-NOTES.md](PATENT-NOTES.md)).

### S3 — event-driven scaling

Scale the worker pool on queue state.

*What is compiler-derived:* optionally, an aggregate over predicted run counts rather than a raw
item count.

*Value:* low, and contingent on cost variance that has not been demonstrated.

*Known constraint:* the obvious off-the-shelf mechanisms scale the **number** of workers, not
the resources given to each. Per-item resource sizing would require a different mechanism
entirely and is out of scope. This is noted because it is the first thing someone assumes is
possible.

*Known trap:* if an aggregate metric is used, the scaling target must be configured to treat it
as a total rather than a per-worker average, or the controller will silently divide it by the
worker count.

## Explicitly excluded, permanently

| Excluded | Reason |
|---|---|
| A custom cluster scheduler | Multi-year; off-the-shelf mechanisms suffice |
| A custom controller or operator | Same |
| Per-item resource sizing | Not supported by the intended mechanism |
| Production-grade orchestration, authentication, multi-tenancy | Not the contribution |
| Any of this before the benchmark harness is complete and measured | The failure mode described above |

## Preconditions

None of S1–S3 may be started until item 14 of [SCOPE.md](SCOPE.md) — the measurement harness —
is complete and a full evaluation has been run. If that condition is not met, this document
stays unimplemented, which is the expected outcome.
