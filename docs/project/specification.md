---
title: "Specification"
parent: "Project"
nav_order: 1
---

# AuxFlow — Project Specification

Authoritative specification. Where any other document in this repository conflicts with this
one, this one governs.

**Revised 2026-08-27 after a prior-art audit.** The audit falsified two hypotheses and removed five
claimed contributions. Its findings govern this document; the evidence is in
[`research/sources/`](../research/sources/) and the analysis in
[RELATED-WORK.md](RELATED-WORK.md). Anything in this repository that still reads as though the audit
had not happened is a defect.

## Title

**AuxFlow: A Static Applicability Test for Fixpoint Convergence in Multi-Pass Document Compilation**

Report subtitle: *An instance-level auxiliary-fact dependency analysis that decides, before the
first engine execution, whether classical fixed-graph fixpoint reasoning applies to a document — with
a taxonomy of the non-convergence mechanisms it cannot see.*

The previous title, "Static Convergence Classification for Multi-Pass Document Compilation", was
retired because "convergence classification" is Farrow 1986 and the unqualified form implies a
completeness the analysis provably does not have.

## Abstract

Multi-pass document compilers resolve cross-references through an auxiliary-file fixpoint: each
engine run reads the auxiliary state written by the previous run. The number of runs required is
therefore a property of the document's cross-reference structure, but in current practice it is
discovered only dynamically. Five widely deployed systems each use a different convergence oracle
and each caps iteration with a hand-chosen constant — `latexmk` 5, Tectonic 6, ConTeXt 9, Typst 5,
`llmk` 5 — and none derives the number from the source. When the cap is reached, two of the five
report no cause at all.

AuxFlow investigates what can instead be determined statically. It implements a conventional
compiler front end over a declared LaTeX subset — a category-code lexer, a recursive-descent parser,
a multi-file AST and six symbol tables — and lowers the result to the Auxiliary Reference Graph
(ARG), an intermediate representation whose nodes are individual auxiliary fact instances and whose
edges carry a *pass lag*: a fact written during run *p* is first readable during run *p+1*. A
monotone dataflow analysis over the ARG assigns each fact a stable pass number; Tarjan's algorithm
identifies strongly connected components; and an influence analysis classifies each feedback edge by
whether the fact value it carries can reach a construct governing the quantity of generated content.

**The machinery is established prior art and is transplanted, not claimed.** Static pass numbering
is Bochmann 1976 and Alblas 1981; bounding fixpoint rounds by a structural graph parameter is Hecht
and Ullman 1975; SCC partition plus per-component fixpoint over the condensation is Jones 1990;
static analysis of circular dependency graphs with a well-definedness obligation is Farrow 1986; and
the fixed-rate versus data-dependent-rate schedulability line is Lee and Messerschmitt 1987. What
the classical work does not cover is a setting in which the dependency graph is **not invariant under
iteration**, because a fact value can change how many fact instances exist. AuxFlow's classification
is best understood as a test of whether the classical fixed-graph fixpoint theory applies to a
document at all — a sufficient condition for the finite-height half of the convergence obligation
that Farrow allocates and that Magnusson and Hedin 2007 state, in writing, that nobody checks.

The analysis is provably incomplete: four published non-convergence mechanisms are cycles through
the value component that the ARG's abstraction severs by construction, and AuxFlow cannot see them.
That incompleteness is declared, given corpus members, and measured.

The system is evaluated against the deployed convergence oracles on a benchmark corpus, using
normalised auxiliary-state equivalence as ground truth, with per-document results including the
cases where static analysis provides no benefit and the cases where it is wrong.

## Problem statement

Given a document source *D* for a multi-pass compilation pipeline, determine before any execution:

1. whether the preconditions under which the auxiliary-state fixpoint for *D* is guaranteed to exist
   can be established;
2. if so, an upper bound on the number of engine runs required to reach it;
3. if not, or if this cannot be decided, which specific cross-reference structures are responsible,
   named with source locations.

