---
title: "Compiler pipeline"
parent: "Reference"
nav_order: 2
---

# Compiler pipeline

Thirteen phases. For each: input, output, responsibility, data structures, algorithm, and the
compiler-design concept it instantiates.

Phases 1–12 require no TeX engine. Phase 13 is the only one that executes anything.

---

## 1. Lexical analysis

- **Input** — source bytes for one file.
- **Output** — `list[Token]`.
- **Responsibility** — classify every character by TeX category code and group characters into
  tokens; recognise comments and verbatim regions so that later phases never see their contents
  as syntax.
- **Data structures** — `Token(catcode, text, file_id, line, col, offset)`; a 256-entry category
  table.
- **Algorithm** — single-pass table-driven scan. Control sequences: escape character (catcode 0)
  followed by either a maximal run of letters (catcode 11) or exactly one other character.
- **Compiler-design relevance** — textbook lexical analysis with a non-trivial character-class
  table. The category-code mechanism is the part worth explaining in a viva: it is a genuine
  lexer-level abstraction that most languages do not have.
- **Traps** — `%` starts a comment but `\%` does not; `\verb|...|` takes its delimiter from the
  next character; a comment consumes the following newline and any leading whitespace on the
  next line.

## 2. Parsing

- **Input** — `list[Token]`.
- **Output** — one AST per file.
- **Responsibility** — recover document structure: preamble, environments, macro calls with
  arguments, groups, sectioning.
- **Data structures** — the node classes of phase 3.
- **Algorithm** — recursive descent, one token of lookahead. Argument parsing is driven by a
  table of known macro signatures (`\label{}` takes one mandatory argument;
  `\includegraphics[]{} ` takes one optional and one mandatory). Unknown control sequences
  consume no arguments and produce a bare `MacroCall`.

The phase 7 parser elaboration preserves `\forloop` and `\whiledo` conditions
and bodies as `ControlConstruct` nodes. It stores `\newcommand` bodies as
unexpanded tokens in `MacroDef` nodes. ARG lowering turns unsupported bare
calls into opaque facts rather than assuming they are safe.

- **Compiler-design relevance** — syntax analysis; a hand-written predictive parser.
- **Note** — this is the highest-risk phase. Optional arguments, nested braces inside optional
  arguments, and verbatim interaction are where the time goes.

## 3. AST construction

- **Input** — parser events.
- **Output** — a typed tree.
- **Node kinds** — `Document`, `Preamble`, `DocumentClass`, `UsePackage`, `Include(kind)`,
  `Sectioning(level)`, `Environment(name)`, `MacroCall(name, args)`, `Group`, `Text`, `Comment`,
  `VerbatimBlock`, `MacroDef(name, arity, body_tokens)`, `CounterOp(op, counter)`,
  `ControlConstruct(kind, condition, body)`, `Opaque(reason)`.
- **Responsibility** — a stable, traversable representation with a mandatory
  `Span(file_id, start, end)` on every node.
- **Compiler-design relevance** — abstract syntax; the visitor pattern for later phases.
- **Design rule** — `MacroDef` records a body as *tokens*, never expanded. If a body contains a
  modelled construct, the macro is marked opaque. Expansion is out of scope and pretending
  otherwise would be unsound.

## 4. Symbol-table construction

- **Input** — AST forest.
- **Output** — six tables.
- **Responsibility** — resolve names across file boundaries.

| Table | Key | Value |
|---|---|---|
| `LabelTable` | label key | defining node, counter kind, file, span, duplicate flag |
| `RefTable` | label key | list of uses with kind (`ref` / `pageref`) and span |
| `CiteTable` | cite key | presence in the bibliography database, spans |
| `PackageTable` | package name | fact kinds it may produce, associated tool, whether modelled |
| `FileTable` | file id | path, includer, reachability, opacity |
| `CounterTable` | counter name | definitions, reads, writes, spans |

`LabelTable` keeps the first definition for each key. Later definitions set its
duplicate flag and retain their spans. `RefTable` keeps uses separate from
definitions until the resolution pass binds them.

The declaration pass scans every file before it binds any use. It records
labels, packages, files and counter operations. An unknown package stays
unmodelled. The pass treats `graphicx` as modelled with no auxiliary facts.

The resolution pass binds `\ref` and `\pageref` uses to declared labels, even
across files. It records each `\cite` key with its source span. Uses with no
definition remain unbound for phase 6 diagnostics.

For cited keys, the resolution pass reads each named `\bibliography` database
relative to its source file. It marks a key present when a BibTeX entry
declaration names that key. Missing databases leave cited keys absent.

- **Algorithm** — two-phase traversal: declare, then resolve. A single phase would misreport
  forward references as undefined.
- **Compiler-design relevance** — symbol tables and scope resolution. The multi-file aspect is
  genuine: a label defined in one included file and referenced in another is exactly
  cross-module name resolution.

## 5. Semantic analysis

- **Input** — AST forest, symbol tables.
- **Output** — diagnostics; annotated tables.
- **Checks** — undefined reference, undefined citation, duplicate label, unresolvable inclusion,
  missing graphics file, inclusion cycle, use of an unmodelled package.

Name diagnostics use the unresolved reference span, the cited key's use span,
or the duplicate label's later definition span. A citation is undefined when
the CiteTable marks its key absent from the declared bibliography databases.

