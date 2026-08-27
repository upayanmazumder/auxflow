# Patent notes

**This is not a patent application, and nothing here is legal advice.** It is an engineering
record of prior-art risk, kept so that the project does not accidentally build its identity on a
claim that is already owned.

Any statement about patentability in this repository uses the phrase *potentially patentable
subject to professional prior-art and patentability review*, and no stronger formulation is
permitted.

## Why this file exists

During project scoping, the intended headline contribution was "statically derive the minimal
number of compilation passes". Prior-art research found that idea anticipated in the academic
literature from 1976 and, apparently, in at least two patent families. Discovering that before
implementation rather than at examination is the entire value of keeping this record.

## Prior-art risks

Ordered by severity.

### High — do not claim

**Deriving iteration or pass counts from dependency-graph structure.**

- Academic: Bochmann (CACM, 1976) decides how many passes an attribute grammar requires; Alblas
  (1981) associates minimal pass numbers with attributes via a graph-theoretic characterisation;
  Räihä and Ukkonen (ICALP 1980) address minimising the number of evaluation passes directly.
  Verified; see [RELATED-WORK.md](RELATED-WORK.md).
- Patents, reported and requiring confirmation: US10025569 (Texas Instruments) on determining
  the maximum number of dataflow-analysis iterations from graph structure; US20240272888 (SAP
  SE) on bounding re-evaluation rounds by dependency-graph diameter, in a description that names
  software build tools.

**Assessment:** anticipated in general form. Any claim of the shape "compute the number of
iterations from the graph" should be assumed unavailable.

### High — do not claim

**Predicting resource requirements or scheduling priority from source-code features.**

Granted patents exist covering extraction of features from a source corpus, prediction of
resource allocation from those features, and reordering a work queue by a content-derived score.

**Assessment:** AuxFlow makes no cost-prediction claim, and should not acquire one. If workload
metadata is ever attached to work items as stretch work, it must be a *classification* (does
this document converge, is it certified) rather than a *predicted cost*, and even then it should
not be presented as inventive.

### Medium

**Parsing document source to determine which build tools to invoke.** Anticipated by existing
build tools that parse LaTeX source for dependency analysis. Dead-tool elimination is therefore
a useful engineering feature and not a contribution.

**Constructing a cross-reference dependency graph from document source.** Anticipated by at
least three existing tools. The graph is not the contribution; the pass-lag semantics and the
use made of it might be.

### Low

**Checksum-based convergence detection.** Standard practice in existing build tools, and
explicitly reimplemented rather than claimed.

## What might be interesting

Stated conservatively, and only after the concessions above.

The element with no located anticipation is **classifying a document's cross-reference feedback
by whether a fact value can influence the quantity of generated content, and using that
classification to identify, before execution, a document whose compilation may not converge,
together with the specific facts and source locations responsible.**

Three properties distinguish it from the art above:

1. It is a **classification**, not a count. The anticipating work computes how many iterations
   are needed; this decides whether a finite number exists at all.
2. It depends on a distinction that **cannot arise in the attribute-grammar setting**, because
   no attribute value there alters the shape of the tree being analysed. It is specific to
   systems where evaluated output feeds back into how much input exists.
3. Its output is **an attributed diagnosis**, not a schedule.

*Potentially patentable subject to professional prior-art and patentability review.*

A claim of this shape would need to recite, at minimum: parsing a document source into fact
instances with source locations; constructing a dependency graph with pass-lag weights;
determining by propagation which fact values reach content-generating constructs; identifying
strongly connected components containing such a dependency; classifying the document on that
basis; and emitting a diagnosis identifying the participating facts without executing the
document compiler.

That is a narrow claim. It should be understood as narrow.

## Claims that must never be made

1. That AuxFlow invented static pass-number minimisation.
2. That a dependency cycle proves a document cannot converge.
3. Any universal soundness claim of the form "predicted runs is always at least required runs" —
   the required count may not exist.
4. That engine warnings are a sound completion oracle, or that AuxFlow's use of state comparison
   is novel.
5. Any resource-cost or scheduling-priority prediction from document content.
6. That the analysis applies to arbitrary TeX rather than to a declared subset.
7. Any performance claim not backed by a committed measurement script.

## What would be needed for a real assessment

- Independent confirmation of the two reported patents against primary sources, including their
  legal status and claim scope as granted.
- A professional search in the relevant classification areas, which a student search cannot
  substitute for.
- An assessment of obviousness, not merely novelty. A combination of known techniques can be
  novel and still unpatentable, and the combination here is not exotic.
- A view on whether the contribution is better served by publication than by filing. For a
  course project the answer is almost certainly publication.

## Position for the project

Proceed on the assumption that the contribution is **publishable but probably not patentable**,
and design the report accordingly: concede the prior art early, claim the classification
narrowly, and let the evaluation carry the weight. Should the classification result prove strong
enough to be worth protecting, seek professional review before any public disclosure — noting
that a course report or a public repository is itself a disclosure in most jurisdictions.
