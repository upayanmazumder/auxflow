# Related work

Prior art is conceded first and claims are made afterwards. A reviewer who discovers an
anticipation after reading an over-claiming introduction will discount everything else; one who
finds it cited in the first section will credit what remains.

**Verification status** is recorded per item. `verified` means the primary source was opened and
the quoted text read directly. `reported` means the text was obtained second-hand during
research and must be confirmed against the primary source before it appears in a report.

---

## 1. Static pass-number analysis is established prior art

**This is the most important section in the document. AuxFlow does not claim to have invented
static pass-number minimisation.**

| Work | Substance | Status |
|---|---|---|
| Bochmann, "Semantic evaluation from left to right", *Communications of the ACM*, 1976, DOI `10.1145/359997.359999` | Gives a condition under which an attribute grammar can be evaluated in a single pass, and "an algorithm is discussed which decides how many passes from left to right are in general necessary, given the attribute grammar" | verified |
| Alblas, "A characterization of attribute evaluation in passes", *Acta Informatica* 16(4):427–464, 1981, DOI `10.1007/BF00264495` | "A graph theoretic characterization is given" of when a grammar meets the multi-pass requirements, and "new algorithms are developed that associate minimal pass numbers with attributes" | verified |
| Räihä and Ukkonen, "Minimizing the number of evaluation passes for attribute grammars", ICALP 1980, LNCS 85, pp. 500–511 | The title is the claim | reported (cited in Alblas's reference list) |
| Engelfriet and Filè, "Passes and paths of attribute grammars" | Deciding whether an arbitrary grammar is pure multipass is of inherently exponential complexity; for fixed *k*, polynomial | reported |

The technique AuxFlow uses to number facts is a transplant of this work. What does not carry
over is the precondition: an attribute grammar's dependency structure is determined by a **fixed
grammar**, whereas a document's is determined by **its data**. Two consequences follow, and they
are the space AuxFlow occupies.

First, the graph must be built per document from an instance-level analysis rather than derived
once from a grammar. Second — and this is the substantive difference — the classical setting
assumes the dependency structure is what it is, whereas here a fact value can change *how much
structure exists*. The classical work has no analogue of that, because in a grammar no attribute
value alters the shape of the derivation tree.

## 2. Convergence detection in practice

| Work | Mechanism | Status |
|---|---|---|
| `latexmk` | Compares auxiliary file contents by checksum between runs to decide whether another is needed; caps iteration with a configurable maximum (documented default 5) | verified |
| `rerunfilecheck` | Adds checksum-based detection of auxiliary-file changes that base LaTeX does not report. Its existence is evidence that the engine's own warning is insufficient | reported |
| Tectonic | Either a user-declared fixed pass count or a dynamic rerun loop | reported |
| `arara` | Acts on author-declared directives embedded in the source, not on inferred structure | reported |
| Overleaf's compilation service | Decides incremental versus full rebuild by file-tree hash comparison, not source analysis | reported |

All are dynamic or author-declared. None derives a schedule from the source before execution.
AuxFlow's runtime verifier is a faithful reimplementation of the checksum approach and is not
claimed as a contribution; it is reimplemented rather than delegated so that the baseline and
the verifier differ only in the variable under study.

## 3. Source-parsing build tools

`Rubber` parses LaTeX source to discover dependencies and to decide which companion tools to
invoke: "Dependency analysis is performed by parsing the source files" (reported). This
anticipates dead-tool elimination outright.

The `latexrun` documentation supplies the honest counterweight: "TeX is, famously, the only
thing that can correctly parse TeX code and as a result Rubber's dependency analysis is fragile"
(reported). This is the strongest available argument for AuxFlow's default-deny subset with an
explicit opaque fallback — the alternative approach exists, and its weakness is documented by
its contemporaries.

Rubber still determines the *number* of runs dynamically.

## 4. Cross-reference dependency graphs for documents

| Work | What it does | Status |
|---|---|---|
| `xreferences` | Reads LaTeX files, maps labels of environments of interest, finds which labels are referenced within them, yielding a dependency graph | verified |
| `latex-dependency-grapher` (2024) | Takes a file or folder, produces a Graphviz dependency graph; also detects declared-but-unused packages | verified |
| KnowTeX, arXiv:2601.15294 (2025) | Generates dependency graphs from LaTeX sources for mathematical exposition, using an explicit author-written `uses` command | verified |

Building a cross-reference dependency graph from LaTeX source is therefore **not novel**. All
three target visualisation or documentation, none carries pass-lag semantics, and none is used
for scheduling or convergence reasoning. KnowTeX is furthest away, being author-declared rather
than inferred.

## 5. Build-system theory

| Work | Relevance | Status |
|---|---|---|
| Mokhov, Mitchell and Peyton Jones, "Build systems à la carte", ICFP 2018, DOI `10.1145/3236774` | Classifies build tasks by expressivity; a monadic task has dynamic dependencies, where what a computation depends on is itself computed. Document compilation is monadic in exactly this sense | verified |
| Erdweg, Lichter and Weiel, "A sound and optimal incremental build system with dynamic dependencies", OOPSLA 2015, DOI `10.1145/2814270.2814316` | Sound and optimal incremental building with dynamic dependencies, with formal proofs. The mechanism interleaves dependency analysis with builder execution — it is dynamic | verified |

The first supplies vocabulary: AuxFlow statically approximates a monadic build task's schedule,
which is precisely the case that framework identifies as hardest. The second establishes that
"sound" and "optimal" are already claimed for build systems, and that AuxFlow must therefore
distinguish itself on being *static and pre-execution* rather than on those adjectives.

## 6. Circular attributes and fixpoint evaluation

Magnusson and Hedin, "Circular reference attributed grammars — their evaluation and
applications", *Science of Computer Programming*, 2007, DOI `10.1016/j.scico.2005.06.005`:
circular attribute grammars support iterative fixed-point computation of attributes in
dependency cycles (verified).

This is the standard machinery for evaluating cyclic attribute dependencies and AuxFlow's
handling of cycles follows it rather than inventing anything. The difference is one of purpose:
that work evaluates circular attributes to a fixpoint, whereas AuxFlow does not evaluate at all
— it classifies the cycle and decides whether a fixpoint can be expected to exist.

## 7. Documented non-convergence

Gaspar, "Does not suffice to run latex a finite number of times to get cross-references right",
*TUGboat* 35:1 (2014), p. 16: "We present a LATEX file such that a cross-reference is wrong no
matter how many times we run latex" (verified — the nine-line counterexample was read in full).

The mechanism is a loop whose bound is a page reference to a label placed inside the material
the loop generates. This is the concrete instance of the amplifying class and is corpus member
`b08`. It is also the clearest statement in the literature that a universal bound on run count
cannot exist, which is why AuxFlow makes no such claim.

## 8. Statically bounding fixpoint iterations — patents

| Patent | Substance | Status |
|---|---|---|
| US10025569, Texas Instruments, granted 2018 | Determines the maximum number of iterations of iterative dataflow analysis for reducible loops from graph structure; its background criticises selecting an iteration cap arbitrarily | reported — **must be confirmed against the primary source** |
| US20240272888, SAP SE, published 2024 | Bounds re-evaluation rounds over a dependency graph by the graph's diameter; the description names software build tools among its applications | reported — **must be confirmed against the primary source** |

If confirmed, these are the closest art to any claim about deriving iteration counts from graph
structure, and reinforce that this aspect must not be presented as novel. See
[PATENT-NOTES.md](PATENT-NOTES.md).

## 9. Resource prediction from source

Several granted patents cover extracting features from source code and predicting resource
requirements or scheduling priority from them. AuxFlow makes **no** cost- or
resource-prediction claim, and this is one reason why. Details in
[PATENT-NOTES.md](PATENT-NOTES.md).

---

## The remaining research space

After the concessions above, what is left:

1. **Instance-level dependency extraction for document compilation.** Existing document
   dependency graphs are coarse and built for visualisation. None carries pass-lag semantics or
   supports per-fact numbering.
2. **Classifying feedback by effect on content quantity.** No prior work distinguishes cycles
   that move values from cycles that change how much content exists. This distinction is what
   makes static analysis of this domain possible rather than vacuous, and it has no analogue in
   the attribute-grammar setting because grammars cannot generate themselves.
3. **Pre-execution diagnosis of non-convergent structures.** Existing tools exhaust a retry cap
   and report that they gave up. None names the responsible facts.
4. **A controlled comparison of convergence oracles.** Engine warnings, checksum comparison and
   output comparison disagree with one another in ways that appear not to be characterised
   anywhere in the literature.

Items 2 and 3 are the contribution. Items 1 and 4 are supporting.

## Negative results from the prior-art search

Recorded because absence of evidence is worth documenting when it was actually searched for.

- No tool or publication was found that statically derives the number of engine runs for a
  document. Searched: CTAN build-tool documentation, TUGboat, academic indexes, patent
  databases.
- No patents were found on cloud or automated LaTeX compilation as such.
- No work was found using compiler or static-analysis output as an input to workload scheduling
  for document builds.

These are `reported` and each should be re-run before publication; a negative result asserted
without a reproducible query is not evidence.
