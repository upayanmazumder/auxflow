# Contributing

Currently a single-author research project. These conventions exist to keep it defensible rather
than to coordinate a team.

## Principles

1. **Compiler first.** Infrastructure never precedes analysis.
2. **Static analysis must be explainable.** Every classification names the facts responsible and
   points at source locations. A result that cannot be explained is not finished.
3. **No unsupported claims.** Every assertion is measured, cited, or explicitly labelled an
   assumption.
4. **No fabricated benchmarks.** A number appears only if a committed script regenerates it.
5. **No premature infrastructure.**
6. **Every compiler phase has tests.**
7. **Unsupported constructs fail safely**, never silently.
8. **Prefer a smaller formal model that can be defended** over a larger one that cannot.
9. **Reproducibility is a deliverable.**
10. **Every research claim has evidence attached.**

## Before writing code

Read [docs/PROJECT.md](docs/PROJECT.md), [docs/SCOPE.md](docs/SCOPE.md) and the specification
for the phase being implemented. The design is fixed; if implementation reveals that it is
wrong, change the specification first and record why.

## Architectural rules

Enforced by review, and worth enforcing by test where practical.

- `auxflow.analysis` must not import `auxflow.ast`. Anything an analysis needs belongs in the
  IR. This is what keeps the ARG an honest intermediate representation.
- Nothing outside `auxflow.runtime` may execute a subprocess.
- Every AST node and every fact carries a source span. No exceptions, including synthetic facts.
- Every dependency edge carries a `reason` string written at construction time, when the
  justification is still known.
- The planner's safety invariant — never emit a plan shorter than the conservative default
  unless the classification is certified — is an assertion, not a convention.

## Claims discipline

The project previously had to withdraw several attractive but incorrect claims. To avoid a
repeat:

- Do not write "minimal" where "model-minimal" is meant.
- Do not write "proves" where the analysis establishes a necessary but not sufficient condition.
- Do not state a soundness property without its assumptions in the same paragraph.
- Do not quote a timing without the distribution behind it.
- The list of claims that must never be made is in [docs/PATENT-NOTES.md](docs/PATENT-NOTES.md).
  It is short and it is binding.

## Tests

| Layer | Location | Expectation |
|---|---|---|
| Unit | `tests/unit/` | Every phase, in isolation |
| Golden | `tests/golden/` | AST and ARG snapshots; regenerated deliberately, never automatically |
| Property | `tests/property/` | Lexer round-trip; planner safety invariant |
| End-to-end | `tests/e2e/` | Full pipeline over the corpus; engine-dependent tests marked and skippable |

Two tests matter more than the rest and should never be weakened: the planner safety invariant,
and the negative classification test asserting that an ordinary table-of-contents document is
**not** classified as potentially non-convergent. A classifier that flags every document is
worthless, and that test is the guard against it.

## Commits

Conventional prefixes: `feat`, `fix`, `docs`, `test`, `refactor`, `bench`, `chore`.

Scope changes state what was traded, as required by
[docs/SCOPE.md](docs/SCOPE.md#scope-change-protocol). Commits that add a measurement reference
the results file that supports it.

## Style

No emoji. No marketing language. Precise technical prose. Where a limitation exists, state it in
the same place as the capability it limits rather than collecting limitations at the end where
nobody reads them.
