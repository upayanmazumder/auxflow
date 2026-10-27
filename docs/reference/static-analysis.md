---
title: "Static analysis"
parent: "Reference"
nav_order: 5
---

# Static analysis

The analysis stage takes the AST and symbol tables and produces a classification, a per-fact
stable-pass numbering, and the evidence needed to explain both.

Four steps: graph construction, taint propagation, SCC detection, stable-pass numbering.

---

## 1. Dependency extraction and graph construction

Syntax-directed, one AST traversal, one rule per modelled construct.

| Construct | Facts produced | Edges added |
|---|---|---|
| `\label{k}` | `LABEL_NUMBER(k).value`, `LABEL_PAGE(k).value` | `CONTENT_VOLUME → LABEL_PAGE(k)` (LAYOUT, lag 0) |
| `\ref{k}` | `REF_USE(k)` | `LABEL_NUMBER(k) → REF_USE(k)` (AUX_ROUNDTRIP, lag 1) |
| `\pageref{k}` | `PAGEREF_USE(k)` | `LABEL_PAGE(k) → PAGEREF_USE(k)` (AUX_ROUNDTRIP, lag 1) |
| sectioning | `TOC_ENTRY(i).exists`, `.value` | `TOC_ENTRY(i).exists → LIST_EXTENT(toc)` (LAYOUT, lag 0); `LIST_EXTENT(toc) → CONTENT_VOLUME` (LAYOUT, lag 1) |
| `\caption` in `figure` / `table` | `LOF_ENTRY` / `LOT_ENTRY`, both components | as sectioning, with the corresponding list |
| `\cite{k}` | `CITE_USE(k)` | `CITE_USE(k) → BBL` (TOOL, lag 1) |
| `\bibliography{f}` | `BBL.exists`, `BBL.value` | `BBL.exists → CONTENT_VOLUME` (LAYOUT, lag 1) |
| `\value{c}` inside a control construct | `COUNTER_READ(c)` | seeds the taint worklist |
| `Opaque` node | `OPAQUE` fact | marks the containing file's facts unknown |

`CONTENT_VOLUME` is a single synthetic fact per document, representing pagination. Its source
location points at the first construct that made pagination sensitive to auxiliary state.

**Sectioning and `\caption` are gated by their list macro.** A `\chapter`/`\section`/`\caption`
always writes a potential list entry in real LaTeX (`\addcontentsline`), but that entry only
affects pagination once the corresponding list is actually typeset. `TOC_ENTRY`, `LOF_ENTRY`
and `LOT_ENTRY` facts -- and the `LIST_EXTENT`/`CONTENT_VOLUME` facts they would feed -- are
therefore produced **only when `\tableofcontents`, `\listoffigures` or `\listoftables`
(respectively) is present somewhere in the document forest**. A document with sectioning but no
`\tableofcontents` has no generated list at all, so `CONTENT_VOLUME` is never instantiated.
`\label` still always produces `LABEL_NUMBER(k).value` and `LABEL_PAGE(k).value` per the table
above, but the `CONTENT_VOLUME → LABEL_PAGE(k)` edge exists only when some construct elsewhere
in the document instantiates `CONTENT_VOLUME`; otherwise `LABEL_PAGE(k)` is a standalone fact
with no incoming edge. This is exactly IR.md's "backward reference, no generated lists" worked
example: a document with only `\label`/`\ref` lowers to two facts and one edge.

**Complexity.** One traversal of *n* source tokens plus construction of *V* facts and *E* edges:
**O(n + V + E)**. Space **O(V + E)**.

---

## 2. Content-quantity taint propagation

The step that separates benign feedback from amplifying feedback.

```
INPUT : ARG, AST
OUTPUT: taint : set[fact_id]; STRUCTURAL edges added to ARG

seeds <- { f : the value of f is read inside
                 - the condition or bound of a ControlConstruct, or
                 - an argument of \setcounter whose counter bounds such a construct, or
                 - a construct that directly emits page material (\newpage, \clearpage)
                   under the control of such a construct }

taint    <- seeds
worklist <- seeds
while worklist is not empty:
    f <- pop(worklist)
    for each edge (f -> g) in ARG with g.component == "value":
        if g not in taint:
            taint.add(g)
            worklist.push(g)

for each f in taint:
    add_edge(f -> CONTENT_VOLUME,
             pass_lag = 1,
             dependency_type = STRUCTURAL,
             reason = "value at <f.source_location> reaches a content-generating construct")
```

**Termination.** The lattice is the powerset of facts ordered by inclusion — finite, and `taint`
grows monotonically. Each fact is pushed at most once.

**Complexity.** Each fact enters the worklist at most once and each edge is examined at most
once: **O(V + E)** time, **O(V)** space.

**Direction.** Forward, from seeds along value-carrying edges. It answers "can this value reach
something that changes how much content exists", which is a reachability question, hence the
simplest possible formulation.

