# Patent prior art

Search area: patents. Audit date 2026-08-27.

Scope: independent verification of the two patents the AuxFlow project has on
record, plus concept searches on Google Patents full-text search for the
mechanisms AuxFlow proposes. This is an engineering prior-art record, not a
freedom-to-operate opinion. See the caveat at the end.

Method note applied throughout: a patent's **specification** (title, abstract,
background, detailed description) can mention any concept the drafter liked;
only the **claims** define the exclusive right. A concept that appears in a
description but in no claim is prior art for novelty purposes (it is published
disclosure) but is not infringed. This file separates the two everywhere.

## Search log

### Google Patents - US10025569 direct record
query    : https://patents.google.com/patent/US10025569B1/en
examined : 1 result
outcome  : HTTP 404. Wrong kind code. B1 does not exist for this number.
status   : SOURCED (negative)

### Google Patents - US10025569 direct record, B2 kind code
query    : https://patents.google.com/patent/US10025569B2/en
examined : 1 result (full record, description + all 15 claims + legal events)
outcome  : VERIFIED. Texas Instruments. See Verified sources P1-1.
status   : SOURCED

### Google Patents - US20240272888 direct record
query    : https://patents.google.com/patent/US20240272888A1/en
examined : 1 result (full record, description + all 21 claims + legal events)
outcome  : VERIFIED. SAP SE. See Verified sources P1-2. Critically, "diameter"
           appears in DEPENDENT claims 3, 4, 10, 11, 17, 18 - not only in the
           description, and not in independent claim 1.
status   : SOURCED

(Priority 2 search log entries appended below under "Priority 2 search log".)

## Verified sources

### P1-1. US10025569B2 - Texas Instruments - VERIFIED

Citation
: Alan L. Davis, Paul Fuqua, Timothy John Harvey, "Linear-time algorithm to
  determine the maximum number of iterations of the iterative algorithm for
  data-flow analysis for reducible loops", US Patent 10,025,569 B2.

| Field | Verified value |
| --- | --- |
| Publication number | US10025569B2 |
| Also published as | US20180024820A1 (2018-01-25) |
| Title | Linear-time algorithm to determine the maximum number of iterations of the iterative algorithm for data-flow analysis for reducible loops |
| Assignee (current and original) | Texas Instruments Inc / TEXAS INSTRUMENTS INCORPORATED |
| Inventors | Alan L. Davis; Paul Fuqua; Timothy John Harvey |
| Application number | US 15/213,425 |
| Priority date | 2016-07-19 |
| Filing date | 2016-07-19 |
| Grant / publication date | 2018-07-17 |
| Legal status | **Active**. Assignment recorded 2016-10-06 (REEL/FRAME 039951/0590). STCF "PATENTED CASE" 2018-06-27. Maintenance fee 4th year paid 2021-12-17 (M1551, large entity). Maintenance fee 8th year paid 2025-12-18 (M1552, large entity). No fee-related expiry. |
| Anticipated expiration | 2036-07-19 |
| CPC | G06F8/433 (dependency analysis; data or control flow analysis); G06F8/443 (optimisation) |
| Claim count | 15 (two independent: claim 1 method, claim 9 CRM) |

URL: https://patents.google.com/patent/US10025569B2/en
PDF: https://patentimages.storage.googleapis.com/90/70/b4/68377538abeb42/US10025569.pdf
Access: full text, full claims, full legal-event history.

