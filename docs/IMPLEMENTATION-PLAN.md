# Implementation plan

One developer, 8–10 weeks, roughly 100–140 hours for the core. Estimates assume fluency in the
implementation language and no prior compiler implementation experience.

Two facts worth internalising before starting:

- **The parser is the hardest phase, not the analysis.** Optional arguments, verbatim
  interaction and brace nesting consume more time than Tarjan and the fixpoint combined.
- **The intellectually interesting phase is among the smallest.** Stable-pass numbering is about
  eight hours. Budget accordingly and do not let the front end be rushed to reach it.

## Phases

| # | Phase | Hours | Depends on | Risk | Deliverable |
|---|---|---|---|---|---|
| 1 | Project and tooling setup | 6 | — | LOW | Repository, CI running lint, type check and tests; empty package importable; **the planner safety assertion written first** |
| 2 | Lexer | 14 | 1 | LOW | Category-code tokenizer; `auxflow tokens`; round-trip property test |
| 3 | Parser | 22 | 2 | **HIGH** | Recursive-descent parser; argument-signature table; recovery on malformed input |
| 4 | AST and inclusion resolution | 12 | 3 | MED | Node classes with mandatory spans; multi-file forest; inclusion graph with cycle detection; `auxflow ast` |
| 5 | Symbol tables | 12 | 4 | LOW | Six tables; two-phase declare-then-resolve; `auxflow symbols` |
| 6 | Semantic analysis | 10 | 5 | LOW | Diagnostics with spans; `auxflow check` |
| 7 | IR generation | 14 | 6 | MED | ARG per the lowering rules; `auxflow graph` emitting DOT |
| 8 | SCC analysis | 6 | 7 | LOW | Iterative Tarjan; cycle classification. Testable on synthetic graphs alone |
| 9 | Taint analysis | 8 | 8 | MED | Content-quantity propagation; STRUCTURAL edge insertion |
| 10 | Stable-pass fixpoint | 8 | 8 | LOW | Per-fact numbering on the condensation; derived run count |
| 11 | Classification and diagnostics | 10 | 9, 10 | MED | Four-state classifier; the report formats of NON-CONVERGENCE.md; `auxflow classify` |
| 12 | Build planner | 10 | 11 | MED | BuildPlan generation; optimisation passes; safety invariant property test; `auxflow plan --explain` |
| 13 | Runtime verification | 12 | 12 | MED | Normalisation, state comparison, extension policy; `auxflow run` |
| 14 | Benchmark harness | 14 | 13 | MED | Corpus authored, baselines A–C, harness, ground-truth computation |
| 15 | Evaluation | 12 | 14 | MED | Full measurement run; tables and figures regenerated from JSONL |
| 16 | Documentation and report | 12 | 15 | LOW | Report, figures, demonstration rehearsal |
| | **Total** | **182** | | | |

The core (phases 1–13) is **144 hours**; phases 14–16 add evaluation and write-up. If the
available budget is nearer 100 hours, the cuts in [SCOPE.md](SCOPE.md) apply in the stated
order.

## Week-by-week

| Week | Phases | Checkpoint |
|---|---|---|
| 1 | 1, 2 | **CP1.** Lexer passes unit tests including verbatim, comments and nested braces. Round-trip property holds: concatenating token texts reproduces the source exactly |
| 2 | 3 | Parser handles the simplest four corpus documents; golden AST snapshots committed |
| 3 | 3, 4 | **CP2.** Front end parses every corpus document. Inclusion cycles detected |
| 4 | 5, 6 | **CP3.** Symbol tables complete; `auxflow check` finds seeded undefined references, duplicate labels and missing files |
| 5 | 7 | ARG constructed; DOT output renders; fact and edge counts match hand counts on two documents |
| 6 | 8, 9 | **CP4.** `b08` classified amplifying with three named facts and correct spans; `b05` **not** amplifying; `b11`–`b13` classified exactly as their `declared_false_negative` expectations say. The headline result |
| 7 | 10, 11 | **CP5.** Stable-pass numbering and the classifier complete; diagnostics match the specified formats |
| 8 | 12, 13 | **CP6. MVP complete.** End-to-end `auxflow run` on all fifteen documents; zero *undeclared* under-predictions |
| 9 | 14, 15 | Baselines and full measurement; results regenerate from one command |
| 10 | 16 | Report and demonstration; buffer |

**The MVP exists at the end of week 8**, leaving two weeks for evaluation and write-up. That
margin is deliberate; evaluation always takes longer than expected, and a rushed evaluation is
worse than a smaller one.

## Gates

Two points where the project makes a decision rather than continuing by default.

**Gate 1 — end of week 6.** `b08` classified amplifying, `b05` not, and `b11`–`b13` misclassified
*exactly as predicted*. If the classifier cannot separate `b08` from `b05`, the central contribution
does not work. If `b11`–`b13` behave differently from the prediction, the model is not merely
incomplete but wrong about its own incompleteness, which is worse. Either way the project must be
reframed around the front end, the mechanism taxonomy and the oracle comparison rather than around
convergence classification.
This is the earliest point at which that is knowable, which is why phases 8 and 9 come before
the fixpoint.

**Gate 2 — end of week 9.** Empirical claim EC1: predicted run count is at least ground truth
for every certified document. If it fails, apply the conservative fallback of open decision D7
and report the failing document as a case study of where assumption A2 breaks. That is a
legitimate result and must not be papered over by tuning.

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Parser scope creep toward real-world documents | **HIGH** | **HIGH** | Default-deny subset; the fallback rule is implemented in phase 1, before the parser exists |
| Recursive Tarjan overflowing the stack | MED | MED | Iterative from the start; the realistic document is large enough to trigger it |
| The ARG collapsing into a fixed lattice | MED | **HIGH** | Instance-level facts are specified in IR.md; fact and edge counts are asserted against hand counts in phase 7 |
| Benign-cycle bound mispredicting | MED | MED | Open decision D7 with a specified conservative fallback |
| Ground-truth criterion chosen badly | MED | **HIGH** | Open decision D6 must close before any measurement; PDF byte equality already rejected on evidence |
| Evaluation squeezed into the last week | MED | **HIGH** | MVP at week 8; two-week margin |
| Infrastructure work displacing compiler work | LOW | **HIGH** | Infrastructure is not in the repository at all |
| Assumption A2 failing broadly | LOW | MED | Prediction misses are a reported metric, so failure is measurable rather than invisible |

## Ordering rationale

- **The safety assertion precedes the parser.** It is three lines, and writing it first means no
  version of the planner ever exists that could emit an unsafe plan.
- **SCC before taint.** SCC detection is testable on synthetic graphs with no LaTeX, making it
  the cheapest phase to get right and a stable base for the harder analysis.
- **Both analyses before the fixpoint.** The classifier is the project's central claim; reaching
  it in week 6 rather than week 9 means a failure is discovered while there is still time to
  respond.
- **Corpus authored during phase 14, expectations written earlier.** The documents themselves
  can be written any time; the expectations must be recorded before the analyser can influence
  them.
