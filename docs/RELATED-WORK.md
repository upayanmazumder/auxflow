# Related work

Prior art is conceded first and claims are made afterwards. A reviewer who discovers an
anticipation after reading an over-claiming introduction will discount everything else; one who
finds it cited in the first section will credit what remains.

This document was rewritten after the prior-art audit of 2026-08-27. Raw evidence, with search
logs, exact queries and verbatim quotes, is in [`research/sources/`](../research/sources/) and is
indexed in [`research/prior-art-log.md`](../research/prior-art-log.md).

**Verification status** is recorded per item. `SOURCED` means the primary source was opened and the
quoted text read directly. `REPORTED` means second-hand and not yet confirmed. `INFERENCE` means
analysis by the project. Nothing marked `REPORTED` may be used to support a claim in a report.

**The audit changed the project's position materially.** Five things the previous version of this
document treated as contributions are anticipated, and two stated hypotheses are wrong. Those
findings are in [section 8](#8-what-the-audit-removed) and are not buried.

---

## 1. Static pass-number analysis is established prior art

**AuxFlow does not claim to have invented static pass-number assignment.**

| Work | Substance | Status |
|---|---|---|
| Bochmann, "Semantic evaluation from left to right", *CACM* 19(2):55–62, 1976, DOI `10.1145/359997.359999` | Gives a single-pass evaluability condition for attribute grammars, and "an algorithm is discussed which decides how many passes from left to right are in general necessary, given the attribute grammar" | SOURCED |
| Alblas, "A characterization of attribute evaluation in passes", *Acta Informatica* 16(4):427–464, 1981, DOI `10.1007/BF00264495` | Graph-theoretic characterisation of multi-pass evaluability; "new algorithms are developed that associate minimal pass numbers with attributes"; coins the *simple* / *pure* distinction, where pure imposes "no requirement that all occurrences of the same attribute are computed in the same pass" | SOURCED |
| Räihä and Ukkonen, "Minimizing the Number of Evaluation Passes for Attribute Grammars", *SIAM J. Comput.* 10(4):772–786, 1981, DOI `10.1137/0210060` | Minimum-pass assignment is **NP-complete**; the standard construction can use `2n−1` passes where `n` suffice | SOURCED |
| Räihä and Ukkonen, "On the optimal assignment of attributes to passes in multi-pass attribute evaluators", ICALP 1980, LNCS 85:500–511, DOI `10.1007/3-540-10003-2_94` | The conference version of the above, under a different title | SOURCED |
| Engelfriet and Filè, "Passes and paths of attribute grammars" / "Simple multi-visit attribute grammars", 1981–1982 | Bochmann's class is *simple multi-pass*, decidable in polynomial time. Deciding **pure** multi-pass membership is of inherently exponential time complexity; polynomial only for fixed *k*. The characterisation is in terms of paths through dependency graphs | SOURCED |

### Bibliographic correction, adopted

The citation *"Räihä and Ukkonen, 'Minimizing the number of evaluation passes for attribute
grammars', ICALP 1980, LNCS 85, pp. 500–511"* — which the previous version of this document carried
— **conflates two distinct papers**. The venue, pages and year belong to the ICALP paper; the title
belongs to the 1981 SIAM journal paper. The error is traceable to Alblas 1981's own reference list,
which cites the ICALP paper under the title of the SIAM submission then in review (SOURCED: the
Springer landing page for `10.1007/BF00264495` exposes Alblas's reference list in its
`citation_reference` metadata). AuxFlow cites the SIAM paper, because that is where the
NP-completeness result is. Reproducing the conflated citation is a visible error to any reviewer who
knows this literature.

### Consequences AuxFlow must accept

1. **Pass numbering is not a contribution.** It is 1976 work.
2. **Instance-level pass numbering is not a refinement AuxFlow invented; it is Alblas's *pure*
   multi-pass setting, and it is the computationally hard one.** Deciding pure multi-pass membership
   is inherently exponential (Engelfriet and Filè). AuxFlow's move from fact kinds to fact instances
   is therefore not a design insight — it is a named 1981 problem class. AuxFlow owes either a
   restriction argument or an explicit statement that it computes a conservative approximation.
3. **No minimality claim is available.** Minimum-pass assignment is NP-complete (Räihä and Ukkonen).
   Limitation L4 in [PROJECT.md](PROJECT.md) is now sourced rather than cautionary.

---

## 2. Circular attribute grammars: the fixpoint machinery, and the framework AuxFlow instantiates

This is the section that matters most, and it did not exist in the previous version of this
document.

| Work | Substance | Status |
|---|---|---|
| Farrow, "Automatic generation of fixed-point-finding evaluators for circular, but well-defined, attribute grammars", *SIGPLAN Notices* 21(7):85–98, 1986, DOI `10.1145/13310.13320` | "This paper presents constraints on individual attributes and semantic functions of an AG that are sufficient to guarantee that a circular AG specifies a well-defined translation and that circularly-defined attribute-instances can be computed via successive approximation." The generated evaluators "are static in the sense that the order of evaluation at each production-instance in the derivation-tree is determined at the time that each translator is generated". "A final algorithm is presented that tells which individual attributes and functions must satisfy the constraints." | SOURCED (abstract) |
| Jones, "Efficient evaluation of circular attribute grammars", *TOPLAS* 12(3):429–462, 1990, DOI `10.1145/78969.78971` | "The algorithms are derived from those for noncircular attribute grammars by partitioning the underlying attribute dependency graph into its strongly connected components and by ordering the evaluations to follow a topological sort of the resulting directed acyclic graph." Works "under any conditions that guarantee finite convergence". Degenerates to the standard optimal algorithm when acyclic | SOURCED (abstract) |
| Magnusson and Hedin, "Circular reference attributed grammars — their evaluation and applications", *Science of Computer Programming* 68(1):21–37, 2007, DOI `10.1016/j.scico.2005.06.005` | States the convergence condition exactly, and admits nobody checks it. See below | SOURCED (preprint read in full) |
| Rodeh and Sagiv, on finding which attributes are on cycles, *JACM* 46(4), 1999 | Polynomial conservative approximation plus an exact exponential algorithm; **finding the circular attributes is strictly harder than testing for circularity** | SOURCED via Magnusson and Hedin §2.1 |
| Boyland, on remote attribute grammars, *JACM* 52(4), 2005 | Circularity testing for **remote** (reference) attribute grammars is **undecidable** | SOURCED via two citing primary sources |

### The convergence condition, quoted

Magnusson and Hedin, §1, verbatim:

> "It suffices that all attributes involved in cyclic dependencies have a fixed point that can be
> computed with a finite number of iterations. […] This is guaranteed if the values for each
> attribute on a cycle can be organized in a lattice of finite height and if all the semantic
> functions involved in computing these attributes are monotonic on the respective lattices."

with the footnote refinement: "More precisely it is sufficient that the domain of the attributes
forms a complete partial order and that the semantic functions satisfy the ascending chain
condition." And a refinement AuxFlow should adopt, §2.2:

> "If two strongly connected components are evaluated in topological order, the dependency between
> the components does not need to be monotonic."

### The admission that defines the remaining gap

Magnusson and Hedin, §3.5, verbatim:

> "Our evaluator presently does not check whether circularly defined attributes take their values
> from a lattice of finite height or if their defining semantic functions are monotonic. Thus there
> is no guarantee that iterations will converge. Our approach is in this respect similar to that of,
> e.g., Farrow […] and means that we rely on the AG author to ensure that the semantic functions
> involved are properly constrained."

So: Farrow's final algorithm **allocates** the convergence obligation. Jones **assumes** it.
Magnusson and Hedin **do not check** it, and say so, with Farrow named. No work in this line
performs a static decision procedure separating cycles that settle from cycles that may not. That
absence is the space AuxFlow occupies, and it is narrow.

### What must be conceded outright

The sentence "AuxFlow finds strongly connected components with Tarjan's algorithm and propagates a
stable pass number by monotone fixpoint over the graph condensation" **describes Jones 1990 with
the words changed.** It is standard technique and must be cited, not presented as design.
Independently, SCC decomposition of a dataflow problem followed by fixpoint iteration over the
condensation is documented prior art from Sharir, "A Strong-Connectivity Algorithm and Its
Applications in Data Flow Analysis", 1981 — cited on the face of a granted US patent (SOURCED; see
[PATENT-NOTES.md](PATENT-NOTES.md)).

