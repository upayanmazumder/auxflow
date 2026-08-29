# Patent notes

**This is not a patent application, and nothing here is legal advice.** It is an engineering record
of prior-art risk, kept so that the project does not build its identity on a claim that is already
owned or already published.

Legal-status fields below are Google Patents' own assumptions plus the USPTO legal-event history
exposed on those records. They have not been confirmed against a national register. **Claim scope as
published is not claim scope as granted.** A professional search in the relevant CPC
classifications, and an assessment of obviousness rather than mere novelty, cannot be substituted for
by this document.

Any statement about patentability in this repository uses the phrase *potentially patentable subject
to professional prior-art and patentability review*, and no stronger formulation is permitted.

Full records, with quoted claim text, search queries and legal-event histories, are in
[`research/sources/patent-prior-art.md`](../research/sources/patent-prior-art.md).

## Why this file exists

During project scoping, the intended headline contribution was "statically derive the minimal number
of compilation passes". Prior-art research found that idea anticipated in the academic literature
from 1976 and in at least two patent families. Discovering that before implementation rather than at
examination is the entire value of keeping this record.

The audit of 2026-08-27 verified both patents on record, corrected one belief about them, and found
a third record that is more dangerous than either.

## Verified: the two patents on record

### US10025569B2 — Texas Instruments — granted and active

"Linear-time algorithm to determine the maximum number of iterations of the iterative algorithm for
data-flow analysis for reducible loops." Inventors Davis, Fuqua, Harvey. Application US 15/213,425.
Priority and filing 2016-07-19; granted 2018-07-17. **Active**; maintenance fees paid through the
eighth year (2025-12-18); anticipated expiry 2036-07-19. CPC G06F8/433, G06F8/443. Fifteen claims,
two independent.

Independent claim 1 recites a method of **compiling a high level language program into a machine
level language program** that: builds a control flow graph; initialises a collapse count to zero;
repeatedly detects nodes with a backedge into the current starting node and collapses everything
between them into a new starting node, incrementing the count, until one node remains; then performs
data flow analysis **for a number of iterations equal to one greater than the collapse count**; then
generates the machine code.

Notable dependent claims: claim 2/10 keeps converged variables and discards only non-converged ones;
claim 3/11 defines converged as unchanged between iterations; claim 8/15 recites merely that the
input graph "comprises a plurality of strongly connected components".

**Specification mentions, claims do not cover.** The description frames the problem generally and
criticises the prior practice of choosing "a maximum number of data-flow analysis iterations
arbitrarily" with convergence "determined when no tracked values changed during the prior iteration".
That is disclosure, not claim scope. No claim covers arbitrary-cap-plus-checksum, nor bounding
iterations of anything other than compiler data-flow analysis driving machine-code generation.

**Assessment.** Infringement risk **LOW**: AuxFlow does not compile to machine code, does not build a
control flow graph, and does not use the backedge-collapse procedure. Novelty risk **HIGH** for any
AuxFlow claim phrased as "statically determine the number of fixpoint iterations from the dependency
graph" — and note that the patent itself concedes the underlying idea is older, citing Sharir 1981
and Cooper et al. 2002 on its face.

### US20240272888A1 — SAP SE — published, still pending

"Resolving dependency graphs with cycles in parallel." Sole inventor Weisbarth. Application US
18/169,364. Priority and filing 2023-02-15; published 2024-08-15. **Pending, under active
rejection**: non-final actions mailed 2025-12-24 and 2025-12-29, response forwarded to the examiner
2026-03-30. CPC G06F8/61, G06F9/4881. Twenty-one claims as published, three independent.

**One project belief corrected.** The project had recorded this as a patent that "bounds
re-evaluation rounds over a dependency graph by the graph's diameter". That is half right. Claim 1
recites a bare parallel topological-evaluation loop — find nodes with no unevaluated required
dependencies, fire them asynchronously, wait for one to finish, collect results, repeat — with **no
cycle handling, no iteration bound, no diameter and no convergence test**. "Diameter" appears only in
dependent claims 3, 4, 10, 11, 17 and 18. Claim 3 recites iterating while the set of actions with
changed inputs is non-empty **and the iteration count is at most the diameter of the dependency
graph**; claim 4 recites exiting when that is exceeded.

