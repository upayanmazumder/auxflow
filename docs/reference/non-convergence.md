---
title: "Non-convergence"
parent: "Reference"
nav_order: 6
---

# Non-convergence classification

The most important document in this repository. It defines what AuxFlow claims about
convergence, what it refuses to claim, and what its diagnostics look like.

## What convergence means here

Within the model: an execution is a sequence of engine runs *r₁, r₂, …*; *A_k* is the auxiliary
state after run *k*; run *k* reads *A_{k−1}* and writes *A_k*.

> The compilation **converges** at *N* when *A_N = A_{N−1}*. At that point run *N* read the same
> state it produced, so a further run would change nothing.

Convergence is a property of the *auxiliary state*, not of the rendered output. The two are
related but distinct, and the evaluation ground truth (see [EVALUATION.md](EVALUATION.md))
requires both to be stable.

## What a dependency cycle means

A cycle in the ARG means a set of facts whose values are mutually dependent: each can only be
computed from the others, across auxiliary round trips. The engine resolves such a set by
iteration.

**A cycle does not mean the document fails to converge.** This is the single most important
qualification in the project, and getting it wrong would make the tool useless.

Ordinary documents are cyclic. A table of contents occupies pages; occupying pages shifts the
page numbers of everything after it; those page numbers are recorded in the table of contents.
That is a genuine feedback loop, present in essentially every thesis, and it settles after two
or three runs.

So the useful question is not *is there a cycle* but *what kind of feedback does the cycle
carry*.

## The distinction that matters

**Benign feedback.** Fact values influence other fact values, but the *quantity* of generated
content is fixed by document structure. A section produces exactly one table-of-contents entry
whatever its page number turns out to be. The number of entries is static; only the recorded
numbers move. Such loops settle.

**Amplifying feedback.** A fact value influences *how much content the document generates*. Now
the loop can chase itself: more content shifts pages, the shifted page value generates a
different amount of content, and so on. This is the class in which convergence can genuinely
fail.

The canonical example is a loop whose bound is a page reference to a label placed in the
material the loop generates. A published nine-line counterexample of this shape exists in which
a cross-reference is wrong regardless of how many runs are performed (Gaspar, *TUGboat* 35:1,
2014, p. 16).

AuxFlow separates the two cases with the taint analysis of
[STATIC-ANALYSIS.md](STATIC-ANALYSIS.md): a feedback edge is `STRUCTURAL` when a fact value can
reach a content-generating construct.

## The four states

| State | Condition | Meaning | Plan |
|---|---|---|---|
| `CERTIFIED(N)` | ARG acyclic, no opaque facts, all `stable_pass` bounded | Under the model the fixpoint exists and is reached within *N = P + 1* runs | exactly *N* runs, verified |
| `BENIGN_CYCLIC(N?)` | every cycle labelled benign, no opaque facts | Ordinary feedback. Expected to converge; the bound, where given, is heuristic | *N* if bounded, else conservative default; always verified |
| `AMPLIFYING(c)` | some SCC contains a `STRUCTURAL` edge | A value influences how much content is generated. **May never converge.** | refuse by default; `--force` runs under a cap |
| `UNKNOWN` | any opaque fact, or an unmodelled package | Cannot reason about this document | conservative default, fully verified |

## What AuxFlow can safely infer

- That a structural cycle exists, and precisely which facts and edges constitute it. Tarjan is
  exact on the constructed graph.
- That a cycle passes through a construct whose generated content quantity depends on a fact
  value.
- That, in the acyclic case and under the stated assumptions, no fact can stabilise earlier than
  its longest dependency chain permits.
- That a document containing constructs outside the subset has not been analysed and must not be
  scheduled aggressively.

## What AuxFlow cannot infer

- **That an amplifying document diverges.** The classification identifies a necessary structural
  condition, not a sufficient one. A loop bounded by a page reference may still settle if the
  fixpoint happens to be consistent.
- **That a benign document converges.** Convergence of benign feedback is an empirical regularity
  within the model, not a theorem. The formal condition it approximates is stated exactly by
  Magnusson and Hedin (*SCP* 68(1), 2007): a fixpoint is guaranteed "if the values for each attribute
  on a cycle can be organized in a lattice of finite height and if all the semantic functions
  involved in computing these attributes are monotonic on the respective lattices". Nobody in that
  literature checks the condition; AuxFlow's taint analysis is an attempt at a domain-specific
  sufficient condition for the finite-height half only.
- **That the absence of a structural cycle implies convergence.** This is the audit's sharpest
  adverse finding and it is not a corner case. Four published mechanisms are non-convergent and
  produce no structural edge at all:
  - the *typeset width* of a resolved reference changing a line break, hence a page break, hence the
    reference (period-2 oscillation, no loop, no conditional — `tex.stackexchange.com/questions/30674`
    accepted answer);
  - a `[!t]` float combined with roman page numbering (same thread, David Carlisle);
  - `varioref`-style dynamic textual references whose length moves the floats they refer to
    (`labelschanged` documentation);
  - references inside margin or foot notes (same).

  All four travel along the `.value` → pagination edge that [IR.md](IR.md)'s `exists`/`value` split
  severs by construction. **An ARG cycle is therefore neither necessary nor sufficient for
  non-convergence.** The full nine-mechanism taxonomy is in
  [RELATED-WORK.md](RELATED-WORK.md) section 7.3.
- **Anything about constructs outside the subset.**
- **Anything about engine termination**, which can fail for reasons unrelated to cross-references —
  including reasons with no cross-reference content at all, such as a generated auxiliary file
  carrying its own creation timestamp (documented in the `latexmk` manual).

## Two failure modes, conflated by one label