No existing tool answers (1) or (2) without executing. Three of five deployed tools answer (3) after
executing — Typst with a source span and a per-iteration value history, `labelschanged` with the
offending label instances, Tectonic with the file name. `latexmk` and ConTeXt answer it not at all.
AuxFlow's difference is the absence of execution, and a dependency chain rather than an endpoint.

## Motivation

1. **Every deployed system caps iteration with a magic number and none derives it.** `latexmk`
   `$max_repeat = 5`; Tectonic `DEFAULT_MAX_TEX_PASSES = 6`; ConTeXt `multipass_nofruns = 9`, with
   the source comment `-- better for tracing oscillation`; Typst `MAX_ITERS = 5`; `llmk`
   `max_repeat = 5`. Five independent implementations, five constants, no analysis. This is the
   best-evidenced motivation the project has.
2. **Fixed schedules are wrong in both directions.** The conventional sequence over-provisions
   simple documents and under-provisions ordinary ones. A document combining a table of contents, a
   bibliography and page references can require four engine runs where the conventional schedule
   performs three.
3. **The engine's rerun warning is unsound in both directions.** It has false negatives —
   `rerunfilecheck`'s own documentation states that base LaTeX's warnings "are not given for the
   table of contents and other data stored in the aux files" — and false positives, since
   `labelschanged`'s documentation records active characters in captions as a cause of spurious
   "may have changed" warnings. Baseline B exists to measure both directions.
4. **The oracles deployed in practice disagree, and nothing characterises how.** Engine warning;
   consecutive-run output checksum (`latexmk`, ConTeXt); consecutive-run *input* comparison
   (latexrun); same-run read-then-written comparison (Tectonic); layout-iteration hash (Typst). No
   published comparison of their agreement, soundness direction, or cost was located.
5. **Non-convergence is real, has several distinct mechanisms, and is undiagnosed as a class.** A
   published one-page counterexample diverges monotonically (Gaspar, *TUGboat* 35:1, 2014); the TeX
   FAQ documents a case that oscillates with period two; a Stack Exchange thread supplies
   counterexamples with no loop and no conditional at all. Nine distinct mechanisms are enumerated in
   [RELATED-WORK.md](RELATED-WORK.md) section 7.3. Nobody has systematised them.

**A previously stated motivation has been withdrawn.** "Dynamic detection costs an execution" is
true only of output-comparison detectors. latexrun compares tool *inputs* and states the argument
explicitly before engineering around it; Tectonic compares files the engine read and then rewrote
within a single run. Both reach *N*, not *N+1*.

Preliminary measurements are recorded in
[`research/preliminary-measurements.md`](../research/preliminary-measurements.md). They were taken
in an unpinned environment and must be reproduced under [docs/EVALUATION.md](EVALUATION.md) before
appearing in any report. Prior-art evidence is in
[`research/sources/`](../research/sources/) and [RELATED-WORK.md](RELATED-WORK.md).

## Research question

> For a declared subset of LaTeX, can a static influence analysis over an instance-level graph of
> auxiliary fact instances decide whether the preconditions of classical fixed-graph fixpoint theory
> hold for a document — and for which published non-convergence mechanisms does that decision
> succeed, for which does it fail, and how does it compare against the convergence oracles deployed
> in current tools?

Secondary questions in [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md).

## Hypotheses

Revised after the prior-art audit. Two of the original four were falsified by the audit before any
measurement was taken; they are recorded as struck in
[RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md) rather than deleted.

- **H1′ (classification, restated).** For documents in the declared subset whose instability arises
  from a *modelled* mechanism, structural analysis of the auxiliary-fact graph distinguishes
  potentially non-convergent documents from benignly cyclic ones with no false negatives. The
  three declared extent-feedback failures (M3, M4 and M6) are measured in `b11`–`b13`.
  Footnote feedback (M7) and `biblatex` citation feedback (M5) are covered as `UNKNOWN`
  fallbacks in `b07` and `b15`. Nondeterministic generated state (M8) is out of model
  and covered by `b10`.
- **H2 (bound).** For documents that are acyclic after abstraction, the statically computed
  stable-pass bound is at least the experimentally determined ground-truth run count. No minimality
  is claimed: minimum-pass assignment is NP-complete (Räihä and Ukkonen, *SIAM J. Comput.*, 1981).