**Precision.** Deliberately coarse. Taint is propagated along any value edge without tracking
whether the influence is quantitative. This over-approximates, which is the safe direction: it
can classify a benign document as amplifying (a false positive, costing the user a flag) but
cannot miss a genuine amplifying cycle among modelled constructs.

**The seed rule is where the analysis is unsound, and the unsoundness is in the seeds, not the
propagation.** A value that is never read in a control construct is never seeded, so its influence on
pagination through *typeset extent* is invisible. Four published non-convergence mechanisms work
exactly that way and are not detected: reference width changing a line break; `[!t]` floats with
roman page numbering; `varioref`-style dynamic textual references; references in margin or foot
notes. See [NON-CONVERGENCE.md](NON-CONVERGENCE.md) and
[RELATED-WORK.md](RELATED-WORK.md) section 7.3.

Widening the seed rule to "any value rendered into the document body" would catch them and would
also make every document containing one `\ref` a single strongly connected component, which is
vacuous. That trade-off is **open decision D13** in [PROJECT.md](PROJECT.md) and is the most
consequential unresolved question in the design. It must be argued in the report, not assumed.

---

## 3. SCC detection

**Tarjan's algorithm, iterative.** A recursive implementation will exhaust the interpreter stack
on the realistic corpus member; use an explicit stack from the start rather than discovering
this later.

Output: components in reverse topological order — which is exactly the order stable-pass
numbering needs, so no separate topological sort is required.

Concretely: for an ARG edge `u -> v` (`u` is a dependency of `v`), Tarjan's natural emission
order places `v`'s component before `u`'s -- this is what "reverse topological order" means
here. Section 4's recurrence needs the opposite -- each fact's dependencies computed before the
fact itself -- so the condensation (below) presents components in the reverse of this list.
That reversal is the "no separate topological sort" referred to above: a single `O(V)` list
reversal of output Tarjan already produced, not a second graph traversal.

**Complexity.** **O(V + E)** time, **O(V)** space.

**Testing note.** SCC detection is testable on synthetic graphs with no LaTeX involved. It is
the cheapest phase to get right and should be implemented before the taint analysis.

### Cycle classification

```
for each SCC C where |C| > 1, or |C| == 1 with a self-loop:
    if any edge internal to C has type == STRUCTURAL:
        label(C) <- AMPLIFYING
    elif any fact in C is opaque:
        label(C) <- UNKNOWN_CYCLE
    else:
        label(C) <- BENIGN
```

---

## 4. Stable-pass numbering

Computed on the **condensation**, which is why cycles cannot cause non-termination.

```
cond <- condensation(ARG)          # available from Tarjan, in reverse topological order

for each component C in topological order:
    if label(C) in {AMPLIFYING, UNKNOWN_CYCLE}:
        for f in C:
            stable_pass[f] <- None                    # not bounded

    elif |C| > 1:                                     # BENIGN cycle
        base <- 1 + max(stable_pass[g] for g in preds(C) if bounded, default 0)
        for f in C:
            stable_pass[f] <- base + |C|              # HEURISTIC -- see below

    else:
        f <- the single member of C
        if preds(f) is empty:
            stable_pass[f] <- 1
        elif any pred of f is unbounded:
            stable_pass[f] <- None
        else:
            stable_pass[f] <- 1 + max(stable_pass[g] + lag(g, f) - 1
                                      for g in preds(f))

P <- max(stable_pass values that are bounded, default 0)
predicted_runs <- P + 1
```

**Complexity.** Longest path over a DAG visited in topological order: **O(V + E)** time,
**O(V)** space.

**Whole-analysis complexity.** Lexing and parsing *n* bytes plus the four steps:
**O(n + V + E)** time, **O(V + E)** space.

### The benign-cycle bound is a heuristic, and is flagged as such

`base + |C|` is a *heuristic*, not a proof. It is plausible for the list-and-pagination feedback
being modelled, where one traversal of the cycle stabilises one fact, but it is not established
in general. This is **open decision D7** in [PROJECT.md](PROJECT.md).

If measurement shows it mispredicting, the correct response is to reclassify benign cycles as
unbounded and defer to runtime verification. That is strictly more conservative: it costs
prediction sharpness, never correctness.

**Do not fit the constant to the corpus.** Tuning a bound until it matches the benchmark is
fitting to the test set, and it would invalidate the evaluation.

---

## Guarantees

Within the declared subset and under the assumptions below:

- **G1 — sound extraction.** Every dependency induced by a construct in the subset appears as an
  edge in the ARG.
- **G2 — exact cycle reporting.** Every strongly connected component of the constructed graph is
  found and reported. Tarjan is exact.
- **G3 — well-defined numbering.** If the graph is acyclic, `stable_pass` is defined for every
  fact and equals the longest weighted path to that fact.
- **G4 — opacity blocks certification.** A document containing any opaque construct is never
  classified certified.
- **G5 — no unsafe shortening.** The emitted plan is never shorter than the conservative default
  unless the document is certified. Enforced by a property test.

### Theorem

