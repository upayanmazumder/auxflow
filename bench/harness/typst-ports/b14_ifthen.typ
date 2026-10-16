// Hand-ported mechanism from bench/corpus/b14_ifthen/main.tex (M2: a
// page-conditioned font size changes the label's own page), per
// docs/EVALUATION.md's "ported by hand" cross-check requirement.

The condition compares the page number of the final label.

#v(18cm)
#context {
  if here().page() <= 1 [
    #text(size: 48pt)[A]
  ] else [
    #text(size: 10pt)[A]
  ]
}
#label("test")
#pagebreak()
