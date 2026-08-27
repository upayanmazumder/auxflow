# AuxFlow

Static convergence classification for multi-pass document compilation.

AuxFlow is a compiler and static analyser for a declared subset of LaTeX. It parses a document
into an instance-level dependency graph of auxiliary facts, computes when each fact stabilises,
and classifies the document's convergence behaviour — before the typesetting engine runs once.

**Status: bootstrap / design phase. No compiler code has been written yet.** See
[Current status](#current-status).

---

## What is AuxFlow?

Document compilers such as LaTeX are *multi-pass*: they resolve cross-references by writing
facts to auxiliary files and reading them back on the next run. A `\ref` cannot be resolved
until the corresponding `\label` has been recorded, which happens during a previous run. The
process iterates to a fixpoint.

How many runs a given document needs is a property of its cross-reference structure. In current
practice that property is discovered *dynamically* — run the engine, compare the auxiliary state
with the previous run's, repeat until nothing changes. AuxFlow asks a different question:

> How much of this can be determined statically, from the source alone?

AuxFlow is a conventional compiler front end (category-code lexer, recursive-descent parser,
multi-file AST, symbol tables) feeding a purpose-built intermediate representation and two
dataflow analyses. Its output is a classification, a build plan, and — for documents whose
cross-reference structure may never converge — a diagnosis naming the facts responsible.

## Problem

Three questions about a document *D* have no answer before execution:

1. Does the auxiliary-state fixpoint for *D* exist?
2. If so, how many engine runs are needed to reach it?
3. If not, which cross-reference structures are responsible?

Existing tooling answers (1) and (2) only by executing, and does not answer (3) at all — it
reports that a retry limit was exhausted, without attributing a cause.

Three further observations motivate the work:

- **Fixed schedules are wrong in both directions.** The conventional `latex, bibtex, latex,
  latex` sequence over-provisions simple documents and under-provisions ordinary ones.
- **The engine's own rerun warning is not a sound completion oracle.** LaTeX warns when
  *references* have changed, but not when a generated list such as a table of contents has.
  A build that stops when the engine stops complaining can emit a document with no table of
  contents.
- **Dynamic detection costs an execution.** A detector that certifies stability by comparing
  consecutive states must observe one unchanged transition, so it performs one run beyond the
  last productive one. This is structural, not an implementation defect.

## Core idea

Lower the document to a graph whose nodes are *individual auxiliary fact instances* — this
label's page number, that table-of-contents entry — and whose edges carry a **pass lag**: a fact
written during run *p* is first readable during run *p+1*. Then:

- propagate a **stable pass number** through the graph by monotone fixpoint;
- find strongly connected components with Tarjan's algorithm;
- classify each component by whether the fact values it carries can influence *how much content
  the document generates*.

That last step is what makes the analysis viable. Ordinary documents are genuinely cyclic — a
table of contents occupies pages, which changes the page numbers recorded in the table of
contents — yet they converge. Documents in which a fact value controls content generation may
not converge at all. Separating these two cases is the technical core of the project.

## Key contribution

- **Instance-level dependency analysis.** Facts are individual instances with source locations,
  not a fixed set of generic node kinds. This is what makes the analysis a real dataflow
  problem rather than a lookup table.
- **Stable-pass propagation.** A per-fact monotone fixpoint over the component condensation.
- **Cycle classification via SCC plus taint.** Feedback edges are classified by whether a value
  can reach a content-generating construct.
- **Early classification of problematic dependency structures**, with the participating facts,
  their source locations, and the dependency types reported — not merely "cycle detected".
- **Build-plan generation** from the analysis result.
- **A controlled comparison against dynamic convergence detection**, including the cases where
  static analysis provides no benefit.

**AuxFlow does not claim to have invented static pass-number minimisation.** Computing minimal
pass numbers from a dependency-graph characterisation is established prior art in the attribute
grammar literature, dating to Bochmann (CACM, 1976). AuxFlow transplants that technique to a
domain that violates its preconditions, and the contribution is the machinery that makes the
transplant possible. See [docs/RELATED-WORK.md](docs/RELATED-WORK.md).

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

Bootstrap and design phase. The repository currently contains specifications, research notes and
scaffolding. `src/` holds package structure and docstrings only — no lexer, no parser, no
analysis has been implemented.

The design is fixed and documented; implementation follows
[docs/IMPLEMENTATION-PLAN.md](docs/IMPLEMENTATION-PLAN.md).

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
