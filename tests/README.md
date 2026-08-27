# Tests

Layout follows [../CONTRIBUTING.md](../CONTRIBUTING.md).

| Directory | Contents |
|---|---|
| `unit/` | One module per compiler phase, tested in isolation |
| `golden/` | AST and ARG snapshots, regenerated deliberately and never automatically |
| `property/` | Invariants that must hold over generated inputs |
| `e2e/` | Full pipeline over the benchmark corpus |

## Markers

- `engine` — requires a TeX engine. Skipped by `make test-fast`.
- `slow` — excluded from the default run.

Everything up to and including build-plan generation must be testable **without** an engine.
That is a design requirement, not a convenience: it is what makes the compiler independently
verifiable.

## The two tests that matter most

1. **Planner safety invariant** (`property/`) — over randomly generated classifications, the
   emitted plan is never shorter than the conservative default unless the classification is
   certified. This is what makes an analysis bug incapable of corrupting a document.

2. **Negative classification** (`e2e/`) — an ordinary document with a table of contents must
   **not** be classified as potentially non-convergent. Such documents are genuinely cyclic, and
   a classifier that flags them is useless while appearing to work. This is the most likely way
   for the project to fail silently.

Neither may be weakened to make a build pass.

## Coverage expectations

No coverage percentage target. Instead: every phase has unit tests, every diagnostic format in
[../docs/NON-CONVERGENCE.md](../docs/NON-CONVERGENCE.md) has a test asserting its shape, and
every corpus document has an end-to-end test checking its classification against the
hand-written expectation.