So capping re-evaluation rounds of a cyclic dependency graph by a structural graph metric, and
aborting when the cap is exceeded, **is claimed subject matter** — in dependent claims of a pending
application whose independent claims are currently rejected.

**Specification mentions, claims do not cover.** The description names the target domains explicitly:
"installers for software-packages, software build-tools, spreadsheet calculators, and service
management of infrastructural services within a cloud". Build tools and spreadsheet calculators are
therefore *disclosed*, which matters as prior-art disclosure, but no claim is limited to them. The
description also states as an aim that "during evaluation, a case of (forever) unstable inputs is
detected and the evaluation aborted" — the abort-on-non-convergence posture, disclosed in 2023, but
implemented as a *dynamic* round cap rather than a static classification.

**Assessment.** Infringement risk **MEDIUM**, and only conditionally: AuxFlow as specified does not
execute the actions it schedules. Claim 3 is the watch item. If AuxFlow ever ships a driver that
reruns the engine while counting rounds against a graph metric, re-check the file's status before
publishing. Novelty risk **HIGH** for any claim to the general idea of diameter- or
node-count-bounded iteration over a cyclic dependency graph.

## The record that matters more than either

### US8181129B2 / US20090044157A1 — Mentor Graphics, now Siemens Industry Software

"Acyclic modeling of combinational loops." Inventors Gupta and Selvidge. Continuation of US
11/068,036 (granted US7454722B2), from provisional US 60/627,172. Priority 2004-11-15; granted
2012-05-15. **Active**, adjusted expiry 2026-12-25 — within months of this audit. CPC G06F30/35,
G06F30/327. Nineteen claims, three independent.

Granted claim 1: instructions for converting a combinational loop in a circuit design into an
acyclic circuit, comprising **determining whether the combinational loop is monotonic** and,
responsive to that determination, transforming it into an acyclic path.

Claim 6: **notifying a user** responsive to a determination that the loop is *not* monotonic.

Claim 7: **determining a strongly connected component of the design, wherein the combinational loop
is contained in the SCC**.

The description defines the criterion in convergence terms — a monotonic loop is one where "the loop
output does not change its value, or in other words, the loop output holds its previous value" — and
states that a non-monotonic loop is "not converted" and that the user may be notified that it "is
therefore likely to be oscillatory and problematic".

**This is AuxFlow's three-step core shape, applied to circuits in 2004:** build a dependency graph
of the artefact, find the strongly connected components, classify each by a semantic property of the
values circulating in it — separating cycles that settle from cycles that may oscillate forever — and
report the bad ones to the user as a design error.

**Assessment.** Infringement risk **LOW**: every independent claim is limited to circuit design, and
the patent expires in December 2026. Novelty risk **HIGH** for any AuxFlow claim of the form
"identify strongly connected components and classify each as convergent or potentially
non-convergent, notifying the user of the latter".

**What it does not reach.** The classification criterion is different in kind: monotonicity here is a
Boolean-function property (`G(I) = 0` in a sum-of-products decomposition) over a **fixed, finite
signal set**, in a setting where no loop can create new nodes. AuxFlow's criterion is whether a value
can influence *how much* artefact exists — an unbounded-quantity property with no analogue in a
combinational circuit. There is no taint analysis, no pass-lag semantics, no source-span diagnosis
and no documents.

## Prior-art risks, ordered by severity

### Highest — do not claim, and the threat is academic rather than legal

**Deriving iteration or pass counts from dependency-graph structure.**