File checks stat inclusion targets and graphics paths relative to their source
file. A graphics name without a suffix can match `.pdf`, `.png`, `.jpg`, `.jpeg`
or `.eps`. A cycle diagnostic uses the span of its closing inclusion.

An unmodelled package produces a warning at its `\usepackage` span. All name
and file defects above produce errors.

- **Algorithm** — table lookups after resolution; DFS with colouring for inclusion cycles.
- **Compiler-design relevance** — semantic analysis proper. Every check runs with zero engine
  executions, which is the point: these are defects an engine would report only after a full
  typesetting run, if at all.

## 6. IR generation

- **Input** — AST forest, symbol tables.
- **Output** — the Auxiliary Reference Graph.
- **Responsibility** — lower syntax into fact instances and lag-weighted dependency edges.
- **Algorithm** — syntax-directed translation; one traversal, one rule per modelled construct.
  Rules are tabulated in [STATIC-ANALYSIS.md](/reference/static-analysis.html).
- **Compiler-design relevance** — intermediate representation generation. Full specification in
  [IR.md](/reference/ir.html).

## 7. Static dependency analysis (content-quantity taint)

- **Input** — ARG, AST.
- **Output** — a set of tainted facts; `STRUCTURAL` edges added to the ARG.
- **Responsibility** — determine which fact values can influence *how much content the document
  generates*.
- **Algorithm** — forward worklist propagation to a fixpoint over a finite lattice.
- **Complexity** — O(V + E).
- **Compiler-design relevance** — taint analysis, a standard forward dataflow problem. This is
  the phase that separates benign feedback from the amplifying kind, and without it the
  classifier is vacuous.

## 8. Fixpoint analysis (stable-pass numbering)

- **Input** — the SCC condensation of the ARG.
- **Output** — `stable_pass: dict[fact_id, int | None]`.
- **Responsibility** — compute, for each fact, the earliest run after which its value no longer
  changes.
- **Algorithm** — longest path over a DAG in topological order; the recurrence is in
  [IR.md](/reference/ir.html).
- **Complexity** — O(V + E).
- **Compiler-design relevance** — monotone dataflow analysis with a least-fixpoint solution;
  the direct analogue of pass numbering in multi-pass attribute evaluation.

## 9. SCC analysis

- **Input** — ARG.
- **Output** — components in reverse topological order; a label per component.
- **Algorithm** — Tarjan's algorithm, **iterative with an explicit stack**. A recursive
  implementation will exhaust the stack on the realistic corpus member.
- **Complexity** — O(V + E).
- **Compiler-design relevance** — strongly connected component analysis over a dependency graph;
  the condensation is what makes phase 8 well defined on a cyclic graph.

## 10. Classification

- **Input** — components, labels, taint set, opacity flags, `stable_pass`.
- **Output** — one of four states plus a diagnosis.
- **Algorithm** — decision procedure in [NON-CONVERGENCE.md](/reference/non-convergence.html).
- **Compiler-design relevance** — static program classification; conservative approximation.

## 11. Optimisation

- **Input** — classification, symbol tables, ARG.
- **Output** — a reduced plan.
- **Passes**
  1. **Dead-tool elimination** — omit the bibliography tool when no citation facts exist.
  2. **Dead-file elimination** — restrict per-file auxiliary tooling to files reachable in the
     inclusion graph.
  3. **Run-count derivation** — derive the run count from `stable_pass` rather than using a
     constant.
  4. **Non-convergence refusal** — emit no plan for an amplifying document unless forced.
- **Compiler-design relevance** — dead code elimination and reachability analysis, applied to a
  build plan rather than to instructions.
- **Note** — deliberately four passes, not more. Merging tool invocations and speculative
  parallelisation were considered and rejected as padding.

## 12. Build-plan generation

- **Input** — optimised analysis result.
- **Output** — `BuildPlan` as JSON.
- **Responsibility** — lower the analysis into an ordered sequence of tool invocations, each
  carrying a `reason` traceable to a fact or a classification.
- **Compiler-design relevance** — code generation, targeting a small tool instruction set rather
  than a machine architecture. Specification in [BUILD-PLANNER.md](/reference/build-planner.html).

## 13. Runtime verification (optional)

- **Input** — `BuildPlan`, a working directory.
- **Output** — artifacts, `ExecReport`.
- **Responsibility** — execute the plan, observe the auxiliary state, confirm or extend.
- **Algorithm** — normalised state comparison; see
  [RUNTIME-VERIFICATION.md](/reference/runtime-verification.html).
- **Compiler-design relevance** — runtime verification of a statically derived property; the
  empirical check on the analysis.

---

## Phase dependency graph

```
1 lexer --> 2 parser --> 3 ast --> 4 symbols --> 5 semantic
                                        |
                                        v
                                     6 ir
                                        |
                          +-------------+-------------+
                          v                           v
                   7 taint analysis              9 scc analysis
                          |                           |
                          +-------------+-------------+
                                        v
                                8 stable_pass (on the condensation)
                                        |
                                        v
                                 10 classification
                                        |
                                        v
                                 11 optimisation
                                        |
                                        v
                              12 build-plan generation
                                        |
                                        v
                            13 runtime verification (optional)
```

Phases 7 and 9 are independent of one another and both feed phase 8: taint supplies the edge
labels that phase 9's classifier reads, and phase 9 supplies the condensation that phase 8
traverses. Implement 9 before 7 — SCC detection is testable on synthetic graphs with no LaTeX
involved, which makes it the cheapest phase to get right.
