# AuxFlow

A static applicability test for fixpoint convergence in multi-pass document compilation.

AuxFlow is a compiler and static analyser for a declared subset of LaTeX. It parses a document
into an instance-level dependency graph of auxiliary facts, computes when each fact stabilises,
and classifies the document's convergence behaviour before the typesetting engine runs once.

**Status: bootstrap / design phase. No compiler code has been written yet.** A prior-art audit was
completed on 2026-08-27; it falsified two hypotheses and removed five claimed contributions, and its
findings govern the specification. See [Current status](#current-status),
[docs/RELATED-WORK.md](docs/RELATED-WORK.md) and [research/sources/](research/sources/).

---

## What is AuxFlow?

Document compilers such as LaTeX are *multi-pass*: they resolve cross-references by writing
facts to auxiliary files and reading them back on the next run. A `\ref` cannot be resolved
until the corresponding `\label` has been recorded, which happens during a previous run. The
process iterates to a fixpoint.

How many runs a given document needs is a property of its cross-reference structure. In current
practice that property is discovered *dynamically*: run the engine, compare the auxiliary state
with the previous run's, repeat until nothing changes. AuxFlow asks a different question:

> How much of this can be determined statically, from the source alone?

AuxFlow is a conventional compiler front end (category-code lexer, recursive-descent parser,
multi-file AST, symbol tables) feeding a purpose-built intermediate representation and two
dataflow analyses. Its output is a classification, a build plan, and, for documents whose
cross-reference structure may never converge, a diagnosis naming the facts responsible.

## Problem

Three questions about a document *D* have no answer before execution:

1. Does the auxiliary-state fixpoint for *D* exist?
2. If so, how many engine runs are needed to reach it?
3. If not, which cross-reference structures are responsible?

Existing tooling answers (1) and (2) only by executing. It answers (3) unevenly: Typst names the
fact with a source span and a per-iteration value history, `labelschanged` names the offending label
instances, Tectonic names the file that changed, and `latexmk` and ConTeXt report only that a cap was
reached. All of them answer it *after* executing.

Four further observations motivate the work:

- **Fixed schedules are wrong in both directions.** The conventional `latex, bibtex, latex, latex`
  sequence over-provisions simple documents and under-provisions ordinary ones.
- **Every deployed system caps iteration with a hand-chosen constant and none derives it.**
  `latexmk` 5, Tectonic 6, ConTeXt 9, Typst 5, `llmk` 5. Five independent implementations, five
  magic numbers, no analysis.
- **The engine's own rerun warning is unsound in both directions.** It misses changes to generated
  lists (`rerunfilecheck`'s documentation states this in as many words), and it fires spuriously on
  active characters in captions, per `labelschanged`'s documentation.
- **The deployed convergence oracles disagree, and nothing characterises how.** Engine warning;
  consecutive-run output checksum; consecutive-run *input* comparison; same-run read-then-written
  comparison; layout-iteration hash. No published comparison was found.

One earlier motivation has been **withdrawn by the audit**: dynamic detection does *not* necessarily
cost an extra execution. That is true of output-comparison detectors only. latexrun compares tool
inputs, and Tectonic compares files the engine read and then rewrote within a single run; both reach
*N*, not *N+1*.

## Core idea

Lower the document to a graph whose nodes are *individual auxiliary fact instances* (this
label's page number, that table-of-contents entry) and whose edges carry a **pass lag**: a fact
written during run *p* is first readable during run *p+1*. Then:

- propagate a **stable pass number** through the graph by monotone fixpoint;
- find strongly connected components with Tarjan's algorithm;
- classify each component by whether the fact values it carries can influence *how much content
  the document generates*.

That last step is what makes the analysis non-vacuous. Ordinary documents are genuinely cyclic (a
table of contents occupies pages, which changes the page numbers recorded in the table of
contents), yet they converge. Documents in which a fact value controls content generation may
not converge at all. Separating these two cases is the technical core of the project.

**The separation is bought with an unsound abstraction, and the price is known.** Splitting each
fact into an `exists` component and a `value` component is what keeps ordinary documents acyclic,
but it severs the edge by which a resolved value's *typeset width* changes a line break and hence a
page break. Four published non-convergence mechanisms travel along exactly that edge, so AuxFlow
cannot see them. The alternative, modelling the extent feedback, makes every document containing one
`\ref` a single strongly connected component and the analysis vacuous. There is no third option
without modelling line breaking. AuxFlow takes the unsound branch, declares it, and measures it;
see [docs/RELATED-WORK.md](docs/RELATED-WORK.md) section 7.4.

## Contribution

Stated after the concessions, because there are many. Full derivation in
[docs/RELATED-WORK.md](docs/RELATED-WORK.md).

**What AuxFlow does not claim.** Static pass numbering is Bochmann (CACM, 1976) and Alblas (1981).
Bounding fixpoint rounds by a structural graph parameter is Hecht and Ullman (1975), including the
"N passes to propagate, one to confirm" decomposition. Instance-level dependency graph plus Tarjan
SCC plus per-component fixpoint over the condensation is Jones (TOPLAS, 1990). Static analysis of
circular dependency graphs with a well-definedness obligation is Farrow (1986). Conservative static
termination analysis where evaluation generates more content to evaluate is Krishnan and Van Wyk
(SLE, 2012). The fixed-rate versus data-dependent-rate schedulability line is Lee and Messerschmitt
(1987). Naming the offending facts is anticipated at least six times, and Typst ships byte spans and
per-iteration value histories today. Checksum verification is universal practice.

**What survives.**

- **A systematised taxonomy of LaTeX non-convergence mechanisms**, stating per mechanism whether a
  dependency-based static criterion detects it. Nine mechanisms; the audit found no prior
  systematisation. Four of the nine are provably invisible to AuxFlow's criterion, and that is
  reported as a result.
- **A controlled comparison of the five deployed convergence oracles**: verdict, soundness
  direction, and executions consumed. Nothing comparable was found.
- **An operational account of a declared LaTeX subset's auxiliary round trip.** No formal semantics
  of TeX exists; Knuth disclaimed interest in one.
- **Contingently:** that a static influence analysis from fact values to content-quantity-governing
  constructs is a usable sufficient condition for the finite-height precondition of
  circular-attribute-grammar fixpoint theory, that is, it decides whether classical fixed-graph
  fixpoint reasoning applies to a document at all. This is what the classical work assumes or
  delegates rather than decides. **The claim is blocked** pending full reads of Krishnan and Van Wyk
  (2012) and Söderberg and Hedin (2013).

## Compiler architecture

```
                Source (declared LaTeX subset)
                            |
                            v
                          Lexer                 category codes 0-15
                            |
                            v
                         Parser                 recursive descent
                            |
                            v
                           AST                  multi-file forest + inclusion graph
                            |
                            v
                   Semantic Analysis            six symbol tables, diagnostics
                            |
                            v
              Auxiliary Reference Graph         instance-level facts, lag-weighted edges
                            |
                            v
                   Static Analysis              content-quantity taint propagation
                            |
                            v
                SCC / Fixpoint Analysis         Tarjan, then stable_pass on the condensation
                            |
                            v
                     Classification             certified / benign-cyclic / amplifying / unknown
                            |
                            v
                       Build Plan               derived schedule + diagnostics
                            |
                            v
            Optional Runtime Verification       normalised auxiliary-state comparison
```

Everything above the build plan is the compiler. Everything below it is optional and may be
removed without the project ceasing to be a complete compiler.

## Current status

Bootstrap and design phase. The repository contains specifications, research notes and scaffolding.
`src/` holds package structure and docstrings only: no lexer, no parser, no analysis.

A prior-art audit was completed on 2026-08-27. Its evidence is in
[research/sources/](research/sources/) (eight files, roughly 460 KB of search logs, verbatim quotes
and per-source anticipation verdicts), indexed by
[research/prior-art-log.md](research/prior-art-log.md). The audit changed the design's positioning
substantially and left three open decisions that must close before implementation: how the taint
criterion is scoped (D13), whether the amplifying class splits (D12), and whether the amplifying
analysis may be claimed at all (D14, blocked on two paper reads).

**Implementation has not started and should not start until D13 and D14 are resolved.**
[docs/IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md) describes the phased plan; it predates the
audit and its ordering must be revisited.

## Scope

**MVP (the compiler, no infrastructure):** lexer, parser, AST, symbol tables, semantic
diagnostics, the Auxiliary Reference Graph, taint analysis, SCC detection, stable-pass fixpoint,
four-state classifier, build-plan generation, plan executor with auxiliary-state verification,
benchmark corpus and measurement harness.

**Stretch:** incremental invalidation, additional external tools, distributed execution,
compiler-derived scheduling metadata, event-driven worker scaling.

**Explicitly excluded:** implementing TeX, macro expansion, full package compatibility, machine
learning, a custom cluster scheduler, a web interface.

Full boundary in [docs/SCOPE.md](docs/SCOPE.md).

## Research

| Document | Contents |
|---|---|
| [docs/PROJECT.md](docs/PROJECT.md) | Authoritative specification, objectives, open decisions |
| [docs/RESEARCH-QUESTIONS.md](docs/RESEARCH-QUESTIONS.md) | Primary and secondary questions, variables |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Compiler core, runtime, optional infrastructure |
| [docs/COMPILER-PIPELINE.md](docs/COMPILER-PIPELINE.md) | Every phase: input, output, algorithms |
| [docs/LANGUAGE-SUBSET.md](docs/LANGUAGE-SUBSET.md) | The supported language and the fallback rule |
| [docs/IR.md](docs/IR.md) | The Auxiliary Reference Graph |
| [docs/STATIC-ANALYSIS.md](docs/STATIC-ANALYSIS.md) | Algorithms, pseudocode, complexity, guarantees |
| [docs/NON-CONVERGENCE.md](docs/NON-CONVERGENCE.md) | Classification and diagnostics |
| [docs/BUILD-PLANNER.md](docs/BUILD-PLANNER.md) | Analysis result to execution plan |
| [docs/RUNTIME-VERIFICATION.md](docs/RUNTIME-VERIFICATION.md) | State-based verification |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Baselines, ground truth, metrics |
| [docs/BENCHMARKS.md](docs/BENCHMARKS.md) | Corpus design |
| [docs/RELATED-WORK.md](docs/RELATED-WORK.md) | Prior art, conceded explicitly |
| [docs/PATENT-NOTES.md](docs/PATENT-NOTES.md) | Prior-art risk; not a patent application |
| [docs/FUTURE-INFRASTRUCTURE.md](docs/FUTURE-INFRASTRUCTURE.md) | Stretch-only distribution work |
| [docs/IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md) | Phased plan with hours and risk |
| [docs/SCOPE.md](docs/SCOPE.md) | Scope lock |
| [docs/AGENT-PROMPT.md](docs/AGENT-PROMPT.md) | Standing prompt for an implementation agent working the plan stage by stage |

The phased plan is also filed on GitHub as [Project #8](https://github.com/users/upayanmazumder/projects/8):
7 milestones, 16 phase issues, 58 sub-issues, a native dependency DAG, and tracking issues for
the risk register, deferred scope, and open decisions. `bench/plan/` holds the machine-readable
source (`implementation-plan.yaml`), its validator, the idempotent poster, and a reconciliation
check that proves GitHub matches the artifact.

Raw notes and unprocessed evidence live in [research/](research/), kept deliberately separate
from the specifications above.

## Reproducibility

All benchmark documents, baseline scripts, the measurement harness and results live under
[bench/](bench/). The rules are fixed before any measurement is taken:

- a pinned, publicly available TeX Live container image, recorded by digest;
- `SOURCE_DATE_EPOCH` and `FORCE_SOURCE_DATE` set for every comparison;
- at least ten repetitions per configuration, reported as median with p95 and interquartile
  range;
- ground truth defined by normalised auxiliary-state equivalence, not by PDF byte identity;
- per-document results only. Corpus-wide means are not reported, because they are determined by
  corpus composition.

No performance claim appears anywhere in this repository without a committed script that
regenerates it.

## Licence

MIT. See [LICENSE](LICENSE).