- **H3′ (execution economy, restated).** The one-execution gap is a property of *output*-comparison
  detectors specifically. It is observed for `latexmk` and ConTeXt and is **not** observed for
  latexrun or Tectonic.
- **H4′ (diagnosis form, restated).** For non-convergent documents AuxFlow reports a dependency
  *chain* with source spans having performed zero engine executions, whereas the tools that do
  report a cause report an endpoint and do so only after executing.

All four are falsifiable. H2 in particular may fail; see [SCOPE.md](SCOPE.md) and
[EVALUATION.md](EVALUATION.md) for why that is a result rather than a failure.

## Objectives

- O1. A working compiler front end over the declared subset, with diagnostics and no engine
  execution.
- O2. The ARG as a documented, instance-level intermediate representation.
- O3. Two dataflow analyses: content-quantity influence propagation and stable-pass numbering.
- O4. A convergence classifier with actionable diagnostics naming a dependency chain.
- O5. A build planner and a plan executor with state-based verification.
- O6. A reproducible benchmark corpus and measurement harness covering every deployed oracle,
  including latexrun and Tectonic.
- O7. An honest evaluation, including negative results.
- O8. **A systematised taxonomy of LaTeX non-convergence mechanisms**, with a per-mechanism
  statement of whether a dependency-based static criterion detects it. Currently the only
  contribution with no located anticipation of any kind.
- O9. **A controlled comparison of the five deployed convergence oracles** — verdict, soundness
  direction, and executions consumed. Also unanticipated in the literature.
- O10. **An operational account of the declared subset's auxiliary round trip.** No formal semantics
  of TeX exists and Knuth disclaimed interest in one, so this definitional work is necessary and
  unclaimed.

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

Stated in three strengths. The full derivation, with the prior art each concession answers, is in
[RELATED-WORK.md](RELATED-WORK.md) section 13.

**Conservative — defensible now.** A declared subset of LaTeX with an operational account of its
auxiliary-state round trip; an instance-level dependency graph of auxiliary fact instances carrying
pass-lag edges; the application of established multipass and circular-attribute-grammar analyses to
it; a systematised mechanism taxonomy of LaTeX non-convergence stating which mechanisms a
dependency-based static criterion can and cannot detect; and a controlled comparison of the
convergence oracles deployed in current tools.

**Strong — only if the experiments validate it, and only after Krishnan and Van Wyk (SLE 2012) and
Söderberg and Hedin (SLE 2013) are read in full.** That a static influence analysis from auxiliary
fact values to constructs governing content quantity is a usable sufficient condition for the
finite-height precondition of circular-attribute-grammar fixpoint theory — that is, that it decides
statically whether classical fixed-graph fixpoint reasoning applies to a document at all — yielding a
pre-execution verdict with source-level attribution for the loop-bounded-by-a-reference class, and
demonstrably failing for the extent-driven class.

**Overclaim — must never appear.** The full list is in [RELATED-WORK.md](RELATED-WORK.md) section 13
and [PATENT-NOTES.md](PATENT-NOTES.md). The short form: AuxFlow did not invent static pass
numbering, SCC-plus-condensation fixpoint, iteration bounds from graph structure, cycle
classification, naming the offending facts, checksum verification, or the observation that
non-convergence is undecidable. It does not detect all non-convergent documents even within its
subset. Dynamic detection does not necessarily cost an extra execution. Existing tools do not all
fail to report a cause.

## Limitations

Stated up front because they constrain what may be claimed.

- **L1.** The analysis is defined only over the declared subset. Everything else produces an explicit
  unknown classification. This is not engineering convenience: circularity testing for *remote*
  reference attribute grammars is undecidable (Boyland, *JACM* 52(4), 2005), and LaTeX's
  `\ref`/`\pageref`/`\cite` are remote references. The subset is what makes the graph statically
  constructible at all.
- **L2.** The abstraction that resolving a reference does not alter pagination is *not faithful*.
  Substituting `17` for `??` can change a line break and therefore a page break. Without this
  abstraction every document collapses into one strongly connected component and the analysis is
  vacuous. The dichotomy is stated openly in [RELATED-WORK.md](RELATED-WORK.md) section 7.4: model
  extent feedback and be vacuous, or do not and be unsound for a named class. AuxFlow takes the
  second option.