Academic, all verified: Hecht and Ullman (*SIAM J. Comput.* 4(4):519–532, 1975) define
loop-connectedness and bound round-robin iteration by it; Ullman's own lecture notes state the
`depth+2` form and decompose it as "depth+1 passes to follow that number of increasing segments" plus
"1 more pass to realize we converged" — which is AuxFlow's build plan verbatim. Bochmann (*CACM*,
1976) decides how many passes an attribute grammar requires; Alblas (1981) associates minimal pass
numbers with attributes; Räihä and Ukkonen (*SIAM J. Comput.*, 1981) show minimum-pass assignment is
NP-complete.

Patents: US10025569B2 as above.

**Assessment:** anticipated in general form and in textbook pedagogy. Any claim of the shape "compute
the number of iterations from the graph" must be assumed unavailable.

### Highest — do not claim

**"Find the strongly connected components, classify each as convergent or potentially
non-convergent, and notify the user of the latter."**

Patents: US8181129B2 as above.

Academic, and stronger: Farrow (1986) gives constraints under which a circular dependency graph is
well defined and computable by successive approximation, plus "a final algorithm […] that tells which
individual attributes and functions must satisfy the constraints". Jones (1990) partitions the
dependency graph into strongly connected components and evaluates each by fixpoint in topological
order. Krishnan and Van Wyk (SLE 2012) give a conservative static analysis deciding termination when
evaluation **generates new content to be evaluated**, using SCC condensation, and explicitly
distinguish it from circularity analysis.

**Assessment:** the shape is anticipated at least four times, once in a granted patent and three
times academically. Only the *criterion* might survive, and its survival is contingent on reading
Krishnan and Van Wyk 2012 and Söderberg and Hedin (SLE 2013) in full.

### High — do not claim

**Predicting resource requirements, work quantity, or scheduling priority from source content.**

US20210232492A1 (Red Hat) claims estimating the amount of work to regenerate a program. Further
granted patents cover extracting features from a source corpus and predicting resource allocation.

**Assessment:** AuxFlow makes no cost-prediction claim and should not acquire one. If workload
metadata is ever attached to work items as stretch work it must be a *classification* (does this
document converge; is it certified) rather than a *predicted cost*, and even then it must not be
presented as inventive.

Separately, US20220197616A1 (Red Hat) **claims** a machine-learning model determining "a number of
compilation passes in the set of compilation passes". The mechanism is unrelated — pass-pipeline
selection, not fixpoint iteration — but the phrasing collides. AuxFlow must avoid the phrase
"determining a number of compilation passes".

### Medium

**Constructing a cross-reference dependency graph from document source.** Anticipated by at least
three existing tools. The graph is not the contribution.

**Parsing document source to determine which build tools to invoke.** Anticipated by existing build
tools that parse LaTeX source. Dead-tool elimination is a useful engineering feature, not a
contribution.

**Instance-level, sub-file fact granularity over auxiliary content.** Pluto's BibTeX builder already
uses "a custom stamper that parses the aux file, extracts the bibliography name and the set of
referenced citation keys, and uses them as a stamp"; `labelschanged` already reports individual label
instances with before and after values. Only *static derivation from source* remains.

### Low

**Checksum-based convergence detection.** Unpatented common practice across `latexmk`, ConTeXt,
`rerunfilecheck`, Tectonic, Typst and Excel's calculation chain. Explicitly reimplemented rather than
claimed.

**Source-span attribution for TeX.** A SyncTeX feature, published TeX-community prior art.

## What appears unoccupied

Stated conservatively, narrowly, and only after everything above.

**Classifying feedback in a dependency graph by whether a value can influence the *quantity* of
generated artefact, and using that to decide whether classical fixed-graph fixpoint theory applies at
all — then emitting, before execution, a source-attributed diagnosis of the participating facts.**

Three properties distinguish it from the art above:

1. It is a **precondition test**, not a count and not a monotonicity test. The anticipating work
   either computes how many iterations are needed, or assumes convergence, or allocates the
   convergence obligation to the author. This decides whether a finite count can be expected to exist
   at all.