> Let *D* be a document all of whose constructs lie in the declared subset. Let *G* be the ARG
> and *T* the taint set. Then (i) every dependency induced by a construct of the subset is an
> edge of *G*; (ii) if *G* is acyclic, `stable_pass` is the unique least solution of the
> recurrence; (iii) *D* is classified certified only if *G* is acyclic and no fact is opaque;
> (iv) every SCC containing a `STRUCTURAL` edge is reported as amplifying.

*Proof sketch.* (i) Structural induction over the AST: the lowering rules are exhaustive over
subset constructs, and the fallback maps every non-subset construct to an opaque fact, so no
construct contributes an unrecorded dependency. (ii) On a DAG the recurrence is a longest-path
computation; topological order evaluates each node after all its predecessors, and monotonicity
with a finite node set gives a unique least fixpoint. (iii) By the definition of the classifier
together with G4. (iv) Tarjan enumerates all SCCs exactly and the classifier inspects every
intra-component edge.

**This theorem is about the analysis, not about the engine.** It states that AuxFlow correctly
analyses its own model. Whether the model predicts real engine behaviour is assumption A2, and
A2 is empirical.

## Assumptions

- **A1 — auxiliary round trip.** A fact written during run *k* is first readable during run
  *k+1*. **Faithful, and now sourced from the LaTeX kernel.** `ltfiles.dtx` shows `\document`
  executing `\@input{\jobname.aux}` *before* `\immediate\openout\@mainaux\jobname.aux`, so the
  `\r@…` values live during run *k* are exactly the records written during run *k−1*. Note one
  asymmetry the same file establishes: the aux read executes `\let\@writefile\@gobbletwo`, so
  `\newlabel` records survive into memory while `.toc`, `.lof` and `.lot` records are discarded and
  re-read at their insertion point. The two fact families therefore need different normalisation
  (open decision D6).
- **A2 — pagination stability under value substitution.** Replacing an unresolved reference with
  its resolved value does not alter pagination. **Not faithful, and known false for a published
  class.** A short placeholder becoming a longer number can change a line break and therefore a
  page break. Four reproducible counterexamples exist — see N6 and
  [RELATED-WORK.md](RELATED-WORK.md) section 7.3. Without A2 the entire document is one strongly
  connected component and the analysis is vacuous, so the choice is between a vacuous analysis and
  an analysis that is unsound for a named class. AuxFlow takes the second and reports the class.
  Any ground-truth run count exceeding the prediction is an A2 violation and must be reported as
  one; any document in the named class that is classified convergent is a *declared* false negative,
  not a discovered one.
- **A3 — modelled packages are complete.** A package in the package table produces only the fact
  kinds recorded for it. Violations surface as prediction misses. A3 is doing more work than it
  looks: `biblatex`'s same-page `ibid` feedback is a real non-convergence mechanism, and it is safe
  only because `biblatex` is unmodelled. Modelling it naively — as `CITE_USE` and `BBL` facts without
  the same-page feedback edge — would introduce a false negative.
- **A4 — external tool lag.** An external tool consumes the state of run *k* and its output is
  visible in run *k+1*. Exact semantics is open decision D5.

## Non-guarantees

- **N1.** That a certified bound matches the real engine. This rests on A2 and is validated
  empirically, not proved.
- **N2.** That an amplifying classification proves divergence. It establishes a *necessary*
  structural condition for the known counterexample class, not a sufficient one.
- **N3.** Anything about documents outside the subset, beyond G4 and G5.
- **N4.** Minimality. A certified bound may exceed the true requirement. This is not a defect to be
  fixed later: constructing a minimum-pass evaluation order is NP-complete (Räihä and Ukkonen,
  *SIAM J. Comput.* 10(4):772–786, 1981), and the standard construction can use `2n−1` passes where
  `n` suffice.
- **N5.** Anything about engine termination.
- **N6.** **That the absence of a structural cycle implies convergence.** Four published mechanisms
  are non-convergent and produce no structural edge, because they act through typeset extent rather
  than through content quantity. An ARG cycle is neither necessary nor sufficient for
  non-convergence. This is a declared incompleteness with named corpus members, not an open bug.
- **N7.** That the analysis is exact rather than approximate. Instance-level pass numbering is
  Alblas's *pure* multi-pass setting, and deciding pure multi-pass membership is of inherently
  exponential time complexity (Engelfriet and Filè). Circularity testing for *remote* reference
  attribute grammars — the class LaTeX's `\ref`/`\pageref` belongs to — is undecidable (Boyland,
  *JACM* 52(4), 2005). AuxFlow computes a conservative approximation over a restricted subset, and
  the `UNKNOWN` verdict is theoretically forced rather than an engineering convenience.

## Empirical claim

Because A2 is not faithful, the practically interesting property is measured rather than proved:

> **EC1.** On the benchmark corpus, for every document classified certified with bound *N*, the
> experimentally determined ground-truth run count *N\** satisfies *N ≥ N\**.

EC1 is the gate at the end of implementation phase 9. If it fails, the fallback of open decision
D7 applies and the failing document becomes a case study in the report — a legitimate result
about where A2 breaks, not a project failure.