**Independent claim 1, verbatim** (the record's own line breaks preserved):

> What is claimed is:
>
> 1. A method for compiling a high level language (HLL) program into a machine
> level language (MLL) program readable by a target computer, the method
> comprising:
>
> forming an initial control flow graph of the HLL program, the initial control
> flow graph including nodes and edge, the nodes including a starting node;
>
> initializing a collapse count to zero;
>
> setting the initial control flow graph as a current control flow graph;
>
> performing iterative collapsing operations on the current control flow graph
> until only a single node remains, wherein each iteration of the iterative
> collapsing operations includes:
>
> detecting each node in the current control flow graph that has a backedge
> into a current starting node;
>
> for each detected node, performing a collapsing operation in which all nodes
> of the current control flow graph between the detected node and the current
> starting node are collapsed into a new starting node;
>
> incrementing the collapse count by one for each collapsing operation;
>
> updating the current control flow graph to include the new starting node; and
>
> if the updated control flow graph includes more than one node, setting the
> new starting node as the current starting node and the updated control flow
> graph as the current control flow graph;
>
> after performing the iterative collapsing operations, performing data flow
> analysis on the initial control flow graph for a number of iterations equal
> to one greater than the collapse count; and
>
> generating the MLL program corresponding to the HLL program based upon the
> data flow analysis.

**Exactly what claim 1 covers.** A method of *compiling HLL source into machine
code*, in which the compiler (a) builds a control flow graph, (b) computes the
loop-connectedness number d(G) by a specific named procedure - repeatedly
detect nodes with a backedge into the current start node, collapse everything
between them into a new start node, count collapses - until one node remains,
(c) runs data-flow analysis for exactly collapse-count + 1 iterations, and (d)
emits machine code from that analysis. Every one of those steps is a
limitation. Claim 9 is the same method as a non-transitory storage medium.

Notable dependent claims:
- Claim 2/10: run the analysis per-variable, **keep** the converged variables
  and **discard** only the non-converged ones.
- Claim 3/11: converged := value unchanged between iterations; non-converged :=
  value changed between the next-to-last and last iteration.
- Claim 8/15, verbatim: *"The method of claim 1, wherein the initial control
  flow graph comprises a plurality of strongly connected components (SCCs)."*
  This is a characterisation of the input graph, not an SCC-finding step.

**Description mentions but claims do not cover.** The specification frames the
problem generally ("the upper bound on the number of required iterations before
the sets converge or may be expected to not converge is defined by a theoretic
characteristic of the control-flow graph of the program called loop
connectedness known as d(G)") and criticises the prior-art practice of choosing
"a maximum number of data-flow analysis iterations arbitrarily", with
convergence "determined when no tracked values changed during the prior
iteration". Those are disclosure. No claim covers arbitrary-cap-plus-checksum,
nor bounding iterations of anything other than compiler data-flow analysis
driving machine-code generation.

**What it does NOT do.** No documents, no typesetting, no cross-references, no
auxiliary files. No taint analysis. No classification of cycles by whether they
amplify work. No instance-level facts - the graph nodes are basic blocks. No
build plan for an external tool. The bound is loop connectedness of a
*reducible* control flow graph, which is a structural property of nesting
depth, not of the semantics of the values flowing round the loop.

**Relevance to AuxFlow.** This is squarely the closest patent to AuxFlow's
"predict the pass count from graph structure" step, and it is the reason
AuxFlow must not present static iteration-count prediction as new. The
underlying idea is older than the patent - the patent itself cites Sharir 1981
and Cooper et al., "Iterative Dataflow Analysis, Revisited" (ACM 2002) as
non-patent prior art, and the description concedes d(G) is a "theoretic
characteristic ... known as" loop connectedness.

**Anticipation verdict: PARTIAL OVERLAP.** It anticipates the *idea* of
computing an exact static iteration bound from graph structure and running the
fixpoint exactly that many times. It does not anticipate AuxFlow's document
domain, its instance-level fact graph, or its amplification/taint
classification. As a claim-scope matter the risk is LOW: AuxFlow does not
compile HLL to MLL, does not build a control flow graph, and does not use the
backedge-collapse procedure.

**Risk rating: LOW** for infringement; **HIGH** as novelty-destroying art for
any AuxFlow claim phrased as "statically determine the number of fixpoint
iterations from the dependency graph".

Evidence label: SOURCED.

### P1-2. US20240272888A1 - SAP SE - VERIFIED (application, still pending)

Citation
: Joerg Weisbarth, "Resolving dependency graphs with cycles in parallel",
  US Patent Application Publication 2024/0272888 A1, SAP SE.

| Field | Verified value |
| --- | --- |
| Publication number | US20240272888A1 |
| Title | Resolving dependency graphs with cycles in parallel |
| Applicant / assignee | SAP SE (Germany). Assignment recorded 2023-02-15, REEL/FRAME 062706/0860. |
| Inventor | Joerg Weisbarth (sole) |
| Application number | US 18/169,364 |
| Priority date | 2023-02-15 |
| Filing date | 2023-02-15 |
| Publication date | 2024-08-15 |
| Legal status | **Pending.** Not granted. Docketed ready for examination 2023-04-10. NON FINAL ACTION MAILED 2025-12-24 and 2025-12-29. RESPONSE TO NON-FINAL OFFICE ACTION ENTERED AND FORWARDED TO EXAMINER 2026-03-30. So the claims are under active rejection and **the claim set below is the published set, which may narrow before grant.** |
| CPC | G06F8/61 (installation); G06F9/4881 (scheduling strategies for dispatcher) |
| Claim count | 21 as published (three independent: 1 method, 8 CRM, 15 system) |

URL: https://patents.google.com/patent/US20240272888A1/en
PDF: https://patentimages.storage.googleapis.com/05/57/32/b902a541d4749f/US20240272888A1.pdf
Access: full text, full claims, full legal-event history.

**Independent claim 1, verbatim as published:**

> What is claimed is:
>
> **1**. A computer-implemented method, comprising:
>
> in each iteration:
>
> determining whether there exists one still unevaluated action in a dependency
> graph;
>
> determining a set of still unevaluated actions without any unevaluated
> required dependencies;
>
> asynchronously starting an evaluation for each action in the set of still
> unevaluated actions, wherein evaluations execute in parallel without waiting
> on evaluation of other actions;
>
> waiting until at least one ongoing action evaluation has finished; and
>
> collecting all still uncollected results of finished asynchronous
> evaluations.

**Exactly what claim 1 covers.** A bare parallel topological-evaluation loop:
find ready nodes (no unevaluated required dependencies), fire them all
asynchronously, block until one finishes, harvest results, repeat. That is
Phase 1 of the disclosure only. Claim 1 recites **no** cycle handling, **no**
iteration bound, **no** diameter, and **no** convergence test. It is
strikingly broad and correspondingly vulnerable - which is consistent with the
non-final rejections on the docket.

**DIAMETER: IN THE CLAIMS, BUT ONLY THE DEPENDENT ONES.** This is the
distinction the audit asked for, and the project's prior belief was wrong in
one direction and right in the other. "Diameter" does **not** appear in any
independent claim (1, 8, 15). It **does** appear in dependent claims 3, 4, 10,
11, 17 and 18. Claim 3 verbatim:

> **3**. The computer-implemented method of claim 2, comprising:
>
> while a set of actions with changed inputs since a last iteration (AwChI))
> is not empty and the number of iterations (i) is<=the diameter (d) of the
> dependency graph:
>
> for each action in the AwChI:
>
> asynchronously and in parallel evaluate each action; and
>
> wait until at least one action evaluation has finished.

and claim 4 verbatim:

> **4**. The computer-implemented method of claim 3, comprising:
>
> exiting if the AwChI is empty or i>d.

Claims 10/11 and 17/18 are the CRM and system mirrors of 3/4, word for word.

So: capping re-evaluation rounds of a cyclic dependency graph by the graph's
diameter, and aborting when that cap is exceeded, **is claimed subject matter**
in a pending SAP application. Note the sloppy drafting in the published set -
claim 3 introduces "(d)" as the diameter, whereas the description's
corresponding text says "a reasonable upper bound for the number of iterations
i is considered to be the number of actions d", conflating d = diameter with
d = node count. That inconsistency is examiner bait but does not help AuxFlow.

**Description mentions but claims do not cover.** The description names the
application domains explicitly:

> Common examples can include installers for software-packages, software
> build-tools, spreadsheet calculators, and service management of
> infrastructural services within a cloud where one service may depend on
> another service to be available.

Software build tools and spreadsheet calculators are therefore **disclosed** as
target domains - relevant as prior-art disclosure - but no claim is limited to
or directed at them. The description also derives the bound:

> Let the diameter (d) of the dependency graph be the maximum distance (counted
> in edges) between any two vertices. ... it takes at most [d] iterations until
> the effects of this change have been propagated through the whole
> dependency-graph. The upper bound on for any dependency-graph is , v-1 which
> adds up to v with the first evaluation in the second phase.

and, importantly for AuxFlow's non-convergence story, states as an aim of the
invention: *"during evaluation, a case of (forever) unstable inputs is detected
and the evaluation aborted"*. That is exactly the abort-on-non-convergence
posture, disclosed in 2023, but implemented as a *dynamic* round cap, not a
static classification.

**What it does NOT do.** No static pre-analysis: the diameter bound is applied
at runtime while actually evaluating. No distinction between a benign cycle
that will converge and an amplifying one that will not - the SAP method treats
exceeding the cap as failure regardless of cause. No taint analysis, no notion
of a value influencing the *quantity* of work. No documents, no typesetting, no
source-level diagnosis. Nodes are deployments, not fact instances. No pass-lag
edge semantics (write in run p, readable in run p+1).

**Relevance to AuxFlow.** Directly occupies "bound the re-evaluation rounds of
a cyclic dependency graph by a structural graph metric, and abort when
exceeded". AuxFlow's fixpoint-over-condensation pass-number propagation is a
static analogue of the same insight. AuxFlow must not claim the general idea of
diameter-bounded or node-count-bounded iteration over a cyclic dependency graph
as its own.

**Anticipation verdict: PARTIAL OVERLAP**, strongest of the two on the cyclic
side. Not full anticipation: AuxFlow's classification of cycles by amplification
is absent here, and the SAP bound is dynamic where AuxFlow's is static.

**Risk rating: MEDIUM.** Pending, not granted, under non-final rejection, and
the diameter limitation sits in dependent claims that AuxFlow would only reach
if it actually ran evaluations in parallel while counting rounds against the
diameter. AuxFlow as described does not execute the actions at all. But if
AuxFlow ever ships a *driver* that reruns the engine and caps rounds by a graph
metric, re-check this file's status - claim 3 is the one to watch.

Evidence label: SOURCED.

## Priority 2 search log

All Priority 2 queries were run against the Google Patents full-text search
backend at `https://patents.google.com/xhr/query?url=q%3D<query>`, which is the
JSON endpoint behind the `patents.google.com/?q=` UI. The plain HTML search page
returns an empty JS shell and is unusable for automated reading; the XHR
endpoint returns the same result set with titles, assignees, dates and matched
snippets. Every query string below is verbatim and re-runnable.

### Concept 1 - bounding fixpoint / dataflow iteration counts from graph structure
query    : `"maximum number of iterations" "data flow analysis" "control flow graph" bound`
examined : 33 results, top 10 reviewed
outcome  : US10025569B2 (already verified, P1-1) is the on-point hit and ranks
           second. Remainder are symbolic-execution and LLM-repair noise. No
           second family occupying the same idea surfaced.
status   : SOURCED

query    : `"number of passes" "attribute grammar" evaluation static`
examined : 0 results
outcome  : NOTHING RELEVANT. The attribute-grammar multipass literature
           (Bochmann 1976, Alblas 1981, Raiha and Ukkonen) appears to have no
           US patent footprint at all. That is the expected result for 1970s
           academic compiler theory, and it means the *academic* prior art in
           this area is stronger and older than the *patent* prior art.
status   : SOURCED (negative)

query    : `"strongly connected component" "fixed point" iterations bound compiler`
examined : 8 results, all reviewed
outcome  : Surfaced US20090044157A1 / US8181129B2 (Mentor Graphics), the single
           most dangerous record found in this audit. See P2-1.
status   : SOURCED

query    : `"number of compilation passes"`
examined : 17 results, top 4 reviewed
outcome  : Only incidental uses. US20220197616A1 (Red Hat, Ulrich Drepper,
           "Compilation framework for hardware configuration generation") claims
           a machine-learning model that determines "a number of compilation
           passes in the set of compilation passes" - but that is ML selection
           of optimisation passes, not derivation of a pass count from a
           dependency graph. The Ericsson obfuscation family (US8522047B2,
           US8286251B2, US8393003B2) uses the phrase only in boilerplate.
status   : SOURCED

### Concept 2 - dependency-graph build scheduling, predicting build/rebuild rounds
query    : `"build plan" "dependency graph" "number of iterations" rebuild`
examined : 0 results
outcome  : NOTHING RELEVANT. No patent couples a build plan to a predicted
           iteration count.
status   : SOURCED (negative)

query    : `"predicting" "build time" OR "number of builds" "static analysis" source code`
examined : 23 results, top 10 reviewed
outcome  : CI/CD pipeline noise (Oracle, PayPal, Accenture, Cisco, SeaLights).
           All are about scheduling, caching and test selection, none about
           deriving a round count from graph structure.
status   : SOURCED

### Concept 3 - convergence detection in iterative builds / iterative computation
query    : `"convergence" "iterative build" detect stable output rebuild`
examined : 1 result (a bacterial DNA methyltransferase patent)
outcome  : NOTHING RELEVANT. The phrase "iterative build" is not patent
           vocabulary. Convergence detection by output comparison appears to be
           unpatented common practice - consistent with the tools-side finding
           that checksum comparison is the standard baseline (latexmk,
           ConTeXt's MD5 of the .tuc file, rerunfilecheck).
status   : SOURCED (negative)

### Concept 4 - detecting AND classifying circular dependencies
query    : `"combinational loop" monotonic "strongly connected component" classify`
examined : 0 results (over-constrained; the word "classify" is not used)
outcome  : Zero, but the same family was reached via the Concept 1 SCC query.
status   : SOURCED (negative, superseded)

query    : `"circular dependency" detecting classifying "dependency graph" build`
examined : 306 results, top 10 reviewed
outcome  : Broad and noisy. Nearest is US11657210B2 (Palantir) which claims
           *implementing* a circular dependency between linked UI panels, not
           classifying one. Nothing classifies a cycle by its convergence
           behaviour. See also P2-4.
status   : SOURCED

query    : `"cyclic dependency" "resolvable" OR "unresolvable" classify graph software build`
examined : 1226 results, top 10 reviewed
outcome  : NOTHING RELEVANT. The OR pulled the query into NLP intent
           classification ("resolvable class or the unresolvable class",
           Oracle chatbot patents). Query is too loose to be probative; recorded
           so it is not re-run in this form.
status   : SOURCED (negative, query defective)

### Concept 5 - spreadsheet circular references and iterative recalculation
query    : `"circular reference" "iterative calculation" spreadsheet`
examined : 7 results, all reviewed
outcome  : Thinner than expected. Nearest are Microsoft's calc-chain family
           (AU2007259398B2 / KR101354810B1, "Multithread spreadsheet processing
           with dependency levels") and US20110314365A1 (Microsoft,
           "Decompiling loops in a spreadsheet"). See P2-2 and P2-3.
status   : SOURCED

query    : `"iterative calculation" spreadsheet "maximum iterations" convergence threshold`
examined : 0 results
outcome  : NOTHING RELEVANT. Excel's documented iterative-calculation feature
           (max-iterations plus max-change convergence threshold) does not
           appear to be claimed in any patent reachable by this phrasing. It is
           nevertheless well-known published prior art through the product
           itself.
status   : SOURCED (negative)

### Concept 6 - static workload / resource estimation from source code
query    : `"estimating" "computational resources" "from source code" static analysis before execution`
examined : 46 results, top 10 reviewed
outcome  : Confirms the area is occupied. Concrete hit: US20210232492A1
           (Red Hat) claims estimating the amount of work to regenerate a
           program. Edge-orchestration patents (Intel EP3974980A1,
           US11630706B2) claim resource estimation but from workload
           descriptors, not source. See P2-5.
status   : SOURCED

### Concept 7 - document compilation, typesetting automation, cross-reference resolution
query    : `"cross-reference" document "multiple passes" typesetting compile resolve`
examined : 10 results, all reviewed
outcome  : NOTHING RELEVANT. Adobe colour separation, video-game level
           generation, autoencoder media compression. No patent on multipass
           cross-reference resolution in documents.
status   : SOURCED (negative)

query    : `"page number" "cross reference" recompile document "second pass" resolve`
examined : 5 results, all reviewed
outcome  : NOTHING RELEVANT. All five matched only on the boilerplate
           "CROSS-REFERENCE TO RELATED APPLICATIONS" heading, which is a
           systematic false-positive trap for this concept area. Any future
           search in this area must exclude that phrase.
status   : SOURCED (negative)

query    : `LaTeX compilation cloud automated document typesetting server`
examined : 87 results, top 10 reviewed
outcome  : Only one genuinely TeX-related record: US20200257755A1 (IBM,
           "Collecting training data from TeX files"). See P2-6. No patent on
           cloud LaTeX compilation as such, on build orchestration for LaTeX,
           or on rerun scheduling for LaTeX.
status   : SOURCED

query    : `"taint analysis" "loop bound" "amount of" output generated static`
examined : 0 results
outcome  : NOTHING RELEVANT. This is the query aimed squarely at AuxFlow's
           distinctive claim - taint from a fact value to the quantity of
           generated content. Zero hits.
status   : SOURCED (negative)

## Priority 2 assessed records

### P2-1. US8181129B2 / US20090044157A1 - Mentor Graphics, now Siemens - THE DANGEROUS ONE

| Field | Verified value |
| --- | --- |
| Publication numbers | US20090044157A1 (pub 2009-02-12); granted as US8181129B2 (2012-05-15) |
| Title | Acyclic modeling of combinational loops |
| Applicant / original assignee | Mentor Graphics Corp |
| Current assignee | Siemens Industry Software Inc (merger and change of name recorded 2021-06-29) |
| Inventors | Amit Gupta; Charles W. Selvidge |
| Application number | US 12/249,320 (continuation; parent US 11/068,036, granted US7454722B2; provisional US 60/627,172) |
| Priority date | 2004-11-15 |
| Filing date | 2008-10-10 |
| Status | **Active**, granted. Adjusted expiration 2026-12-25 - i.e. it expires within four months of this audit date. |
| CPC | G06F30/35, G06F30/327 |
| Claims | 19 (independent: 1 CRM, 10 method, 18 computer-assisted method) |

URL (application): https://patents.google.com/patent/US20090044157A1/en
URL (grant): https://patents.google.com/patent/US8181129B2/en
Access: full text of application, full granted claim set.

**Granted claim 1, verbatim:**

> 1. A computer-readable storage medium storing computer-executable instructions
> for converting a combinational loop in a circuit design into an acyclic
> circuit, the instructions defining steps including:
>
> determining whether the combinational loop is monotonic; and
>
> responsive to a determination that the combinational loop is monotonic,
> transforming the combinational loop into an acyclic path by adding at least
> one state-holding element.

Operative dependent claims, verbatim:

> 6. The computer-readable medium method of claim 1, wherein the instructions
> further define a step of notifying a user responsive to a determination that
> the combinational loop is not monotonic.

> 7. The computer-readable medium of claim 1, wherein the instructions further
> define a step of determining a Strongly Connected Component (SCC) of the
> design, wherein the combinational loop is contained in the SCC.

> 2. ... determining a function F(I), a function G(I), and a function B(I),
> wherein I represents at least one non-cyclic input to the loop, such that
> A =(F(I) AND A) OR (G(I) AND INV(A)) OR B(I), and wherein A represents a first
> output of the loop; and determining whether G(I) is zero or nonzero,
> determining that the combinational loop is monotonic based on a determination
> that G(I) is zero.

**Technical mechanism.** Find the SCCs of the design graph (the description
cites Cormen et al. chapter 21, i.e. the textbook Tarjan/Kosaraju treatment).
For each feedback loop inside each SCC, decide a *semantic* property of the
loop - whether it is "monotonic", defined in the description as: *"the term
'monotonic' implies that if the loop is closed, the loop output does not change
its value, or in other words, the loop output holds its previous value."*
Monotonic loops are provably non-oscillatory and get rewritten into acyclic
form. Non-monotonic loops are *"not converted"* and *"the user may be notified
... that the loop is not monotonic and is therefore likely to be oscillatory
and problematic ... The user may find this helpful because it may signify that
there is an error in the design."*

**Specific overlap with AuxFlow.** This is the same three-step shape as
AuxFlow's core:
1. Build a dependency graph of the artefact under analysis.
2. Find SCCs.
3. Classify each SCC by a semantic property of the values circulating in it,
   separating the well-behaved cycles (which converge / hold their value) from
   the ill-behaved ones (which may oscillate and never settle), and report the
   ill-behaved ones to the user as a design error.

That is structurally AuxFlow's BENIGN_CYCLIC versus AMPLIFYING split, done in
2004 for gate-level circuits. The correspondence is close enough that AuxFlow
cannot present "find SCCs, then classify each by whether it can fail to
converge, then diagnose the bad ones to the user" as a new idea.

**What it does NOT do.** The classification criterion is entirely different in
kind. Monotonicity here is a Boolean-function property (G(I) = 0 in a
sum-of-products decomposition over a fixed, finite signal lattice). AuxFlow's
criterion is whether a fact value can influence *how much content the document
generates* - an unbounded-quantity/amplification property with no analogue in a
combinational circuit, where the signal set is fixed by construction and no
loop can create new nodes. There is no taint analysis, no pass-lag semantics,
no notion of a value feeding back with a one-round delay into a *larger*
artefact, no source-span diagnosis, no build plan, and no documents. Expiry in
December 2026 also removes it as an infringement concern almost immediately.

**Risk rating: LOW for infringement** (circuit-design-limited preamble in every
independent claim; expires 2026-12-25). **HIGH as novelty-destroying art** for
any AuxFlow claim of the form "identify strongly connected components and
classify each as convergent or potentially non-convergent, notifying the user
of the latter".

Evidence label: SOURCED.

### P2-2. US20110314365A1 - Microsoft - "Decompiling loops in a spreadsheet"

| Field | Verified value |
| --- | --- |
| Publication number | US20110314365A1 |
| Title | Decompiling loops in a spreadsheet |
| Applicant | Microsoft Corporation |
| Priority date | 2010-06-17 |
| Publication date | 2011-12-22 |
| Status | metadata only at time of audit; not re-verified for grant/abandonment |

Matched snippet, verbatim from the Google Patents search index: *"A computer
program product for use at a computer system, the computer program product of
implementing a method for identifying looping semantics within a spreadsheet"*.

**Overlap.** Recovering loop structure from a declarative recalculation graph is
adjacent to AuxFlow's problem of recovering iteration structure from a
declarative document. **What it does not do:** no convergence classification, no
iteration-count prediction, no distinction between benign and amplifying cycles.

**Risk rating: LOW.** Different problem (structure recovery, not convergence).
Evidence label: REPORTED - only the index snippet and bibliographic metadata
were read; the claims were not opened. Listed as an outstanding search below.

### P2-3. AU2007259398B2 / KR101354810B1 - Microsoft - spreadsheet calc chain

| Field | Verified value |
| --- | --- |
| Publication numbers | AU2007259398B2 (granted 2012-01-19); KR101354810B1 (2014-01-22) |
| Title | Multithread spreadsheet processing with dependency levels |
| Assignee | Microsoft Technology Licensing, LLC |
| Priority date | 2006-05-08 |

Matched snippet, verbatim: *"Sorting, by one or more processors, the equations
into a single calculation chain, Attempting to evaluate a first formula of the
single calculation chain, Moving the dependent ..."*.

**Technical mechanism.** The Excel calc-chain algorithm: attempt evaluation in a
guessed order, and when a formula turns out to depend on an unevaluated cell,
move it later in the chain and retry. That is *dynamic* discovery of evaluation
order by re-running, the direct spreadsheet analogue of "run LaTeX again and see
if the aux file changed".

**Overlap with AuxFlow.** Reinforces that the dynamic baseline - iterate until
stable, discover the order at runtime - is long-established practice in a second
independent domain. AuxFlow's claim to differentiation must therefore rest on
staticness plus classification, not on the iterate-to-stability idea.

**Risk rating: NONE** for infringement (spreadsheet-limited, non-US
jurisdictions in this record). Useful as context.
Evidence label: REPORTED - index snippet and metadata only.

### P2-4. US11657210B2 - Palantir - circular dependency between UI panels

| Field | Verified value |
| --- | --- |
| Publication number | US11657210B2 |
| Title | Cached database and synchronization system for providing dynamic linked panels of user interface |
| Assignee | Palantir Technologies Inc. |
| Priority date | 2016-07-21 |
| Publication date | 2023-05-23 |

Matched snippet from claim 6/7, verbatim: *"the second action is associated with
the first panel, creating a circular dependency between the first panel and the
second panel. 7. The computer system of claim 6, wherein the circular dependency
is implemented, in the generated code, by at least one of: ..."*.

**Assessment.** The claim *creates and implements* a circular dependency; it does
not detect, classify, or bound one. Surfaced only to record that the highest-
ranked "circular dependency" claim language in the 306-hit search is about
building cycles, not analysing them.

**Risk rating: NONE.** Evidence label: REPORTED - index snippet only.

### P2-5. US20210232492A1 - Red Hat - "History based build cache for program builds"

| Field | Verified value |
| --- | --- |
| Publication number | US20210232492A1 |
| Title | History based build cache for program builds |
| Applicant | Red Hat, Inc. |
| Priority date | 2020-01-27 |
| Publication date | 2021-07-29 |

Matched claim language, verbatim from the search index: *"wherein estimating the
amount of work to regenerate the program includes one of (i) determining a
quantity of source files that differ between the first list and the second list,
(ii) determining a cumulative size of each file in the third list, and (iii)
d[etermining] ..."*.

**Technical mechanism.** Estimate the cost of rebuilding by comparing file lists
and sizes against build history, and use the estimate to decide cache policy.

**Specific overlap with AuxFlow.** This is the first of the two concrete records
confirming that "statically estimate how much work a build will take, from the
source, before running it" is claimed territory. AuxFlow's build plan - "this
document will need N passes" - is a work estimate for a build. **What it does
not do:** the estimate is history-and-size based, not derived from a dependency
graph's structure, and there is no cycle handling and no convergence question.

**Risk rating: LOW,** but this is the record to cite when the project says the
static-workload-estimation area is occupied.
Evidence label: REPORTED - claim-language snippet from the full-text index; the
full claim set was not opened.

### P2-6. US20200257755A1 - IBM - "Collecting training data from TeX files"

| Field | Verified value |
| --- | --- |
| Publication number | US20200257755A1 |
| Title | Collecting training data from TeX files |
| Applicant | International Business Machines Corporation |
| Priority date | 2019-02-08 |
| Publication date | 2020-08-13 |

Abstract, verbatim from the record: *"A method of collecting training data of a
document component may be provided. The documents have a structure and are coded
in the typesetting language TeX. The method comprise receiving a TeX source
file, compiling it into a PDF file and a related sync file, ..."*

**Assessment.** The only substantive TeX-domain patent this audit surfaced. It
compiles TeX and consumes the SyncTeX file to map PDF regions back to source
spans - i.e. it uses source-span mapping, which AuxFlow also needs for its
diagnosis output. But the purpose is machine-learning corpus construction. There
is no analysis of the TeX source, no dependency graph, no passes, no
convergence.

**Specific overlap with AuxFlow: source-span attribution for TeX only.** That is
a SyncTeX feature, published TeX-community prior art independent of this patent.

**Risk rating: NONE.** Evidence label: SOURCED (abstract read in full from the
search record; claims not opened).

### P2-7. US20220197616A1 - Red Hat - compilation-pass count chosen by ML

| Field | Verified value |
| --- | --- |
| Publication number | US20220197616A1 |
| Title | Compilation framework for hardware configuration generation |
| Applicant | Red Hat, Inc. |
| Inventor | Ulrich Drepper |
| Priority date | 2020-12-18 |
| Publication date | 2022-06-23 |

Matched claim language, verbatim: *"wherein the first configuration information
comprises data representing a machine learning model trained to perform at least
one of determining whether to identify an additional configuration information,
or determining a number of compilation passes in the set of compilation passes."*

**Assessment.** The only record found that *claims* determining a number of
compilation passes. But "passes" here means distinct optimisation stages in a
pass pipeline, chosen by a trained model - not repeated re-execution of the same
pipeline until a fixpoint. Orthogonal mechanism, colliding vocabulary. Worth
knowing because a careless AuxFlow claim phrased as "determining a number of
compilation passes" would read onto adjacent language.

**Risk rating: LOW.** Terminology hazard rather than substantive overlap.
Evidence label: REPORTED - claim-language snippet from the full-text index.

### P2-8. US11829738B2 - IBM - static block frequency prediction in irreducible loops

| Field | Verified value |
| --- | --- |
| Publication number | US11829738B2 |
| Title | Static block frequency prediction in irreducible loops within computer code |
| Assignee | International Business Machines Corporation |
| Priority date | 2021-12-10 |
| Publication date | 2023-11-28 |

Matched description snippet, verbatim: *"Loop 422 is an irreducible loop, since
node 406, in this example, does not dominate all the nodes (e.g., 408 and 410)
in the strongly connected component (e.g., irreducible loop 422). Besides the
irreducible loop 422, the reducible loop 424 also con[tains] ..."*

**Assessment.** Statically predicting a *quantitative* property (execution
frequency) of code regions from SCC and dominance structure. Relevant because it
is the closest thing found to "statically predict how much a cyclic region will
run", and because it covers the irreducible case that US10025569B2 explicitly
excludes. Nodes are basic blocks; there is no convergence classification and no
document domain.

**Risk rating: LOW.** Cite it if AuxFlow ever claims static quantitative
prediction over SCCs generally.
Evidence label: REPORTED - description snippet from the full-text index.

### P2-9. Bounded-iteration prior art cited *by* US10025569B2

The TI patent's own citation list is itself a compact prior-art map for
Concept 1, and is worth recording because it shows the examiner-acknowledged
state of the art:

- US5485616A, "Using program call graphs to determine the maximum fixed point
  solution of interprocedural bidirectional data flow problems in a compiler",
  granted 1996-01-16. Listed by Google Patents as a similar document. Determining
  a maximum fixed point solution from graph structure, in 1996.
- Non-patent citations on the face of US10025569B2: M. Sharir, "A
  Strong-Connectivity Algorithm and Its Applications in Data Flow Analysis",
  Comp. & Maths. with Appls. vol. 7, pp. 67-72, Pergamon Press Ltd., 1981; and
  Cooper et al., "Iterative Dataflow Analysis, Revisited", ACM 2002.

**Consequence for AuxFlow.** SCC-based decomposition of a dataflow problem plus
iteration to a fixpoint over the condensation is documented prior art from 1981,
cited on the face of a granted US patent. AuxFlow's "monotone fixpoint over the
graph condensation" step is textbook, and must be presented as such.

**Risk rating: NONE** (no exclusive right implicated; this is literature).
Evidence label: SOURCED (citation list read directly from the US10025569B2
record).

## Negative results

Exact, re-runnable queries that found nothing relevant. All were run against the Google Patents
full-text XHR endpoint `https://patents.google.com/xhr/query?url=q%3D<query>`.

```
"number of passes" "attribute grammar" evaluation static          -> 0 results
"build plan" "dependency graph" "number of iterations" rebuild    -> 0 results
"convergence" "iterative build" detect stable output rebuild      -> 1 result, unrelated (biology)
"iterative calculation" spreadsheet "maximum iterations" convergence threshold -> 0 results
"taint analysis" "loop bound" "amount of" output generated static  -> 0 results
"cross-reference" document "multiple passes" typesetting compile resolve -> 10 results, none relevant
"page number" "cross reference" recompile document "second pass" resolve -> 5 results, all matching
                                                                    only the boilerplate
                                                                    "CROSS-REFERENCE TO RELATED
                                                                    APPLICATIONS" heading
LaTeX compilation cloud automated document typesetting server     -> 87 results, one TeX-related
                                                                    (US20200257755A1, IBM), nothing
                                                                    on LaTeX build orchestration
```

Three specific negatives, each with the query that establishes it:

1. **No patent was found on static convergence classification of document compilation.** The
   nearest queries are the Concept 7 pair above plus the taint query. Zero relevant hits.
2. **No patent was found on classifying dependency cycles by whether a value affects the quantity of
   generated work.** The `"taint analysis" "loop bound" "amount of" output generated static` query
   returns zero. The closest thing in any jurisdiction is US8181129B2 (P2-1), which classifies cycles
   by a Boolean-function monotonicity property over a fixed signal set, not by work amplification.
3. **No patent was found on cloud or automated LaTeX compilation as such.** The Concept 7 query
   above examined 87 results and found only a machine-learning corpus-construction patent.

Note also, as a positive finding disguised as a negative: the attribute-grammar multipass literature
(Bochmann 1976, Alblas 1981, Raiha and Ukkonen 1980/1981) has **no US patent footprint reachable by
these queries at all**. The academic prior art in this area is therefore older, stronger and more
dangerous to AuxFlow's novelty than the patent prior art.

## Outstanding searches

Not reached in this pass. These must not be mistaken for negative results.

- Full granted claim sets for P2-2 (US20110314365A1), P2-5 (US20210232492A1), P2-7
  (US20220197616A1) and P2-8 (US11829738B2). Only index snippets and bibliographic metadata were
  read for these.
- Current legal status of P2-2 (grant or abandonment).
- Espacenet and WIPO Patentscope cross-checks. Everything here is from Google Patents and the USPTO
  legal-event history it exposes; no independent register was consulted.
- EP and CN family members of US20240272888A1, if any, since SAP files broadly.
- CPC-scoped searches rather than keyword searches, in particular G06F8/41 (compiling), G06F8/71
  (version control / build), G06F40/106 (display of document layout) and G06F30/327 (logic
  synthesis, where P2-1 lives). Keyword search alone under-covers a patent landscape.
- A search on the specific phrase family around "unstable" / "does not stabilize" / "fails to
  converge" as a *diagnostic output*, which is where Typst-style reporting would sit if patented.

## What AuxFlow must not claim

Each item is followed by the record that forecloses it.

1. **That it statically determines the number of fixpoint or dataflow iterations from graph
   structure.** Foreclosed as an idea by US10025569B2 (TI, granted, active to 2036) and, older and
   stronger, by Hecht & Ullman 1975 and Bochmann 1976. Infringement risk is LOW because the TI
   claims are limited to compiling HLL to MLL via a control flow graph and a specific
   backedge-collapse procedure; novelty risk is HIGH.
2. **That it is new to bound re-evaluation rounds of a cyclic dependency graph by a structural graph
   metric and abort when the bound is exceeded.** Claimed subject matter in dependent claims 3, 4,
   10, 11, 17 and 18 of US20240272888A1 (SAP, pending). Note the correction to the project's prior
   belief: "diameter" is in the claims, but only the dependent ones; the independent claims recite a
   bare parallel topological-evaluation loop with no bound at all.
3. **That "find the strongly connected components, classify each as convergent or potentially
   non-convergent, and notify the user of the latter" is new.** Foreclosed by US8181129B2 (Mentor
   Graphics / Siemens, "Acyclic modeling of combinational loops"), claim 1 plus dependent claims 6
   and 7: determine whether a combinational loop is monotonic; if not, do not transform it and
   notify the user; the loop is contained in an SCC of the design. This is AuxFlow's three-step core
   shape, applied to circuits in 2004.
4. **Any prediction of resource requirements, work quantity or scheduling priority from source
   content.** US20210232492A1 (Red Hat) claims estimating the amount of work to regenerate a
   program. The area is occupied.
5. **That "determining a number of compilation passes" is unclaimed language.** US20220197616A1
   (Red Hat) claims a machine-learning model that determines "a number of compilation passes in the
   set of compilation passes". The mechanism is unrelated but the phrasing collides; avoid it.
6. **That checksum or state-comparison convergence detection is inventive.** Unpatented common
   practice across latexmk, ConTeXt, rerunfilecheck, Tectonic, Typst and Excel's calc chain.

## What appears unoccupied

Stated narrowly, and only after the concessions above.

- **Classifying feedback in a dependency graph by whether a value can influence the *quantity* of
  generated artefact, and using that to decide whether classical fixed-graph fixpoint theory applies
  at all.** The `"taint analysis" "loop bound" "amount of" output generated static` query returns
  zero, and the closest art (P2-1) classifies by Boolean monotonicity over a fixed signal set, where
  no loop can create new nodes. This is the only element of AuxFlow with no located patent
  anticipation.
- **Pre-execution, source-span-level attribution of the specific facts responsible, for document
  compilation.** No patent found. But note that this is *not* unoccupied as published art: Typst
  ships exactly this output dynamically, and `labelschanged` ships label-instance attribution for
  LaTeX. Patent-unoccupied is not the same as novel.

Both are narrow, and both should be understood as narrow. The honest position remains that AuxFlow
is more likely publishable than patentable, and that a course report or a public repository is
itself a disclosure in most jurisdictions.

## Summary for the audit

- **Both named patents verified, and one project belief corrected.** US10025569B2 is Texas
  Instruments, granted 2018-07-17, **active**, maintenance fees paid through the 8th year, anticipated
  expiry 2036-07-19; claim 1 is limited to compiling HLL to MLL, computing loop-connectedness by a
  named backedge-collapse procedure, and running dataflow analysis for exactly collapse-count + 1
  iterations. US20240272888A1 is SAP SE, filed and priority 2023-02-15, published 2024-08-15, and is
  **still pending under non-final rejection** (actions mailed 2025-12-24 and 2025-12-29, response
  forwarded 2026-03-30). Its independent claims contain **no** diameter bound; "diameter" appears
  only in dependent claims 3/4/10/11/17/18.
- **Specification-mentions versus claims-cover matters in both cases.** TI's description criticises
  arbitrary iteration caps and checksum-based convergence detection, but no claim covers them.
  SAP's description names "software build-tools, spreadsheet calculators" as target domains, but no
  claim is limited to them.
- **THE MOST DANGEROUS RECORD IN THIS AUDIT IS NOT EITHER OF THE TWO ON RECORD.** It is
  **US8181129B2 / US20090044157A1, Mentor Graphics (now Siemens Industry Software), "Acyclic
  modeling of combinational loops"**, priority 2004-11-15, granted 2012-05-15, adjusted expiry
  2026-12-25. Claim 1: determine whether a combinational loop is monotonic, and if so transform it
  to acyclic form. Claim 6: notify the user when it is not monotonic. Claim 7: the loop is contained
  in a strongly connected component of the design. The description defines the classification in
  convergence terms and states that a non-monotonic loop "is therefore likely to be oscillatory and
  problematic". That is find-SCCs, classify-by-a-semantic-property-of-the-circulating-values,
  diagnose-the-bad-ones-to-the-user, twenty-two years before AuxFlow. Infringement risk LOW (circuit
  preamble, expires within months); novelty risk HIGH.
- **Patent risk to AuxFlow's freedom to operate is low across the board.** AuxFlow does not compile
  to machine code, does not build a control flow graph, does not synthesise circuits, and as
  specified does not even execute the actions it schedules. The only live watch item is SAP claim 3:
  if AuxFlow ever ships a driver that reruns the engine while counting rounds against a graph
  metric, re-check that file's status.
- **The real threat is to novelty, and it comes from the literature rather than the register.** The
  attribute-grammar multipass line has no patent footprint at all, which means the strongest
  anticipations of AuxFlow are academic papers from 1976-1990 that no patent examiner has ever had
  to consider. See `area-a-attribute-grammars.md` and `area-d-non-convergence.md`.
- **One element survives the patent search unoccupied:** classification of feedback by influence on
  the *quantity* of generated artefact. Zero hits on the query aimed squarely at it. That is the
  narrow claim, and it should be stated narrowly.

## Caveat

This is an engineering record of prior-art risk compiled from public databases by a non-professional
searcher, and it is **not legal advice**. Legal status fields are Google Patents' own assumptions
plus the USPTO legal-event history exposed on those records; they have not been confirmed against a
national register. Claim scope as published is not claim scope as granted. A professional search in
the relevant CPC classifications, and an assessment of obviousness rather than mere novelty, cannot
be substituted for by this document.
