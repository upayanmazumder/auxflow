# AuxFlow — Project Specification

Authoritative specification. Where any other document in this repository conflicts with this
one, this one governs.

## Title

**AuxFlow: Static Convergence Classification for Multi-Pass Document Compilation**

Report subtitle: *An instance-level auxiliary-fact dependency analysis that classifies
convergence behaviour and diagnoses non-convergent cross-reference structures before the first
engine execution.*

## Abstract

Multi-pass document compilers resolve cross-references through an auxiliary-file fixpoint: each
engine run reads the auxiliary state written by the previous run. The number of runs required is
therefore a property of the document's cross-reference structure, but in current practice it is
discovered only dynamically, by running the engine repeatedly and observing when the auxiliary
state stops changing. This is adequate for correctness but yields no information before
execution, and it is not free: a detector that certifies stability by comparing consecutive
states must perform one execution beyond the last one that changed anything.

AuxFlow investigates what can instead be determined statically. It implements a conventional
compiler front end over a declared LaTeX subset — a category-code lexer, a recursive-descent
parser, a multi-file AST and six symbol tables — and lowers the result to the Auxiliary
Reference Graph (ARG), an intermediate representation whose nodes are individual auxiliary fact
instances and whose edges carry a *pass lag*: a fact written during run *p* is first readable
during run *p+1*. A monotone dataflow analysis over the ARG assigns each fact a stable pass
number; Tarjan's algorithm identifies strongly connected components; and a taint analysis
classifies each feedback edge by whether the fact value it carries can influence the quantity of
generated content.

That last distinction is the technical core. Ordinary documents are structurally cyclic — a
table of contents occupies pages, which changes the page numbers recorded in the table of
contents — yet they converge. Documents in which a fact value controls content generation may
not converge at all. AuxFlow separates these two cases statically and reports the offending
facts and source locations for the second.

The system is evaluated against four dynamic convergence-detection mechanisms on a ten-document
benchmark corpus, using normalised auxiliary-state equivalence as ground truth, with per-document
results including the cases where static analysis provides no benefit.

## Problem statement

Given a document source *D* for a multi-pass compilation pipeline, determine before any
execution:

1. whether the auxiliary-state fixpoint for *D* exists;
2. if so, an upper bound on the number of engine runs required to reach it;
3. if not, or if this cannot be decided, which specific cross-reference structures are
   responsible.

Existing tooling answers (1) and (2) only by executing, and does not answer (3) — it reports
that a retry limit was exhausted, without attributing a cause.

## Motivation

1. **Fixed schedules are wrong in both directions.** The conventional sequence over-provisions
   simple documents and under-provisions ordinary ones. A document combining a table of
   contents, a bibliography and page references can require four engine runs where the
   conventional schedule performs three.
2. **The engine's rerun warning is not a sound completion oracle.** LaTeX warns when
   *references* have changed. It does not warn when a generated list changes. A build that stops
   when the engine stops complaining can emit a document missing its table of contents. The
   existence of the `rerunfilecheck` package is independent confirmation that base LaTeX's
   warning is insufficient.
3. **Dynamic detection costs an execution.** Certifying stability by comparing consecutive
   states requires observing one unchanged transition, hence one run beyond the last productive
   one. This is structural.
4. **Non-convergence is real and undiagnosed.** A published nine-line counterexample exists in
   which a cross-reference is wrong regardless of how many runs are performed (Gaspar, TUGboat
   35:1, 2014). Existing tools respond by exhausting a retry cap and reporting only that they
   gave up.

Preliminary measurements supporting points 1–3 are recorded in
[`research/preliminary-measurements.md`](../research/preliminary-measurements.md). They were
taken in an unpinned environment and must be reproduced under
[docs/EVALUATION.md](EVALUATION.md) before appearing in any report.

## Research question

> Can a static, instance-level dependency analysis of a document's cross-reference structure
> distinguish convergent from potentially non-convergent compilations, and bound the required
> number of engine runs, before any execution — and how does the resulting classification
> compare, in accuracy and in executions consumed, against dynamic convergence detection?

Secondary questions in [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md).

## Hypotheses

- **H1 (classification).** For documents in the declared subset, structural analysis of the
  auxiliary-fact graph distinguishes potentially non-convergent documents from benignly cyclic
  ones with zero false negatives on the benchmark corpus.
- **H2 (bound).** For documents that are acyclic after abstraction, the statically computed
  stable-pass bound equals the experimentally determined ground-truth run count.
- **H3 (execution economy).** Static classification certifies a document's run count using
  strictly fewer engine executions than any consecutive-state comparison detector, the gap being
  exactly one execution.
- **H4 (diagnosis latency).** For non-convergent documents, AuxFlow reports the responsible
  facts without executing the engine, whereas dynamic tools report only after exhausting a
  retry cap.

All four are falsifiable. H2 in particular may fail; see [SCOPE.md](SCOPE.md) and
[EVALUATION.md](EVALUATION.md) for why that is a result rather than a failure.

## Objectives

- O1. A working compiler front end over the declared subset, with diagnostics and no engine
  execution.
- O2. The ARG as a documented, instance-level intermediate representation.
- O3. Two dataflow analyses: content-quantity taint propagation and stable-pass numbering.
- O4. A four-state convergence classifier with actionable diagnostics.
- O5. A build planner and a plan executor with state-based verification.
- O6. A reproducible benchmark corpus and measurement harness covering five baselines.
- O7. An honest evaluation, including negative results.

## Scope

