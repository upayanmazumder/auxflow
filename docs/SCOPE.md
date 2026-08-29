# Scope lock

Explicit boundary. Changes to this document are scope changes and should be made deliberately,
with a note of what is being traded away.

## MUST BUILD

The compiler. This list alone constitutes a complete project.

1. Category-code lexer covering codes 0–15, with comment and verbatim handling, and
   `auxflow tokens`.
2. Recursive-descent parser with an argument-signature table and error recovery.
3. AST with a mandatory span on every node; multi-file forest; inclusion graph with cycle
   detection; `auxflow ast`.
4. Six symbol tables with two-phase resolution; `auxflow symbols`.
5. Semantic diagnostics — undefined references and citations, duplicate labels, unresolvable
   inclusions, missing graphics, inclusion cycles — with zero engine executions;
   `auxflow check`.
6. The Auxiliary Reference Graph with instance-level facts and the exists/value split;
   `auxflow graph` emitting DOT.
7. Content-quantity taint analysis inserting STRUCTURAL edges.
8. Iterative Tarjan SCC detection with cycle classification.
9. Stable-pass fixpoint over the condensation.
10. Four-state classifier with the diagnostic formats specified in
    [NON-CONVERGENCE.md](NON-CONVERGENCE.md); `auxflow classify`.
11. Build-plan generation with the four optimisation passes and the safety invariant;
    `auxflow plan --explain`.
12. Plan executor with normalised auxiliary-state verification and bounded extension;
    `auxflow run`.
13. A benchmark corpus with hand-written expectations, committed. It **must** contain one member per
    non-convergence mechanism enumerated in [RELATED-WORK.md](RELATED-WORK.md) section 7.3,
    including the four that AuxFlow provably cannot detect. Without them the mechanism-coverage
    result — the project's least contingent contribution — does not exist. That makes the corpus
    larger than the ten documents originally planned.
14. Measurement harness covering baselines A, B, C, C′, C″, D and E per
    [EVALUATION.md](EVALUATION.md), ground-truth computation, and table generation. C′
    (consecutive-input comparison) and C″ (same-run read-then-written comparison) were added by the
    prior-art audit and are not optional: without them the execution-economy comparison is a
    strawman against tools that already avoid the redundant run.
15. A mechanism-coverage table: per mechanism, the expected classification, the observed
    classification, and whether a mismatch was declared in advance.
16. An oracle-comparison table: per corpus member, each oracle's verdict, its soundness direction,
    and the executions it consumed.

## SHOULD BUILD

Valuable for the research, not required for the compiler to be complete.

17. Per-fact stability report — naming which specific references force the final run.
18. Dead-file and dead-tool elimination, with the realistic corpus document containing genuinely
    unreachable files so the effect is measurable.
19. `--strict` mode refusing to execute unknown-classified documents.
20. DOT output that colours nodes by component and edges by dependency type, so benign and
    amplifying cycles are visually distinguishable.
21. Golden-file test infrastructure for AST and ARG snapshots.
22. Splitting `AMPLIFYING` into a finite-height failure and a monotonicity failure (open decision
    D12). Small, and it makes the coverage gap visible rather than hidden behind one label.

## STRETCH

Attempted only after item 16 is complete and measured.

23. `\includeonly`-driven incremental invalidation.
24. Index tool support, confirming the tool-lag model generalises beyond one external program.
25. Long-table width feedback, a convergence mechanism unrelated to pagination.
26. Distributed execution of independent documents.
27. Compiler-derived scheduling metadata attached to work items.
28. Event-driven worker scaling.

Items 26–28 are specified in [FUTURE-INFRASTRUCTURE.md](FUTURE-INFRASTRUCTURE.md) and are not
present in this repository.

## DO NOT BUILD

Excluded deliberately. Each has been considered and rejected.

| Excluded | Reason |
|---|---|
| A TeX engine or interpreter | Multi-year; the project analyses documents, it does not typeset them |
| Macro expansion | Requires an interpreter; a partial implementation would be unsound while appearing to work |
| Category-code redefinition support | Invalidates the lexer's own assumptions |
| Full package compatibility | Unbounded surface; coverage is measured in mechanisms modelled, not macros recognised |
| A production replacement for existing build tools | Not the contribution; existing tools are correct |
| Any LLVM or MLIR involvement | The IR models document facts, not machine code; nothing in a compiler backend framework represents it |
| Machine-learning prediction of anything | No training data, no need, and it would replace an explainable analysis with an unexplainable one |
| A custom cluster scheduler | Multi-year; off-the-shelf mechanisms suffice for the stretch work |
| A cluster operator or controller | Same |
| Per-pod resource sizing | Not something the intended stretch mechanism can do; noted so it is not attempted |
| Production distributed orchestration | Not the contribution |
| A web interface | Two command-line invocations demonstrate the system |
| Authentication, multi-tenancy, persistence beyond a results file | Not the contribution |
| Support for arbitrary real-world documents | Default-deny subset; growth is by mechanism |
| Any infrastructure before item 16 is complete | The failure mode that has sunk comparable projects |

## Cut order

If time runs short, cut in exactly this order. The order is chosen so that every prefix removal
leaves a coherent project.

1. Event-driven worker scaling.
2. Distributed execution and scheduling metadata.
3. Index and long-table support.
4. Incremental invalidation.
5. Dead-file elimination.
6. Per-fact stability report.
7. Explained-plan detail, reducing `--explain` to a plain plan dump.

## Never cut

Lexer. Parser. Symbol tables. Semantic diagnostics. The ARG. Taint analysis. SCC detection.
Stable-pass numbering. The classifier. Build-plan generation. The planner safety invariant.
Runtime verification. The corpus. The harness.

After every permitted cut, what remains is a lexer, a parser, symbol tables, a graph
intermediate representation, two dataflow analyses, a classifier, code generation and a verified
executor — a complete compiler project containing no infrastructure whatsoever.

## Scope change protocol

Adding to MUST BUILD requires removing something else, or explicitly accepting a schedule slip
in [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md). Record the trade in the commit message. The
purpose of this document is to make scope changes visible, not to forbid them.