### The one place the classical theory does not reach

In an attribute grammar the derivation tree is fixed before attribute evaluation, so the set of
attribute instances — and hence the dependency graph — is invariant across iterations. In a
document it is not: a fact value can change the page count, which changes how many `\pageref`
instances exist, which changes the graph. **The fixpoint is over a space whose dimension is itself
a function of the iterate.** Farrow, Jones and Magnusson and Hedin do not cover this.

This is the correct framing for AuxFlow's benign/amplifying split. It is *not* "we classify cycles"
— that is Farrow. It is **"we decide whether the classical fixed-graph fixpoint theory applies to
this document at all."** (INFERENCE, but grounded in the sourced quotes above.)

---

## 3. Higher-order attribute grammars: the nearest neighbour, and the claim that had to be withdrawn

The previous version of this document asserted that AuxFlow's setting "has no analogue in the
attribute-grammar setting because grammars cannot generate themselves". **That is false and the
claim is withdrawn.**

| Work | Substance | Status |
|---|---|---|
| Vogt, Swierstra and Kuiper, "Higher order attribute grammars", PLDI 1989 | Removes the restriction. Per Swierstra and Vogt 1991, verbatim: HAGs are an extension "in the sense that the distinction between the domain of parse-trees and the domain of attributes has disappeared: parse trees may be computed in attributes and grafted to the parse tree at various places" | SOURCED via Swierstra and Vogt 1991 |
| Vogt et al. 1989, on well-definedness | A well-defined HOAG must be complete, non-circular, *and* create "a finite number of new trees during attribute evaluation"; "attribute evaluation for a complete, non-circular HOAG may not terminate since creating an unbounded number of trees during higher-order attribute evaluation can lead to non-termination" | SOURCED via Krishnan and Van Wyk 2012; the PLDI text is REPORTED and **must be read directly** |
| **Krishnan and Van Wyk, "Termination Analysis for Higher-Order Attribute Grammars", SLE 2012, LNCS 7745:44–63, DOI `10.1007/978-3-642-36089-3_4`** | **A conservative static analysis whose sole purpose is to decide whether attribute evaluation that generates new content to be evaluated terminates.** It explicitly separates that question from circularity: "This type of non-termination is not detected by a circularity analysis for higher-order attribute grammars." It uses SCC condensation of a non-terminal graph as its scheduling device. It is openly conservative: "there are terminating grammars for which the analysis fails." Validated on a full attribute grammar for a real language | SOURCED (abstract and related-work section) |
| Söderberg and Hedin, "Circular Higher-Order Reference Attribute Grammars", SLE 2013, LNCS 8225:302–321, DOI `10.1007/978-3-319-02654-1_17` | Abstract, verbatim: "In this previous work, dependencies between circular attributes and rewrites are not considered. In this paper, we investigate how these extensions can interact, and still be well defined. We introduce a generalized evaluation algorithm that can handle grammars where circular attributes and rewrites are interdependent." | SOURCED (abstract) |
| Riouak, Fors, Öqvist, Hedin and Reichenbach, SLE 2024 (Distinguished Paper), DOI `10.1145/3687997.3695644` | "a static meta-analysis that identifies" attributes that "can never be circular", so the fixpoint machinery can be skipped — i.e. a static `CERTIFIED`-versus-cyclic partition, in the same formalism, with measured speedups | SOURCED (abstract) |

**Krishnan and Van Wyk 2012 is the single most dangerous piece of prior art found in the entire
audit.** It is a conservative static termination analysis for the case where evaluation generates
more work to evaluate; it is explicitly distinguished from circularity analysis; and it uses SCC
condensation. That is AuxFlow's amplifying analysis, in a different formalism, in 2012.

Söderberg and Hedin 2013 names AuxFlow's exact configuration — circular attributes interdependent
with tree changes — and gives a well-definedness account for it.

**AuxFlow's remaining differentiator against this line is a matter of formulation, and it is
narrow.** Krishnan and Van Wyk reason about *rewriting*: how many new trees a production can create.
AuxFlow reasons about *influence*: whether a value can reach a construct that governs content
quantity. Krishnan and Van Wyk themselves note that theirs is the first to use "the structure of the
equations and not just the attribute dependencies", which is adjacent to but not the same as a taint
analysis. **Whether even this survives is contingent on reading both papers in full.** Until that is
done, no novelty claim about the amplifying analysis may appear in a report.

---

## 4. Statically bounding fixpoint iteration in compilers

| Work | Substance | Status |
|---|---|---|
| Hecht and Ullman, "A Simple Algorithm for Global Data Flow Analysis Problems", *SIAM J. Comput.* 4(4):519–532, 1975, DOI `10.1137/0204044` | Defines loop-connectedness *d*: "if G is an rfg, d is the largest number of back edges found in any cycle-free path in G". Relates it to the round count of reverse-postorder round-robin iteration on a **reducible** flow graph | SOURCED (abstract) |
| Kam and Ullman, "Global data flow analysis and iterative algorithms", *JACM* 23(1):158–171, 1976, DOI `10.1145/321921.321938` | The rapidity precondition for the bound, and the observation that useful analyses can fail it | SOURCED |
| Kam and Ullman, "Monotone data flow analysis frameworks", *Acta Informatica* 7(3):305–317, 1977, DOI `10.1007/BF00290339` | Generalisation to merely monotone frameworks; MFP versus MOP. Metadata SOURCED; contribution REPORTED, no abstract deposited | REPORTED |
| Ullman, Dragon Book lecture notes, Stanford InfoLab | "The depth of a flow graph is the greatest number of retreating edges along any acyclic path"; "if we use DF order to visit nodes, we converge in depth+2 passes"; "Depth+1 passes to follow that number of increasing segments" / "1 more pass to realize we converged"; "The depth+2 bound works for any monotone framework, as long as information only needs to propagate along acyclic paths" | SOURCED |

