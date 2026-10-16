// Hand-ported mechanism from bench/corpus/b08_cycle/main.tex (M1: a loop
// bounded by a page reference to a label inside the generated material),
// per docs/EVALUATION.md's "ported by hand" cross-check requirement.
//
// Typst has no separate .aux round trip: it resolves `\pageref`-style
// forward references by re-running its own layout pass internally, capped
// at a small fixed attempt count, and reports an explicit "did not
// converge" error rather than silently emitting a stale value. This port
// exists to record what that built-in oracle says about the same
// mechanism, not to reproduce LaTeX's run-count exactly.

#let n = state("n", 0)

#context {
  let target = locate(<boundary>).page()
  while n.get() < target {
    n.update(x => x + 1)
    pagebreak()
  }
}

Boundary page. #label("boundary")