- **L3.** A cycle classified as amplifying is a *necessary* structural condition for one class of
  known non-convergence, not a proof of divergence.
- **L3b.** **An ARG cycle is neither necessary nor sufficient for non-convergence.** Not sufficient
  is well known. Not necessary is the audit's sharpest adverse finding: four published mechanisms are
  non-convergent and produce no structural edge. Any claim of completeness within the subset is
  false.
- **L3c.** Divergence and oscillation are distinct failure modes with distinct causes — the first
  violates finite height, the second monotonicity — and a single amplifying label conflates them.
- **L4.** No minimality claim. Minimum-pass assignment is NP-complete; a computed bound may exceed
  the true requirement by design.
- **L5.** Package coverage is finite. An unmodelled package that writes auxiliary state will manifest
  as a prediction miss. The `biblatex` same-page citation feedback mechanism is safe only because it
  is unmodelled; modelling `biblatex` naively would introduce a false negative.
- **L6.** Nothing is claimed about engine termination.
- **L7.** Instance-level pass numbering is Alblas's *pure* multi-pass setting, and deciding pure
  multi-pass membership is of inherently exponential complexity (Engelfriet and Filè). AuxFlow
  computes a conservative approximation over a restricted subset and must say so.

## Open technical decisions

Decisions that materially affect research validity are listed as open. Decisions that are
obvious and low-risk have been made and are marked RESOLVED with a rationale.