**AuxFlow's build plan is literally "N passes to propagate, one more to confirm", and a co-author of
the original result states that decomposition as settled undergraduate pedagogy.** Deriving the
number of fixpoint rounds from a structural parameter of the dependency graph is a fifty-year-old
textbook result. AuxFlow must cite Hecht and Ullman 1975 and Kam and Ullman 1976, and must not
present static pass-count derivation as its own.

Note on constants: `d+2` and `d+3` both circulate, differing on whether the initialisation and
confirming passes are counted. AuxFlow must not quote either as canonical without stating the
convention.

---

## 5. Data-dependent rates: the structural analogue of AuxFlow's central distinction

| Work | Substance | Status |
|---|---|---|
| Lee and Messerschmitt, "Static Scheduling of Synchronous Data Flow Programs for Digital Signal Processing", *IEEE Trans. Computers* C-36(1):24–35, 1987, DOI `10.1109/TC.1987.5009446` | "Synchronous data flow (SDF) differs from traditional data flow in that the amount of data produced and consumed by a data flow node is specified a priori […] This means that the scheduling of SDF nodes need not be done at runtime, but can be done at compile time (statically)." A node whose output rate depends on data "is an asynchronous node because it is not possible to specify a priori how many samples will be produced on each output when the node is invoked" — and it leaves the model | SOURCED (full text) |
| Lee and Messerschmitt, "Synchronous data flow", *Proc. IEEE* 75(9):1235–1245, 1987, DOI `10.1109/PROC.1987.13876` | Companion tutorial | Metadata SOURCED, content REPORTED |

**SDF's dividing line is AuxFlow's dividing line, stated in 1987 in full generality:** can a value
determine *how many* firings occur, or only *what* they compute? AuxFlow's `BENIGN_CYCLIC` is the
fixed-rate case; `AMPLIFYING` is the data-dependent-rate case. The distinction is anticipated; only
its instantiation in a document build is not.

Two things AuxFlow should borrow rather than re-invent:

1. **Separate the failure modes.** SDF separates *rate inconsistency* (rank of the topology matrix
   ≠ *s*−1; no bounded schedule exists at any period) from *deadlock* (insufficient initial tokens
   in a directed loop). Two independent static failure modes is a better-factored taxonomy than
   AuxFlow's single `AMPLIFYING` label. See [section 7](#7-two-failure-modes-not-one).
2. **Data-dependent *runtime* is benign; data-dependent *rate* is fatal.** That is exactly
   AuxFlow's `exists`/`value` split, and SDF is a citable precedent for making it.

---

## 6. Build-system theory: the static/dynamic gap is the field's organising axis

| Work | Substance | Status |
|---|---|---|
| Mokhov, Mitchell and Peyton Jones, "Build systems à la carte", ICFP 2018, DOI `10.1145/3236774`; JFP 2020, DOI `10.1017/S0956796820000088` | A *type-level* distinction: `Task Applicative` dependencies are determinable statically "by looking at the formulae, without 'computing' them"; `Task Monad` dependencies are "determined by values of intermediate computations". Names LaTeX's category as "bistable or diverging" without offering any means to detect it. Notes that some frameworks support cycles "under the assumption that tasks are monotonic in a certain sense" — assumed, never verified | SOURCED |
| Erdweg, Lichter and Weiel, "A sound and optimal incremental build system with dynamic dependencies" (Pluto), OOPSLA 2015, DOI `10.1145/2814270.2814316` | See below | SOURCED |
| Mitchell, "Shake before building", ICFP 2012, DOI `10.1145/2364527.2364538` | Dynamic dependencies in a practical build system | SOURCED |
| Miller, "Recursive Make Considered Harmful", 1998 | For multi-pass recursive Make, "there is no guarantee that two passes are enough! The upper bound of the number of passes […] is proportional to the number of graph edges which cross module boundaries" | SOURCED |
| GNU Make, makefile-remaking restart | Make "starts with a clean slate and reads all the makefiles over again", counts restarts in `MAKE_RESTARTS`, and documents **no bound at all** | SOURCED |
| Bazel include scanning | Shipped as `--experimental_unsupported_and_brittle_include_scanning`, default off, documented as breaking builds: "the include scanner does not fully implement C preprocessor semantics. In particular, it does not understand dynamic #include directives and ignores preprocessor conditional logic. Use at your own risk. Any issues relating to this flag that are filed will be closed." | SOURCED |

**AuxFlow must not frame the static-versus-dynamic dependency gap as an unstudied observation.** It
is the organising axis of the field's canonical paper.

**Pluto is dangerous on four axes at once, and the title conceals it.** Its running example is a
LaTeX and BibTeX builder. It identifies the auxiliary self-cycle explicitly — "the Latex builder is
in a cycle by itself because it reads from and writes to the same aux file" — and the LaTeX/BibTeX
cycle. It ships a `FixpointCycleHandler` that iterates a cycle to stability, with the printed
disclaimer that it "does not guarantee a fixpoint will be reached. The builders in the cycle need to
be designed to take part in a fixpoint compilation." And its BibTeX builder uses "a custom stamper
that parses the aux file, extracts the bibliography name and the set of referenced citation keys,
and uses them as a stamp" — **sub-file, semantic, fact-level dependency granularity on auxiliary
content.** AuxFlow's instance-level fact granularity is therefore not novel as an idea; only its
static derivation from source is.

**The sharpest single sentence in the build-systems literature, and AuxFlow must answer it in the
first two pages.** Pluto §3.3: *"In the case of Latex where even parsing is undecidable [4], soundly
detecting dependencies is a lost cause."* Reference [4] is Erdweg and Ostermann, "Featherweight TeX
and Parser Correctness", SLE 2010, DOI `10.1007/978-3-642-19440-5_26`. This is not an oversight to
exploit; it is a considered rejection, published at OOPSLA, by an author who had already written the
formal paper on TeX parsing. AuxFlow's only available answer is the declared subset, and that answer
is credible only if the subset is specified precisely and every escape from it maps to `UNKNOWN`.

Bazel is the industry-scale cautionary tale for AuxFlow's method: Google built "parse the source to
predict the build graph" for C and C++, and the documented failure modes — conditionals and computed
filenames — map one-to-one onto LaTeX conditionals and macro-computed `\input` arguments.

No build-system work classifies cyclic build dependencies as benign versus divergent. Pluto is the
only build system with first-class cycle support and it explicitly refuses to classify.

---

## 7. Document compilation, non-convergence, and the mechanism taxonomy

### 7.1 The mechanics, now sourced from the LaTeX kernel

The auxiliary round trip and the rerun warning are established from primary source rather than from
memory (all SOURCED, from `latex3/latex2e`):

- `ltxref.dtx`: `\label{FOO}` writes one `\newlabel` record carrying five components (counter
  representation, page, label name, hyperref target, reserved kernel slot); `\ref` reads only the
  macro `\r@<key>` and typesets `??` with a warning when it is undefined.
- `ltfiles.dtx`: `\begin{document}` executes `\@input{\jobname.aux}` **before** reopening the file
  for writing. This is the mechanical proof of AuxFlow's pass lag of exactly 1. It also shows an
  asymmetry AuxFlow must model: `\newlabel` records survive into the next run's memory, whereas
  `\@writefile` records (`.toc`, `.lof`, `.lot`) are gobbled at read time
  (`\let\@writefile\@gobbletwo`).