In scope: the compiler front end, the ARG, the two analyses, classification, build-plan
generation, plan execution with verification, the corpus and harness.

Out of scope: implementing TeX; macro expansion; supporting arbitrary real-world documents;
producing typeset output; beating existing tools on wall-clock time; machine learning; any
production system. Full boundary in [SCOPE.md](SCOPE.md).

## Non-goals

- **Not a replacement for existing build tools.** `latexmk` is correct and is used as a
  baseline, not as a target to defeat.
- **Not a performance project.** Measurement determines whether savings exist. Preliminary data
  suggests they concentrate on documents that are already cheap.
- **Not a TeX implementation.** The subset is declared and everything outside it degrades to an
  explicit unknown state.
- **Not an infrastructure project.** Distribution and autoscaling are stretch work and are cut
  first.

## Expected contribution

An instance-level intermediate representation for auxiliary-fact dependencies in multi-pass
document compilation, together with a static analysis that (a) assigns each fact a stable-pass
number by monotone fixpoint, (b) classifies each strongly connected component by whether the
fact values it carries can influence the quantity of generated content, and (c) uses that
classification to separate convergent, benignly cyclic and potentially non-convergent documents,
reporting the responsible facts and source locations for the last.

Minimal pass numbering itself is prior art and is explicitly transplanted, not claimed. The
contribution is the feedback classification that makes the transplant applicable to a
data-dependent domain, and the pre-execution diagnosis it enables. See
[RELATED-WORK.md](RELATED-WORK.md).

## Limitations

Stated up front because they constrain what may be claimed.

- **L1.** The analysis is defined only over the declared subset. Everything else produces an
  explicit unknown classification.
- **L2.** The abstraction that resolving a reference does not alter pagination is *not faithful*.
  Substituting `17` for `??` can change a line break and therefore a page break. Without this
  abstraction every document collapses into one strongly connected component and the analysis is
  vacuous. Its consequences are validated empirically, not proved.
- **L3.** A cycle classified as amplifying is a *necessary* structural condition for known
  non-convergence, not a proof of divergence.
- **L4.** No minimality claim. A computed bound may exceed the true requirement.
- **L5.** Package coverage is finite. An unmodelled package that writes auxiliary state will
  manifest as a prediction miss.
- **L6.** Nothing is claimed about engine termination.

## Open technical decisions

Decisions that materially affect research validity are listed as open. Decisions that are
obvious and low-risk have been made and are marked RESOLVED with a rationale.

| # | Decision | Status |
|---|---|---|
| D1 | Implementation language | **RESOLVED: Python 3.12+.** The interesting logic is hand-written either way; Python keeps the front end short, makes the harness easy, and has no bearing on the research claims. Core package takes no third-party dependencies — Tarjan and the fixpoint are written by hand as part of the project. |
| D2 | Parser architecture | **RESOLVED: hand-written recursive descent with one token of lookahead.** A parser generator would obscure category-code handling, which is the part with genuine subtlety. |
| D3 | AST representation | **RESOLVED: frozen dataclasses, one class per node kind, mandatory `Span` on every node.** Spans are load-bearing: the diagnostics in [NON-CONVERGENCE.md](NON-CONVERGENCE.md) are worthless without them. |
| D4 | Exact fact kind set | **OPEN.** A provisional set is given in [IR.md](IR.md). It will be revised once the corpus is authored, because fact kinds should be justified by documents that need them, not invented in advance. Freeze before implementation phase 7. |
| D5 | Pass-lag semantics for external tools | **OPEN.** The auxiliary round trip is lag 1. Whether a tool edge (`bibtex`) is best modelled as lag 1 from the run that produced its input, or as a separate scheduling node, affects predicted counts for bibliography documents. Resolve with a targeted experiment in phase 8. |
| D6 | State equivalence definition | **OPEN, leaning normalised auxiliary state.** PDF byte identity is measurably too strict; raw file equality is sensitive to ordering. See [EVALUATION.md](EVALUATION.md). Must be fixed before any ground truth is generated. |
| D7 | Benign-cycle bound | **OPEN.** Whether a benign cycle can be assigned a finite bound at all, or should always be reported as unbounded and deferred to runtime verification. The conservative option is the fallback; do not tune a constant against the corpus. |
| D8 | Runtime verification strategy | **RESOLVED: normalised auxiliary-state comparison, never engine warnings.** See [RUNTIME-VERIFICATION.md](RUNTIME-VERIFICATION.md). |
| D9 | Benchmark harness form | **RESOLVED: Python harness emitting JSONL, plus shell baseline scripts.** Baselines must be readable shell so a reviewer can confirm exactly what was executed. |
| D10 | Containerised engine environment | **OPEN.** A public TeX Live image must be selected and pinned by digest, and must contain `latexmk` so baseline C is measurable. |
| D11 | Whether opaque constructs invalidate the whole document or only the containing file | **OPEN.** Per-file is more useful but requires arguing that opacity cannot leak across an inclusion boundary. Currently specified as whole-document (conservative). |

## Engineering principles

1. Compiler first. Infrastructure never precedes analysis.
2. Static analysis must be explainable. Every classification names the facts responsible.
3. No unsupported claims. Every assertion is measured, cited, or labelled as an assumption.
4. No fabricated benchmarks. Numbers come from a committed script or they do not appear.
5. No premature infrastructure.
6. Every compiler phase has tests.
7. Unsupported constructs fail safely, never silently.
8. Prefer a smaller formal model that can be defended.
9. Reproducibility is a deliverable, not an afterthought.
10. Every research claim has evidence attached.