`AMPLIFYING` currently covers two distinct failures with distinct causes, and the audit recommends
splitting them (open decision D12 in [PROJECT.md](PROJECT.md)):

- **Finite-height failure.** Gaspar's `\forloop` bounded by `\pageref` diverges *monotonically*: the
  recorded page value increases by exactly one every run, without bound. The value domain is
  unbounded because the page count is a function of the iterate.
- **Monotonicity failure.** The width-driven and conditional cases *oscillate* with period two. The
  domain is bounded; the feedback function is not monotone.

The distinction matters because AuxFlow detects the first class and largely cannot detect the second.
Reporting them under one label makes the coverage gap invisible. Synchronous dataflow makes the same
split — rate inconsistency versus deadlock — and it is a citable precedent (Lee and Messerschmitt,
*IEEE Trans. Computers*, 1987).

## What already ships elsewhere

Recorded here because the diagnostic design below must be positioned against it rather than
presented as new.

- **Typst** emits, per unstable fact, a warning with a byte span, the full per-iteration value
  history, and a secondary "created here" span for the element that produced the value — plus a
  document-level `document did not converge within five attempts`. Its own test suite contains
  AuxFlow's amplifying case with the observed counts `0,1,2,3,4,5`.
- **`labelschanged`** (CTAN) prints the offending label instances with their old and new `\meaning`
  on every compile, and ships a hand-written taxonomy of causes.
- **Tectonic** names the file whose content changed (`"foo.aux" changed`).
- **`latexmk` and ConTeXt** report nothing but that a cap was reached.

AuxFlow's remaining differentiators are that it reports a *dependency chain* rather than an endpoint,
and that it does so having performed **zero** engine executions. Both must be demonstrated
side-by-side, not asserted. See RQ6 in [RESEARCH-QUESTIONS.md](RESEARCH-QUESTIONS.md).

## Required wording

AuxFlow must **never** print "this document cannot converge" or "this document will not
terminate". The permitted phrasing is *may not converge*, accompanied by the structural evidence
that prompted it.

The asymmetry is deliberate. A false positive costs the user one flag. A false negative costs a
silently wrong document. Bias toward reporting.

## Diagnostic design

A diagnostic that says only `CYCLE DETECTED` is a failure of the project, not a feature of it.
Every report must answer four questions: *which facts*, *where in the source*, *what kind of
dependency*, and *what most likely caused it*.

### Amplifying cycle

```
auxflow: AMPLIFYING CYCLE -- this document may not converge.

  A cross-reference value influences how much content the document generates,
  which in turn changes that value.

  cycle (3 facts):
    PAGEREF_USE(l)        main.tex:5:32    reads the page of label 'l'
      -> CONTENT_VOLUME   main.tex:5:5     STRUCTURAL: the value bounds \forloop,
                                           whose body emits \newpage
      -> LABEL_PAGE(l)    main.tex:7:22    the page of 'l' is set by pagination
      -> PAGEREF_USE(l)   main.tex:5:32

  likely cause:
    the loop at main.tex:5 is bounded by \pageref{l}, and the label 'l' is
    placed inside content that the loop generates.

  Under the supported semantics no finite run count is guaranteed to stabilise
  this structure.

  No build plan emitted. Use --force to execute under a cap of 6 runs.
```

### Benign cycle, reported only at higher verbosity

```
auxflow: note: benign feedback cycle (2 facts)

    LIST_EXTENT(toc)      main.tex:3:1     table of contents occupies pages
      -> CONTENT_VOLUME   main.tex:3:1     LAYOUT
      -> LIST_EXTENT(toc)

  The number of entries is fixed by document structure, so this loop affects
  recorded values only. Classified BENIGN_CYCLIC.
```

Reporting benign cycles at normal verbosity would train the user to ignore the amplifying ones.

### Unknown

The default report groups the same unsupported construct across a project.
It shows the first source location and the number of occurrences. `-v` shows
every location.

```text
auxflow: UNKNOWN -- document contains constructs outside the analysable subset.

    unsupported control sequence: \csname (3 occurrences)  chapters/methods.tex:88:3
    unmodelled package: exotic  main.tex:12:1

  These constructs have unmodelled effects. The plan uses the
  conservative default and requires runtime verification.
```

### Certified, with an explanation of the bound

```
auxflow: CERTIFIED -- 4 runs

  longest dependency chain (stable_pass 3):
    CITE_USE(knuth84)       chapters/intro.tex:44:12   -> 1
    BBL.exists              main.tex:210:1   TOOL       -> 1
    TOC_ENTRY(bib).exists   main.tex:210:1   LAYOUT     -> 2
    CONTENT_VOLUME          main.tex:3:1     LAYOUT     -> 3
    LABEL_PAGE(res:tab)     chapters/res.tex:19:4       -> 3
    PAGEREF_USE(res:tab)    chapters/disc.tex:7:55      consumed on run 4

  Two page references are the only facts requiring the fourth run.
```

The last line is the most useful thing AuxFlow produces for an author, and it comes free from
per-fact numbering — a per-document count could not produce it.

## Diagnostic data requirements

Every element above is drawn from fields already in the IR. Specifically the reports require:
`Fact.source_location` on every fact including synthetic ones; `DepEdge.reason` written at
construction time; `DepEdge.dependency_type`; SCC membership; and `stable_pass` per fact.

This is why those fields are mandatory in [IR.md](IR.md) rather than optional.

## Testing

The two highest-value tests in the project both live here:

1. **b08 must be classified amplifying**, with all three facts named and correct spans.
2. **b05 must not be classified amplifying.** A classifier that flags every document containing
   a table of contents is worthless, and this negative test is the guard against the most likely
   way for the analysis to fail while appearing to work.