- `ltmiscen.dtx`: `\enddocument` rebinds `\@newl@bel` to `\@testdef`, re-inputs the auxiliary file,
  and emits "Label(s) may have changed. Rerun to get cross-references right" from a single global
  boolean. The kernel comment states the warning is deliberately **suppressed** when labels are
  multiply defined.
- `rerunfilecheck` (LaTeX Project Team / Oberdiek, v1.11): "Checksum based rerun checks on auxiliary
  files"; "provides additional rerun warnings if some auxiliary files have changed"; its `.dtx`
  states explicitly that base LaTeX's rerun warnings "are not given for the table of contents and
  other data stored in the aux files or other auxiliary files".

### 7.2 Non-convergence is published, in two distinct modes

Gaspar, "Does not suffice to run latex a finite number of times to get cross-references right",
*TUGboat* 35:1 (2014), p. 16, in the **Letters** section, one page, indexed "Introductory — simple
counterexample" (SOURCED, read in full):

> "We present a LATEX file such that a cross-reference is wrong no matter how many times we run
> latex."

The mechanism is `\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}` with `\label{l}` after the
loop: the loop emits `\pageref{l}` pages, so the document has `\pageref{l}`+1 pages. The recorded
value therefore increases by exactly one every run. **This is monotone divergence, not
oscillation.** Gaspar also points at `tex.stackexchange.com/questions/30674` for "an even more
diabolical counterexample that avoids a for loop", and that thread supplies **period-2 oscillation
with no loop and no conditional at all** (SOURCED, read in full).

The TeX FAQ entry "Rerun messages won't go away" independently documents a roman-numeral
page-number case that oscillates and states that "such a sequence can obviously not terminate"
(SOURCED).

### 7.3 The mechanism taxonomy, and what AuxFlow's criterion misses

Nine distinct mechanisms are identified and sourced in
[`research/sources/area-d-non-convergence.md`](../research/sources/area-d-non-convergence.md),
Part 3. Summarised:

| Mechanism | Behaviour | Caught by AuxFlow's taint seeds? |
|---|---|---|
| M1 loop bounded by a page reference to a label inside the generated material | monotone divergence | **yes** — the motivating case |
| M2 conditional selecting differently sized content on a page reference | period-2 oscillation | **yes**, but only by over-approximation; no content quantity changes |
| M3 typeset *width* of a resolved reference changes a line break, hence a page break | period-2 oscillation, no loop, no conditional | **no** |
| M4 `[!t]` float plus roman page numbering | period-2 oscillation | **no** |
| M5 citation style selecting a shorter form when the previous citation is on the same page (`biblatex` `ibid`) | period-2 oscillation | only by refusal, via the opaque-package rule |
| M6 dynamic textual references (`varioref`) whose length moves the floats they refer to | oscillation | **no** |
| M7 references in margin or foot notes | oscillation | **no** |
| M8 a non-deterministic generated auxiliary file (e.g. an `.eps` carrying a timestamp) | unbounded rerun with no cross-reference cause | **no**, and out of model |
| M9 active characters in captions defeating the kernel's own change test | *not* real non-convergence — a false positive of `\@testdef` | n/a |

M6 and M7 are taken verbatim from the `labelschanged` documentation, which is a first-party taxonomy
of causes maintained on CTAN (SOURCED). M8 is from the `latexmk` manual (SOURCED). M9 matters
because it shows the engine's own oracle has false positives as well as false negatives.

### 7.4 An ARG cycle is neither necessary nor sufficient for non-convergence

*Not sufficient* is known: ordinary documents are cyclic and converge. The `latexmk` manual states
it directly (SOURCED): "This situation, of circular dependencies, is endemic to latex, and is one of
the issues that latexmk is programmed to overcome." latexrun independently draws the cyclic graph of
`latex` and `bibtex` with `.aux`, `.toc` and `.bbl` feedback edges and states that its goal is to
find its fixed point.

*Not necessary* is new to the project and adverse. M3, M4, M6 and M7 are genuinely non-convergent
and produce **no cycle in the ARG as specified**, because [IR.md](IR.md)'s `exists`/`value` split
severs the extent-feedback edge by construction. That split *is* assumption A2, and A2 is false for
a published, reproducible class of documents.

**The dichotomy must be stated in the report, not buried.** Either `CONTENT_VOLUME` depends on every
`.value` rendered into the body — in which case every document containing one `\ref` is a single SCC
and the analysis is vacuous — or it does not, in which case the analysis is unsound for the
extent-driven class. There is no third option available to a static analysis that does not model
line breaking. AuxFlow takes the second option. That is defensible only if the excluded class is
named, given a corpus member, and reported as a measured false negative.

### 7.5 Two failure modes, not one

M1 is monotone but unbounded: it violates the **finite-height** half of the Magnusson and Hedin
condition. M2, M3 and M4 alternate: they violate the **monotonicity** half. A single `AMPLIFYING`
label conflates two different failures with different causes and different diagnostics. Splitting it
is a small, honest refinement that follows directly from the sourced convergence condition, and it
mirrors SDF's separation of rate inconsistency from deadlock.

---

## 8. What the audit removed

Recorded prominently because the previous version of this document claimed some of it.

1. **"No prior work distinguishes cycles that move values from cycles that change how much content
   exists."** Withdrawn. Krishnan and Van Wyk 2012 is a conservative static termination analysis for
   exactly the content-generating case; Vogt et al. 1989 made finite tree creation a
   well-definedness condition; SDF 1987 draws the fixed-rate versus data-dependent-rate line in full
   generality; and US8181129B2 classifies SCCs by a semantic property of the circulating values and
   notifies the user of the bad ones.
2. **"In classical AGs no attribute value alters the shape of the derivation tree, and this is what
   makes our setting different."** The first clause is true of Knuth-classical AGs. The second is
   false: higher-order attribute grammars removed that restriction in 1989.
3. **"Existing tools exhaust a retry cap and report only that they gave up."** True of `latexmk` and
   ConTeXt. **False** of Tectonic (names the file that changed), `labelschanged` (names the offending
   label instances with before and after values) and Typst (names the fact, gives a byte span, gives
   the full per-iteration value history, and adds a second span for the element that produced the
   unstable value).
4. **H3, "the gap being exactly one execution."** Falsified. latexrun's README states AuxFlow's own
   argument and then engineers around it (SOURCED, verbatim): "A direct approach could be to check
   the output of latex and bibtex after each run and stop when the output is the same from one run to
   the next. This works, but runs latex too many times; it will have already produced its final
   output one iteration before this approach can figure out that it's done. Instead, latexrun models
   latex and bibtex as deterministic functions of the file system state […] Hence, if the *inputs* to
   latex and bibtex do not change over one iteration, then latexrun can guarantee that the output
   also will not change, and stop." Tectonic independently avoids the extra run by comparing files
   the engine "read and then rewrote" **within** a single run. The extra run is a property of
   *output*-comparison detectors, not of dynamic detection. Baseline C as specified is a strawman
   unless latexrun and Tectonic are added as baselines.