| # | Decision | Status |
|---|---|---|
| D1 | Implementation language | **RESOLVED: Python 3.12+.** The interesting logic is hand-written either way; Python keeps the front end short, makes the harness easy, and has no bearing on the research claims. Core package takes no third-party dependencies — Tarjan and the fixpoint are written by hand as part of the project. |
| D2 | Parser architecture | **RESOLVED: hand-written recursive descent with one token of lookahead.** A parser generator would obscure category-code handling, which is the part with genuine subtlety. |
| D3 | AST representation | **RESOLVED: frozen dataclasses, one class per node kind, mandatory `Span` on every node.** Spans are load-bearing: the diagnostics in [NON-CONVERGENCE.md](NON-CONVERGENCE.md) are worthless without them. |
| D4 | Exact fact kind set | **OPEN.** A provisional set is given in [IR.md](IR.md). It will be revised once the corpus is authored, because fact kinds should be justified by documents that need them. Freeze before implementation phase 7. |
| D5 | Pass-lag semantics for external tools | **RESOLVED: TOOL-edge effective lag is 0 for stable-pass purposes.** The auxiliary round trip is lag 1, sourced from `ltfiles.dtx`: `\begin{document}` inputs the previous run's `.aux` before reopening it for writing. The `DepEdge.pass_lag` field on a `bibtex` edge stays 1 (bibtex genuinely needs the prior run's `.aux`), but `auxflow.analysis.stable_pass` treats a `TOOL` edge's lag as 0 in the stable_pass recurrence specifically. This is the only setting that reproduces [IR.md](IR.md)'s worked bibliography-cascade example (`BBL.exists` stable_pass 1, "external tool runs after run 1"); resolved while implementing phase 10's stable-pass numbering rather than by a separate experiment, since the worked example is itself the targeted case. |
| D6 | State equivalence definition | **RESOLVED: normalised auxiliary-state equality plus rendered-text equality, exclusion list `{\relax}`.** Implemented in `auxflow.runtime.normalize` (phase 13) and reused unchanged by the ground-truth sweep (`bench/harness/groundtruth_incontainer.py`) and by baselines B/C/C'/C'' (`bench/harness/normstate.py`), so every oracle in `docs/EVALUATION.md` shares one normalisation. `\relax` is excluded because the engine writes it as argument-free aux-file boilerplate with no state; every other record kind, including unrecognised ones, stays observable so a changing unknown record cannot look stable. Text equality is checked via `pdftotext -layout` to guard against auxiliary state settling before rendered output does, per `docs/EVALUATION.md`'s ground-truth definition. |
| D7 | Benign-cycle bound | **OPEN.** Whether a benign cycle can be assigned a finite bound at all, or should always be reported as unbounded and deferred to runtime verification. The conservative option is the fallback; do not tune a constant against the corpus. |
| D8 | Runtime verification strategy | **RESOLVED: normalised auxiliary-state comparison, never engine warnings.** See [RUNTIME-VERIFICATION.md](RUNTIME-VERIFICATION.md). |
| D9 | Benchmark harness form | **RESOLVED: Python harness emitting JSONL, plus shell baseline scripts.** Baselines must be readable shell so a reviewer can confirm exactly what was executed. |
| D10 | Containerised engine environment | **RESOLVED: `bench/Dockerfile`, `python:3.12-slim-bookworm` base pinned by digest.** TeX Live (including `latexmk`) from the Debian bookworm apt archive; `latexrun` pinned to one commit, Tectonic 0.15.0 and Typst 0.11.0 as pinned release binaries, `biber` for the `b15_ibid` cross-check, `labelschanged` built from its CTAN `.dtx`/`.ins` pair. `auxflow` itself is pip-installed into the image so baseline scripts and the ground-truth sweep share identical normalisation with the host (see D6). The built image's content digest is recorded in every `bench/results/*.jsonl` record. |
| D11 | Whether opaque constructs invalidate the whole document or only the containing file | **OPEN.** Per-file is more useful but requires arguing that opacity cannot leak across an inclusion boundary. Currently specified as whole-document (conservative). |
| **D12** | **Whether to split `AMPLIFYING` into a finite-height failure and a monotonicity failure** | **OPEN, added by the audit.** Gaspar's loop diverges monotonically (finite height fails); the width-driven and conditional cases oscillate with period two (monotonicity fails). The Magnusson and Hedin condition separates them, and so does synchronous dataflow's separation of rate inconsistency from deadlock. Splitting is a small, honest refinement; it also means the second class is largely undetectable, which is why it is a decision and not a foregone conclusion. |
| **D13** | **Whether the taint criterion is stated as "quantity of generated content" or as "any layout-determining measurement"** | **RESOLVED: narrow ("quantity of generated content").** The wide form makes every document containing one `\ref` a single strongly connected component, so the analysis would be vacuous. The narrow form is unsound for M3, M4 and M6 in `b11`–`b13`, recorded as declared false negatives. M7 appears in `b07` as an `UNKNOWN` fallback because footnote syntax remains outside the subset. The corpus measures both outcomes. There is no third option without modelling line breaking. Decision: accept the narrow criterion and declared incompleteness; do not attempt the wide form. |
| **D14** | **Whether the amplifying analysis may be claimed as a contribution at all** | **RESOLVED (split): yes, against Krishnan and Van Wyk; not claimed against Söderberg and Hedin.** Krishnan and Van Wyk (SLE 2012, DOI `10.1007/978-3-642-36089-3_4`) was read in full via Krishnan's PhD dissertation ("Composable Semantics Using Higher-Order Attribute Grammars", University of Minnesota, 2012, open access, `https://hdl.handle.net/11299/144010`, chapter 5), which is the source the SLE paper was drawn from. Their analysis operates at the **grammar level**: SCCs over a static non-terminal graph, proved terminating via a recursive path ordering on production symbols (term-rewriting theory). AuxFlow's taint analysis operates at the **instance level**: SCCs over a per-document value-dependency graph (the ARG), with taint propagated by reachability from control-construct reads to `CONTENT_VOLUME`. Different formal object (grammar specification vs. one document's fact graph) and different proof technique (rewrite-ordering vs. reachability). The differentiator in [RELATED-WORK.md](RELATED-WORK.md) section 3 survives against this paper. Söderberg and Hedin (SLE 2013, DOI `10.1007/978-3-319-02654-1_17`) remains **unread in full** — no open-access copy exists and institutional access was unavailable. No claim of novelty against that paper may appear in any report; it is recorded as an open risk (see RELATED-WORK.md section 3) rather than cleared. |

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