2. It depends on a distinction that **cannot arise in a fixed-graph setting**, because there no value
   alters the number of nodes. That is the gap between AuxFlow's setting and Farrow's, Jones's and
   Mentor Graphics'. It is *not* a gap against Krishnan and Van Wyk 2012 or Söderberg and Hedin 2013,
   which is why those must be read before this paragraph is relied on.
3. Its output is **an attributed diagnosis derived without execution**, not a schedule and not a
   generated evaluator.

The targeted patent query — `"taint analysis" "loop bound" "amount of" output generated static` —
returns zero results. No patent was found on static convergence classification of document
compilation, on classifying dependency cycles by whether a value affects the quantity of generated
work, or on cloud or automated LaTeX compilation as such.

*Potentially patentable subject to professional prior-art and patentability review.*

A claim of this shape would need to recite, at minimum: parsing a document source into fact instances
with source locations; constructing a dependency graph with pass-lag weights; determining by
propagation which fact values reach constructs governing the quantity of generated content;
identifying strongly connected components containing such a dependency; classifying the document on
that basis; and emitting a diagnosis identifying the participating facts without executing the
document compiler.

**That is a narrow claim. It should be understood as narrow.** And note that patent-unoccupied is not
the same as novel: Typst ships exactly this diagnostic output today, dynamically, and `labelschanged`
ships label-instance attribution for LaTeX. The unoccupied part is the static derivation, nothing
else.

## Claims that must never be made

1. That AuxFlow invented static pass-number assignment, minimisation, or any bound derived from graph
   structure.
2. That "find SCCs, classify each by convergence behaviour, notify the user" is a new pattern.
3. That no prior work distinguishes cycles that move values from cycles that change how much content
   exists.
4. That AuxFlow's setting has no analogue in the attribute-grammar literature.
5. That a dependency cycle proves a document cannot converge, or that its absence proves it can.
6. That AuxFlow detects all non-convergent documents even within its subset. It provably does not:
   mechanisms M3, M4, M6 and M7 in [RELATED-WORK.md](RELATED-WORK.md) section 7.3.
7. Any universal soundness claim of the form "predicted runs is always at least required runs" — the
   required count may not exist.
8. That engine warnings are a sound completion oracle, or that AuxFlow's use of state comparison is
   novel.
9. That dynamic convergence detection necessarily costs one extra execution. latexrun and Tectonic do
   not.
10. That existing tools report no cause for non-convergence. Typst, `labelschanged` and Tectonic do.
11. That observing non-convergence to be undecidable is an insight. `latexmk`'s shipped source says
    it, and Mädje's 2022 thesis proves it via Rice's theorem.
12. Any resource-cost or scheduling-priority prediction from document content.
13. That the analysis applies to arbitrary TeX rather than to a declared subset.
14. Any performance claim not backed by a committed measurement script.

## What would be needed for a real assessment

- Full granted claim sets for the records currently held at index-snippet level: US20110314365A1,
  US20210232492A1, US20220197616A1, US11829738B2.
- Espacenet and WIPO Patentscope cross-checks. Everything on record is from Google Patents.
- CPC-scoped rather than keyword-only searches, in particular G06F8/41, G06F8/71, G06F40/106 and
  G06F30/327. Keyword search alone under-covers a landscape.
- EP and CN family members of US20240272888A1.
- A professional search, which a student search cannot substitute for.
- An assessment of **obviousness**, not merely novelty. A combination of known techniques can be
  novel and still unpatentable, and this combination is not exotic — it is Farrow 1986 plus Jones
  1990 plus a domain-specific taint criterion.

## Position for the project

Proceed on the assumption that the contribution is **publishable but almost certainly not
patentable**, and design the report accordingly: concede the prior art in the first section, claim
the precondition test narrowly and conditionally, and let the mechanism taxonomy and the oracle
comparison carry the weight. Those two are the parts with no located anticipation of any kind.

If the classification result proves strong enough to be worth protecting, seek professional review
before any public disclosure — noting that a course report or a public repository is itself a
disclosure in most jurisdictions, and that this repository already is one.