5. **H1's "zero false negatives" form.** Falsified in advance by mechanisms M3, M4, M6 and M7 unless
   the corpus is restricted to modelled mechanisms and the restriction is declared.
6. **"Compute the number of iterations from the graph" as anything but conceded prior art.**
   Confirmed anticipated academically (1975, 1976) and in a granted, active patent.
7. **The undecidability observation.** `latexmk`'s own source says it (SOURCED): "It is impossible
   for an algorithm to determine in general whether there is an infinite loop. (An example of the
   Turing halting theorem.)" Mädje's thesis proves it via Rice's theorem for document introspection.
   AuxFlow may not present it as an insight.

---

## 9. The deployed convergence oracles

Five independent systems, five different oracles, five hand-chosen caps, no derivation anywhere. All
SOURCED from manuals and source code; details in
[`research/sources/area-c-latex-tools.md`](../research/sources/area-c-latex-tools.md) and
[`research/sources/tex-ecosystem-convergence-machinery.md`](../research/sources/tex-ecosystem-convergence-machinery.md).

| System | Oracle | Cap | Cause reported on cap exhaustion |
|---|---|---|---|
| `latexmk` 4.88 | `(time, size, md5)` database over every file in the rule network; engine `Rerun to get` warning as secondary trigger | `$max_repeat`, documented default `5` | none: `Maximum runs of <rule> reached without getting stable files` |
| latexrun | tool **inputs** unchanged over one iteration — avoids the redundant run by construction | none documented | none |
| Tectonic | per-file `ReadThenWritten` comparison **within** a run | `DEFAULT_MAX_TEX_PASSES = 6` | names the file: `"foo.aux" changed`; nothing on cap exhaustion |
| ConTeXt `mtx-context` | MD5 of the single `.tuc` multipass file | `multipass_nofruns = 9`, with the source comment `-- better for tracing oscillation` | none: `"maxruns"` |
| Typst | 128-bit hash comparison of layout iterations 4 and 5 | `MAX_ITERS = 5` in `introspection/convergence.rs` | **extensive**: per-fact warnings with byte spans, full per-iteration value histories, a secondary "created here" span, plus `document did not converge within five attempts` |
| `llmk` | as `latexmk` | `max_repeat = 5`, documented "to prevent potential infinite loops" | none |

AuxFlow's runtime verifier is a faithful reimplementation of the checksum approach and is **not** a
contribution. It is reimplemented rather than delegated so that baselines B, C and E share identical
normalisation and differ only in the mechanism under study.

**Typst deserves separate emphasis.** It has engineered away the *build-orchestration* half of
AuxFlow's problem entirely — no auxiliary files, no external driver, a fixed five iterations — and it
has already built the *reporting* half, dynamically and at instance level with source spans. What
remains unoccupied is the static, pre-execution half. Typst's existence also weakens the practical
motivation for the problem area, because the modern answer to "my document will not converge" is
increasingly "the engine tells you, with a span".

---

## 10. Document-domain research: nearly empty, and one dangerous thesis

Searched extensively (exact queries in
[`research/sources/area-b-latex-compilation.md`](../research/sources/area-b-latex-compilation.md)).

- **No published work statically derives the number of engine runs for a document.** SOURCED
  negative, six recorded queries, ~70 sources examined.
- **No formal semantics of TeX exists, and Knuth says so himself** (*TUGboat* 35:3, p. 239): "I have
  no real interest, for example, in defining exactly what it would mean for TEX to be correct".
  Defining a semantics for AuxFlow's declared subset is therefore necessary, unclaimed work.
- **No MSc or PhD thesis and no peer-reviewed paper on LaTeX build automation, LaTeX dependency
  analysis, or document compilation scheduling was located.** "Incremental typesetting" as a research
  keyword is essentially empty between Chen, Harrison and Minakata (DOCPROCS 1988, DOI
  `10.1145/62506.62523`) and 2022.

**The dangerous item is Mädje's MSc thesis** (Laurenz Mädje, TU Berlin, Faculty IV, 8 September
2022; the Typst design thesis), §6.3, pp. 48–51 (SOURCED, read). It names intra-document
dependencies as cyclic, gives AuxFlow's benign and amplifying exemplars as worked examples,
formalises stability as convergence of a recurrence relation, **proves via Rice's theorem that it is
undecidable for arbitrary code**, proposes a per-query *observability* test instead of whole-state
comparison, and prescribes a constant iteration cap plus "a user-facing error message at the guilty
locate call". AuxFlow must cite this and must not claim the fixpoint framing, the undecidability
observation, the benign/amplifying examples, or the idea of naming the guilty construct.

A 2026 arXiv position paper (arXiv:2603.02873, "LaTeX Compilation: Challenges in the Era of LLMs")
is both help and threat. It supplies a citable framing — "the LATEX typesetting process is
essentially an iterative workflow that relies on intermediate results to converge", under the
section heading "Multi-pass Compilation: A Fragile Stopgap" — and it also asserts that analysing
LaTeX structure without running TeX is "virtually unfeasible in practice" because conditional
expansion makes the structure dynamic. AuxFlow's declared subset is the only answer, and must be
stated as such.

### Cross-reference dependency graphs for documents

Building one from LaTeX source is **not novel**. `xreferences`, `latex-dependency-grapher` and
KnowTeX all do it; all target visualisation or documentation; none carries pass-lag semantics; none
is used for scheduling or convergence reasoning. `xreferences` remains REPORTED and must be
inspected before any claim about graph extraction is made.

Scribble (Racket's documentation tool) is the language-design alternative AuxFlow should
acknowledge: it declares four passes by construction, runs its traverse pass to a fixed point, and
imposes a language-level restriction that resolve-pass expansion must not create new hyperlink
targets — a real precedent for restricting feedback by design rather than analysing it.

---

## 11. Novelty matrix

Brutal by instruction. Novelty risk is the risk that the element is anticipated; `HIGH` means the
element is anticipated and must not be claimed.

| # | AuxFlow feature | Closest prior work | Exact overlap | Difference | Novelty risk |
|---|---|---|---|---|---|
| 1 | LaTeX parsing (catcode lexer, recursive descent) | Erdweg and Ostermann, Featherweight TeX, SLE 2010; latexrun's `\includegraph` counterexample; arXiv:2603.02873 | Parsing LaTeX is a solved-and-published-as-hard problem | The artefact is new code over a *declared subset*; the subset is what makes it sound | **HIGH** (no novelty; the feasibility objection is published and must be answered) |
| 2 | Semantic fact extraction | `labelschanged` (hooks `\@testdef`, enumerates label instances with values); Pluto's BibTeX stamper parses the aux file for citation keys | Fact-level granularity over auxiliary content already exists | AuxFlow extracts from *source* before any run | **HIGH** |
| 3 | Cross-reference dependency graph | `xreferences`, `latex-dependency-grapher`, KnowTeX; latexrun's cyclic-graph diagram | Building the graph from LaTeX source | Pass-lag edge weights | **HIGH** for the graph; MEDIUM for the lag semantics |
| 4 | Instance-level fact representation | Alblas 1981 *pure* multi-pass; Engelfriet and Filè 1981; Jones 1990 (instance-level attribute dependency graph) | Per-instance rather than per-kind numbering is a named 1981 class | Applied to document facts | **HIGH**, and AuxFlow inherits an exponential decision problem it must address by restriction |
| 5 | `stable_pass` propagation | Bochmann 1976; Alblas 1981; Hecht and Ullman 1975; Ullman's "depth+1 to propagate, 1 to notice" | Total | Different graph | **HIGH** |
| 6 | SCC detection | Tarjan 1972; Sharir 1981; Jones 1990 | Total | none | **HIGH** |
| 7 | Cycle classification (benign vs amplifying) | Farrow 1986; Krishnan and Van Wyk 2012; US8181129B2; SDF 1987 | Find SCCs, classify by a semantic property of the circulating values, diagnose the bad ones | The *criterion*: influence on the quantity of generated content, in a setting where the graph is not invariant | **HIGH** for the shape; **MEDIUM** for the criterion, contingent on reading Krishnan and Van Wyk and Söderberg and Hedin in full |
| 8 | Non-convergence diagnosis | Alblas 1981 ("indicate […] the attributes that cause the rejection"); Rodeh and Sagiv 1999; Magnusson and Hedin's robust evaluator; Typst; `labelschanged`; Tectonic; Mädje's "guilty locate call" | Naming the offending facts is anticipated at least six times | Doing it **before** any execution | **HIGH** for the output; **LOW-MEDIUM** for pre-execution derivation |
| 9 | Source-level explanation (spans, chains) | Typst ships byte spans, per-iteration value histories and a "created here" secondary span | Total, for the output | AuxFlow reports a *chain*, and reports it statically | **HIGH** for the output form |
| 10 | Static build-plan generation | Farrow 1986 (evaluation order fixed at generation time); Bochmann 1976; Miller 1998 (graph-structural bound on Make passes) | Deriving a schedule statically from a dependency graph | Applied to an external engine's run count | **HIGH** |
| 11 | Runtime verification (state comparison) | `latexmk`, ConTeXt, `rerunfilecheck`, Tectonic, Typst, Excel calc chain | Total | none; explicitly reimplemented, not claimed | **HIGH** (conceded by design) |
| 12 | Static/dynamic oracle comparison | Nothing located | — | Five deployed oracles, five caps, no published comparison of agreement, soundness or cost | **LOW** — genuinely unoccupied |
| 13 | Mechanism taxonomy of LaTeX non-convergence | Gaspar (one letter); TeX FAQ (one entry); tex.SE 30674 (a thread); `labelschanged` (a hand-written list) | The individual mechanisms are all published somewhere | Nobody has systematised them or mapped them against static criteria | **LOW** — genuinely unoccupied |
| 14 | Declared-subset operational semantics for the auxiliary round trip | No formal semantics of TeX exists (Knuth's own disclaimer); Featherweight TeX covers parsing only | — | Definitional work, necessary and unclaimed | **LOW** |
| 15 | Compiler-derived workload metadata | US20210232492A1 (Red Hat, estimating work to regenerate a program); resource-prediction-from-source patents | Estimating build work from source | none worth having | **HIGH** — must stay out of scope |
| 16 | Kubernetes scheduling | Standard practice | Total | none | **HIGH** — not a contribution, and not in this repository |
| 17 | KEDA scaling | Standard practice | Total | none | **HIGH** — not a contribution, and not in this repository |

**Three rows out of seventeen carry low novelty risk: 12, 13 and 14.** One row (7) is genuinely
contingent. Everything else is anticipated.

---

## 12. The research gap

Stated after the concessions, and not forced. Three items survive.

**G1 — a decision procedure where the graph is not invariant under iteration.** Farrow 1986
*allocates* the convergence obligation; Jones 1990 *assumes* it; Magnusson and Hedin 2007 state in
writing that they do not check it and that Farrow does not either. Krishnan and Van Wyk 2012 do
decide termination of content generation, but in a *rewriting* formulation over a fixed grammar
rather than an *influence* formulation over instance data. So the gap is: a static, conservative,
domain-specific sufficient condition for the finite-height half of the classical convergence
obligation, in a setting where fact values can change how much structure exists.
**Status: contingent.** It survives only if Krishnan and Van Wyk 2012 and Söderberg and Hedin 2013,
read in full, do not already provide it. Until then, no claim.

**G2 — a controlled comparison of convergence oracles for document compilation.** Five deployed
systems use five different oracles (engine warning; output checksum across runs; input checksum
across runs; same-run read-then-written comparison; layout-iteration hash) with five hand-chosen
caps (5, none, 6, 9, 5). Nothing was found characterising when they agree, which are unsound and in
which direction, or what each costs. The engine's own oracle has both false negatives (generated
lists, sourced from `rerunfilecheck`'s own documentation) and false positives (active characters in
captions, sourced from `labelschanged`). **Status: unoccupied, cheap, defensible.**

**G3 — a systematised, reproducible taxonomy of LaTeX non-convergence mechanisms, mapped against
what static criteria can and cannot catch.** The present record is one TUGboat letter, one FAQ
entry, one Stack Exchange thread and one package's informal list of usual suspects. Section 7.3 of
this document is, as far as the audit could establish, the first attempt to enumerate the mechanisms
and state per mechanism whether a given static criterion detects it. **Status: unoccupied.**

**What is not a gap:** static pass numbering; SCC plus condensation fixpoint; instance-level
dependency graphs; iteration bounds from graph structure; cycle classification as such; naming the
offending facts; checksum verification; source parsing for dependency discovery; the undecidability
observation; the one-extra-run observation; the benign/amplifying *examples*.

---

## 13. What AuxFlow may claim

### Conservative — safe now

> AuxFlow specifies a declared subset of LaTeX together with an operational account of its
> auxiliary-state round trip, and lowers documents in that subset to an instance-level dependency
> graph of auxiliary fact instances carrying pass-lag edges. It applies established multipass and
> circular-attribute-grammar analyses (Bochmann 1976; Alblas 1981; Farrow 1986; Jones 1990) to that
> graph. Its contributions are a systematised mechanism taxonomy of LaTeX non-convergence with a
> statement of which mechanisms a dependency-based static criterion can and cannot detect, and a
> controlled comparison of the convergence oracles deployed in current tools.

### Strong — only if the experiments validate it, and only after Krishnan and Van Wyk 2012 and Söderberg and Hedin 2013 are read in full

> For a declared subset of LaTeX, a static influence analysis from auxiliary fact values to
> constructs governing the quantity of generated content is a usable sufficient condition for the
> finite-height precondition of circular-attribute-grammar fixpoint theory. That is, it decides
> statically whether classical fixed-graph fixpoint reasoning applies to a document at all. For the
> loop-bounded-by-a-reference class of non-convergent documents this yields a pre-execution verdict
> with source-level attribution, where deployed tools reach the same conclusion only after
> exhausting an iteration cap — and for the extent-driven class it does not, which is a measured and
> declared limitation rather than a discovered one.

### Overclaim — must never appear

1. That AuxFlow invented static pass-number assignment, minimisation, or any bound derived from
   graph structure.
2. That no prior work distinguishes cycles that move values from cycles that change how much content
   exists.
3. That AuxFlow's setting has no analogue in the attribute-grammar literature.
4. That a dependency cycle proves non-convergence, or that its absence proves convergence.
5. That AuxFlow detects all non-convergent LaTeX documents, or all non-convergent documents in the
   subset. It provably does not: M3, M4, M6 and M7.
6. Any universal soundness claim of the form "predicted runs is always at least required runs" — the
   required count may not exist.
7. That dynamic convergence detection necessarily costs one extra execution. latexrun and Tectonic
   do not.
8. That existing tools report no cause for non-convergence. Typst, `labelschanged` and Tectonic do.
9. That AuxFlow's state comparison, SCC detection, condensation fixpoint, or diagnostic output form
   is novel.
10. Any resource-cost or scheduling-priority prediction from document content.
11. That the analysis applies to arbitrary TeX rather than to a declared subset.
12. Any performance claim not backed by a committed measurement script.

---

## 14. Base papers

Ten, categorised. Each entry states what AuxFlow does with it: **extends**, **adapts**,
**combines**, or **compares against**. "Compares against" includes mandatory concessions.

### Theoretical foundation

| # | Citation | DOI | Why it matters | AuxFlow builds on | Relation |
|---|---|---|---|---|---|
| 1 | Bochmann, "Semantic evaluation from left to right", *CACM* 19(2):55–62, 1976 | `10.1145/359997.359999` | Origin of static pass-number assignment from a dependency-graph characterisation | `stable_pass` numbering | **compares against** — mandatory concession, section 1 |
| 2 | Hecht and Ullman, "A Simple Algorithm for Global Data Flow Analysis Problems", *SIAM J. Comput.* 4(4):519–532, 1975 | `10.1137/0204044` | The iteration count of a monotone fixpoint is bounded by a structural depth parameter; "N passes to propagate, one to confirm" | The build plan's shape and the `P+1` formula | **compares against** — mandatory concession, section 4 |
| 3 | Farrow, "Automatic generation of fixed-point-finding evaluators for circular, but well-defined, attribute grammars", *SIGPLAN Notices* 21(7):85–98, 1986 | `10.1145/13310.13320` | Static analysis of circular dependency graphs; well-definedness constraints; an algorithm identifying which parts carry the convergence obligation | The whole skeleton of cycle handling | **extends** — AuxFlow attempts to discharge what Farrow allocates, in a variable-graph setting. **Read in full before any claim.** |
| 4 | Jones, "Efficient evaluation of circular attribute grammars", *TOPLAS* 12(3):429–462, 1990 | `10.1145/78969.78971` | SCC partition, condensation, topological order, one fixpoint per component | The analysis architecture, wholesale | **compares against** — adopted verbatim as standard technique |
| 5 | Magnusson and Hedin, "Circular reference attributed grammars — their evaluation and applications", *SCP* 68(1):21–37, 2007 | `10.1016/j.scico.2005.06.005` | States the finite-height + monotonicity convergence condition exactly, and admits nobody checks it | The formal statement of what `BENIGN_CYCLIC` approximates | **extends** — AuxFlow supplies a domain-specific check for the condition they decline to check |
| 6 | Krishnan and Van Wyk, "Termination Analysis for Higher-Order Attribute Grammars", SLE 2012, LNCS 7745:44–63 | `10.1007/978-3-642-36089-3_4` | Conservative static analysis deciding termination when evaluation generates new content to evaluate; explicitly distinguished from circularity analysis | The nearest neighbour of the taint analysis | **compares against**, possibly **adapts**. **The single most important paper to read fully.** |

### Document compilation foundation

| # | Citation | URL | Why it matters | AuxFlow builds on | Relation |
|---|---|---|---|---|---|
| 7 | Mädje, *A Programmable Markup Language for Typesetting*, MSc thesis, TU Berlin, 8 September 2022, §6.3 | `laurmaedje.github.io/programmable-markup-language-for-typesetting.pdf` | Formalises document-introspection stability as a recurrence; proves undecidability via Rice's theorem; gives the benign and amplifying exemplars; prescribes a cap plus a diagnostic at the guilty call | The problem framing | **compares against** — mandatory concession. AuxFlow's difference is staticness, a declared subset, a decision procedure and a predicted count |

### Build-system foundation

| # | Citation | DOI | Why it matters | AuxFlow builds on | Relation |
|---|---|---|---|---|---|
| 8 | Mokhov, Mitchell and Peyton Jones, "Build systems à la carte", ICFP 2018 | `10.1145/3236774` | Applicative versus monadic tasks: the static/dynamic dependency axis. Names LaTeX's category as bistable or diverging | The vocabulary for the problem | **compares against** — supplies terminology; AuxFlow statically approximates a monadic task |
| 9 | Erdweg, Lichter and Weiel, "A sound and optimal incremental build system with dynamic dependencies" (Pluto), OOPSLA 2015 | `10.1145/2814270.2814316` | LaTeX/BibTeX running example; the aux self-cycle; a fixpoint cycle handler; fact-level aux stamping; and the published judgement that soundly detecting LaTeX dependencies "is a lost cause" | Nothing — it is the objection AuxFlow must answer | **compares against** — must be confronted in the first two pages |

### Non-convergence foundation

| # | Citation | URL | Why it matters | AuxFlow builds on | Relation |
|---|---|---|---|---|---|
| 10 | Gaspar, "Does not suffice to run latex a finite number of times to get cross-references right", *TUGboat* 35:1 (2014), p. 16 | `tug.org/TUGboat/tb35-1/tb109gaspar.pdf` | The existence proof: a document whose cross-reference is wrong for any finite run count. Monotone divergence | Corpus member `b08`; the reason no universal bound is claimed | **compares against** — an existence result, not a theory |

### Evaluation and baseline foundation

These are engineering artefacts, not papers, and are labelled as such. They are the baselines and
must be characterised exactly rather than paraphrased.

- `latexmk` 4.88 manual and `latexmk.pl` — the primary baseline. `(time, size, md5)` database;
  `$max_repeat` default 5; `Maximum runs of <rule> reached without getting stable files`; and the
  author's own statement of undecidability in the shipped source.
- latexrun `README.md` — the input-comparison oracle that avoids the extra run, and the
  `\includegraph` counterexample that justifies the declared subset.
- Tectonic `src/driver.rs` — `DEFAULT_MAX_TEX_PASSES = 6`; same-run `ReadThenWritten` comparison;
  `RerunReason::FileChange(name)`.
- Typst `crates/typst-library/src/introspection/convergence.rs` and
  `tests/suite/introspection/convergence.typ` — `MAX_ITERS = 5`; hash comparison; per-fact
  diagnostics with spans and value histories.
- ConTeXt `scripts/context/lua/mtx-context.lua` — MD5 of `.tuc`; `multipass_nofruns = 9`.
- `labelschanged` (CTAN) — per-label-instance instability reporting, plus a first-party taxonomy of
  causes.

### Second tier — read before publication, not base papers

Söderberg and Hedin, SLE 2013, DOI `10.1007/978-3-319-02654-1_17` (circular attributes
interdependent with rewrites — **the second most important paper to read fully**); Lee and
Messerschmitt, IEEE TC 1987, DOI `10.1109/TC.1987.5009446`; Erdweg and Ostermann, SLE 2010, DOI
`10.1007/978-3-642-19440-5_26`; Alblas, *Acta Informatica* 1981, DOI `10.1007/BF00264495`; Räihä and
Ukkonen, *SIAM J. Comput.* 1981, DOI `10.1137/0210060`; Riouak et al., SLE 2024, DOI
`10.1145/3687997.3695644`; Vogt, Swierstra and Kuiper, PLDI 1989; Alblas, "Iteration of
transformation passes over attributed program trees", *Acta Informatica* 27(1):1–40, 1989, DOI
`10.1007/BF00263499`.

---

## 15. Proposed Related Work structure for the report

With the exact works belonging in each section.

**2.1 Multipass compiler analysis.** Bochmann 1976; Alblas 1981 (simple versus pure); Räihä and
Ukkonen 1980/1981 (NP-completeness, the `2n−1` bound); Engelfriet and Filè 1981/1982 (pure
multipass is inherently exponential); Alblas 1991 (survey/taxonomy). Purpose: concede pass numbering
in the first paragraph of the section.

**2.2 Attribute evaluation, dependency scheduling, and cyclic attributes.** Knuth 1968 with the 1971
correction (*Mathematical Systems Theory* 5(2):95–96, DOI `10.1007/BF01702865` — note, 5(2), not
5(1), which is what most citing papers print); Jazayeri, Ogden and Rounds 1975 and Wu 2004
(circularity is EXPTIME-complete, not merely "exponential"); Kastens 1980; Farrow 1986; Jones 1990;
Rodeh and Sagiv 1999; Magnusson and Hedin 2007; Boyland 2005 (undecidability for remote AGs);
Riouak et al. 2024. Purpose: establish the framework AuxFlow instantiates and the exact convergence
condition.

**2.3 Higher-order attribute grammars and self-generating evaluation.** Vogt, Swierstra and Kuiper
1989; Swierstra and Vogt 1991; Krishnan and Van Wyk 2012; Söderberg and Hedin 2013; Alblas 1989.
Purpose: this is where the withdrawn novelty claim goes, and where AuxFlow's nearest neighbour is
positioned. It must not be omitted or a reviewer will supply it.

**2.4 Static bounds on fixpoint iteration.** Hecht and Ullman 1975; Kam and Ullman 1976, 1977;
Sharir 1981; the modern textbook restatement. Purpose: concede the `P+1` formula.

**2.5 Static schedulability under data-dependent rates.** Lee and Messerschmitt 1987; Buck and Lee
on Boolean dataflow. Purpose: position the benign/amplifying distinction as a domain instance of a
known dividing line, and borrow the two-failure-mode taxonomy.

**2.6 Document compilation and LaTeX build systems.** The LaTeX kernel sources (`ltxref.dtx`,
`ltfiles.dtx`, `ltmiscen.dtx`); `rerunfilecheck`; `latexmk`; latexrun; Tectonic; ConTeXt; `arara`;
`llmk`; Typst and Mädje 2022; Scribble; Chen, Harrison and Minakata 1988; arXiv:2603.02873. Purpose:
establish the baselines exactly, and concede the diagnostic output form to Typst.

**2.7 Incremental and dependency-aware build systems.** Mokhov, Mitchell and Peyton Jones 2018/2020;
Erdweg, Lichter and Weiel 2015; Mitchell 2012; Miller 1998; GNU Make's remaking restart; Bazel
include scanning; the Makefile static-analysis line (Tamrawi et al.; Licker and Rice, ICSE 2019, DOI
`10.1109/ICSE.2019.00125`). Purpose: concede the static/dynamic axis, and answer Pluto's "lost
cause" sentence.

**2.8 Cyclic dependencies and non-convergence in documents.** Gaspar 2014; the TeX FAQ oscillation
entry; tex.SE 30674 and 81695; `labelschanged`'s taxonomy; the M1–M9 mechanism table. Purpose:
establish that the phenomenon is real, has several distinct mechanisms, and is undiagnosed as a
class.

**2.9 Existing LaTeX dependency-analysis tools.** `xreferences`; `latex-dependency-grapher`;
KnowTeX; `texdepend`; Rubber (via latexrun's critique). Purpose: concede graph extraction.

**2.10 Research gap.** G1, G2, G3 from section 12, with G1 marked contingent.

**2.11 AuxFlow's position.** The conservative claim from section 13, with the strong claim stated as
conditional on the experiments.

---

## 16. Negative results from the prior-art search

Recorded because absence of evidence is evidence only when the query is written down. All queries
are in [`research/prior-art-log.md`](../research/prior-art-log.md) and in the per-area files under
[`research/sources/`](../research/sources/).

- **No tool or publication statically derives the number of engine runs for a document.** SOURCED
  negative; six web queries plus arXiv and DBLP queries; ~70 sources examined.
- **No work performs static, subset-restricted, conservative convergence analysis of document
  compilation.** The only work that treats document convergence as a static-analysis problem —
  Mädje 2022 — does so in order to *deny* that it can be done in general.
- **No attribute-grammar paper classifies dependency cycles by whether cycle-carried values
  influence the quantity of generated content.** SOURCED negative with the exact query. The
  literature partitions the space differently: circularity existence; which attributes are on
  cycles; whether a cycle converges (assumed, not decided); whether tree creation terminates.
- **No build-system work bounds the number of iterations to a fixpoint**, beyond Miller 1998's
  single qualitative sentence about recursive Make.
- **No build-system work classifies cyclic build dependencies as benign versus divergent.**
- **No patent was found on static convergence classification of document compilation**, on
  **classifying dependency cycles by whether a value affects the quantity of generated work** (the
  targeted query returns zero), or on **cloud or automated LaTeX compilation as such**.
- **The attribute-grammar multipass literature has no reachable US patent footprint at all.** The
  academic prior art in this area is therefore older, stronger and more dangerous to AuxFlow's
  novelty than the patent prior art.
- **No formal semantics of TeX exists**; Knuth's own disclaimer is the primary evidence.
- **No MSc or PhD thesis and no peer-reviewed paper on LaTeX build automation, LaTeX dependency
  analysis, or document compilation scheduling was located.**

### Corrections to propagate

- The Räihä and Ukkonen citation is a conflation of two papers. See section 1.
- Magnusson and Hedin's DOI is `10.1016/j.scico.2005.06.005` (SCP **68**(1)). The value
  `10.1016/j.scico.2007.01.005` is a different paper (SCP **67**(1), "ScriptEase") and must not be
  used.
- Knuth's 1971 correction is *Mathematical Systems Theory* **5(2)**:95–96, not 5(1).
- Circularity for attribute grammars is **EXPTIME-complete**, not merely "exponential".
- Licker and Rice, ICSE 2019, is DOI `10.1109/ICSE.2019.00125`.
- A TUG 2026 preprint cites "Bour, TeXpresso, *TUGboat* 44(2):185–192, 2023" at a URL that 404s, and
  no such article exists in the TUGboat title index, author index, or either candidate issue's file
  list. **Do not propagate that citation.**
- The Plass thesis PDF hosted at tug.org is scanned page images with no text layer. Do not quote it.
