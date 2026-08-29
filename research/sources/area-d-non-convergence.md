# Non-convergence and cyclic dependency classification

Search area D: non-convergence and cyclic dependency classification. Audit date 2026-08-27.

## Search log

### CrossRef REST API - Farrow 1986
query    : `https://api.crossref.org/works/10.1145/13310.13320`
examined : 1 record
outcome  : Metadata and FULL VERBATIM ABSTRACT confirmed. Rodney Farrow (Declarative Systems), "Automatic generation of fixed-point-finding evaluators for circular, but well-defined, attribute grammars", ACM SIGPLAN Notices 21(7):85-98, July 1986. 21 references. CrossRef records `is-identical-to` DOI 10.1145/12276.13320 (proceedings-level duplicate deposit for the 1986 Symposium on Compiler Construction).
status   : SOURCED

### CrossRef REST API - Jones 1990
query    : `https://api.crossref.org/works/10.1145/78969.78971`
examined : 1 record
outcome  : Metadata and FULL VERBATIM ABSTRACT confirmed. Larry G. Jones (Univ. of Illinois at Urbana-Champaign), "Efficient evaluation of circular attribute grammars", ACM TOPLAS 12(3):429-462, July 1990. Abstract explicitly states SCC partitioning of the attribute dependency graph plus topological sort of the condensation. DIRECT ARCHITECTURAL HIT.
status   : SOURCED

### CrossRef REST API - Magnusson/Hedin DOI disambiguation
query    : `https://api.crossref.org/works/10.1016/j.scico.2005.06.005` and `https://api.crossref.org/works/10.1016/j.scico.2007.01.005`
examined : 2 records
outcome  : DISCREPANCY RESOLVED IN FAVOUR OF THE AUXFLOW REPOSITORY. See the dedicated correction note below. 10.1016/j.scico.2005.06.005 is the Magnusson/Hedin paper; 10.1016/j.scico.2007.01.005 is an unrelated paper on game scripting.
status   : SOURCED

### Lund University SDE preprint server
query    : `https://fileadmin.cs.lth.se/sde/publications/papers/2007-MagnussonEva-CRAGs-SCP-Preprint.pdf`
examined : full PDF, text extracted
outcome  : Preprint obtained and read. Both quotes flagged by the previous attempt verified verbatim with section locations. Also yielded a high-value secondary description of Jones's and Farrow's algorithms, and the Knuth / Rodeh-Sagiv / Boyland circularity-decidability results.
status   : SOURCED

## Verified sources

### D1. Farrow 1986 - PRIORITY 1, the most dangerous item in this area

Citation : Rodney Farrow, "Automatic generation of fixed-point-finding evaluators for circular, but well-defined, attribute grammars", ACM SIGPLAN Notices 21(7):85-98, July 1986. Proceedings of the 1986 SIGPLAN Symposium on Compiler Construction. Affiliation: Declarative Systems.
DOI/URL  : https://doi.org/10.1145/13310.13320 (CrossRef also lists identical deposit 10.1145/12276.13320)
Access   : metadata + complete structured abstract via CrossRef; full text paywalled at ACM DL (see Negative results). Secondary technical description of the algorithm obtained from Magnusson/Hedin 2007 Section 2.2, which is a primary-source description by later researchers who implemented a competing scheme.
Evidence label : SOURCED (abstract verbatim; algorithm description SOURCED via Magnusson/Hedin, i.e. second-hand but from a peer-reviewed primary source that engages with Farrow directly).

Verbatim quote - complete abstract, from the CrossRef `abstract` field (JATS paragraphs joined):

> "In the traditional formulation of attribute grammars (AGs) circularities are not allowed, that is, no attribute-instance in any derivation tree may be defined in terms of itself. Elsewhere in mathematics and computing, though, circular (or recursive) definitions are commonplace, and even essential. Given appropriate constraints, recursive definitions are well-founded, and the least fixed-points they denote are computable. This is also the case for circular AGs.
>
> This paper presents constraints on individual attributes and semantic functions of an AG that are sufficient to guarantee that a circular AG specifies a well-defined translation and that circularly-defined attribute-instances can be computed via successive approximation. AGs that satisfy these constraints are called finitely recursive.
>
> An attribute evaluation paradigm is presented that incorporates successive approximation to evaluate circular attribute-instances, along with an algorithm to automatically construct such an evaluator. The attribute evaluators so produced are static in the sense that the order of evaluation at each production-instance in the derivation-tree is determined at the time that each translator is generated.
>
> A final algorithm is presented that tells which individual attributes and functions must satisfy the constraints."

Verbatim quote - Magnusson/Hedin 2007 preprint, Section 2.2 "Evaluation of circular attribute grammars", describing Farrow's scheme:

> "Farrow [9] introduced a static evaluation technique based on the one by Katayama [18], but modified to compute the fixed point for attributes which potentially have circular dependencies. His scheme is also limited to traditional AGs without remote references since it depends on deriving the attribute dependencies statically from the productions of the grammar."

Verbatim quote - Magnusson/Hedin 2007 preprint, Section 3.2 "Comparison of algorithms", on what Farrow's final algorithm achieves:

> "Thus, we have a similar situation as in Farrow's static evaluator where potentially circular attributes are detected by analyzing the productions of the grammar."

Exact contribution:
1. Identifies the constraints - finite-height lattice / complete partial order on each cyclic attribute's domain, plus monotonicity / ascending chain condition on the semantic functions - under which a *circular* attribute grammar nonetheless denotes a well-defined translation. Names the resulting class "finitely recursive" AGs.
2. Gives an evaluation paradigm that computes circular attribute instances by successive approximation (Kleene iteration from bottom), and an algorithm to *automatically generate* such an evaluator.
3. The generated evaluators are STATIC: "the order of evaluation at each production-instance in the derivation-tree is determined at the time that each translator is generated". This is static multipass-style scheduling in the presence of cycles.
4. "A final algorithm is presented that tells which individual attributes and functions must satisfy the constraints." Per Magnusson/Hedin, this works by "analyzing the productions of the grammar" to detect *potentially circular* attributes.

What it does NOT do - and this is the crux:
- The final algorithm identifies WHICH attributes/functions carry the proof obligation. It does not itself DISCHARGE that obligation. It does not decide whether a given semantic function is monotonic, nor whether a given attribute domain has finite height. Those remain assumptions the grammar author must satisfy (Magnusson/Hedin make the same admission for their own evaluator, explicitly - see D3).
- Therefore Farrow 1986 is best described as a static identification of the cycles that NEED a convergence argument, together with a soundness theorem saying that if the argument holds the successive-approximation evaluator terminates. It is NOT a decision procedure that partitions cycles into "will converge" and "may not converge" by inspecting the specification.
- It is not a *diagnostic* tool. There is no notion of reporting a non-convergent cycle back to the author with a source-level explanation; a non-finitely-recursive AG is simply outside the accepted class.
- It has no notion of a value influencing HOW MUCH STRUCTURE the artefact contains. Attribute grammars are defined over a FIXED derivation tree. The tree is given by the parse; attribute values never change the tree. So the amplification phenomenon AuxFlow targets - a fact value determining how many pages/nodes exist, hence changing the graph itself - is structurally absent from Farrow's setting.
- No relation to document processing, TeX, or multi-run build scheduling.

Relevance to AuxFlow : maximal. This is the closest thing in the literature to "statically classify cycles in a dependency graph by whether iteration settles".

ANTICIPATION VERDICT : **PARTIAL OVERLAP, very heavy - concede most of the framework, keep only the amplification analysis.**

#### The blunt assessment (the single most important paragraph in this file)

Farrow 1986 anticipates, in 1986, essentially the whole *skeleton* of AuxFlow's cycle handling. Specifically, the following AuxFlow elements must not be claimed as novel:
(a) that a cyclic dependency graph over derived facts can still be well-defined and computable;
(b) that the way to compute it is monotone successive approximation from a bottom element;
(c) that the termination argument is finite-height lattice plus monotone functions;
(d) that a *static*, generation-time analysis can determine the evaluation order in the presence of cycles;
(e) that a static analysis can identify precisely which parts of the specification the convergence obligation falls on.
Point (e) is the dangerous one, because it is superficially the same shape as AuxFlow's "classify each SCC". A reviewer who knows this paper will read AuxFlow's SCC classifier as Farrow's final algorithm transplanted from attribute grammars to LaTeX aux files, and that reading is largely correct.

Where AuxFlow genuinely differs, and it is a narrow but real gap:
1. **Farrow's final algorithm allocates a proof obligation; AuxFlow's classifier attempts to discharge a decision.** Farrow says "these attributes must be monotone over a finite-height lattice - author, please ensure it". AuxFlow says "this SCC is BENIGN_CYCLIC / this one is AMPLIFYING", i.e. it tries to answer the question Farrow delegates. AuxFlow's taint analysis is a concrete, domain-specific sufficient condition for the finite-height half of Farrow's obligation: if no fact in the SCC can influence how much content is generated, the value domain (page numbers, counters, TOC entries over a document of fixed length) is bounded, hence finite height. That specialisation - identifying *content amplification* as the mechanism that destroys finite height in a document processor - is not in Farrow.
2. **Farrow's dependency graph is fixed; AuxFlow's is not.** In an AG the derivation tree is fixed before attribute evaluation, so the set of attribute instances and hence the graph is invariant across iterations. In LaTeX, a fact value can change the number of pages, which changes the number of `\pageref` instances, which changes the graph. This is a strictly harder setting: the fixpoint is over a space whose *dimension* is itself a function of the iterate. Farrow's theory does not cover it, and neither does Jones's or Magnusson/Hedin's. AuxFlow's amplifying/benign split is exactly a test for whether the document stays in the fixed-graph regime where the classical theory applies. **This is the defensible novelty claim, and it should be phrased that way: not "we classify cycles", but "we detect whether the classical fixed-graph fixpoint theory is applicable at all".**
3. **Farrow produces an evaluator; AuxFlow produces a diagnosis.** Source-level attribution of the offending facts and spans, and a CERTIFIED / BENIGN_CYCLIC / AMPLIFYING / UNKNOWN verdict aimed at a document author, is a different deliverable from a generated attribute evaluator. This is an engineering difference, not a theoretical one, and is worth little on its own.
4. **AuxFlow's edges carry pass lag; Farrow's do not.** Farrow iterates within a single translator run. AuxFlow's "written in run p, readable in run p+1" is a build-scheduling quantity. But see the established corrections: static pass-number assignment is Bochmann/Alblas prior art, so this difference buys nothing either.

Net: AuxFlow must be repositioned. The honest framing is "AuxFlow instantiates the Farrow/Jones circular-AG fixpoint framework for LaTeX auxiliary files, and extends it to the case where the dependency graph is not invariant under iteration because fact values can change how much content exists". Any framing that presents static benign-cycle classification itself as new is anticipated by Farrow 1986.

### D2. Jones 1990 - PRIORITY 2, SCC-plus-per-component-fixpoint is anticipated

Citation : Larry G. Jones, "Efficient evaluation of circular attribute grammars", ACM Transactions on Programming Languages and Systems 12(3):429-462, July 1990. Affiliation: Univ. of Illinois at Urbana-Champaign. 41 references.
DOI/URL  : https://doi.org/10.1145/78969.78971
Access   : metadata + complete verbatim abstract via CrossRef; full text paywalled at ACM DL. Detailed algorithm description obtained from Magnusson/Hedin 2007 Section 2.2.
Evidence label : SOURCED

Verbatim quote - complete abstract, CrossRef `abstract` field:

> "We present efficient algorithms for exhaustive and incremental evaluation of circular attributes under any conditions that guarantee finite convergence. The algorithms are derived from those for noncircular attribute grammars by partitioning the underlying attribute dependency graph into its strongly connected components and by ordering the evaluations to follow a topological sort of the resulting directed acyclic graph. The algorithms are efficient in the sense that their worst-case running time is proportional to the cost of computing the fixed points of only those strongly connected components containing affected attributes or attributes directly dependent on affected attributes. When the attribute grammar is noncircular or the specific dependency graph under consideration is acyclic, both algorithms reduce to the standard optimal algorithms for noncircular attribute evaluation."

Verbatim quote - Magnusson/Hedin 2007 preprint, Section 2.2, describing Jones:

> "Jones [15] proposes a dynamic evaluation algorithm derived from the underlying attribute dependency graph. Optimal dynamic evaluation for circular AGs is obtained by analyzing the dependency graph dynamically to identify its strongly connected components. A strongly connected component is a maximal set of vertices in which there is a path from any one vertex in the set to any other vertex in the set. All attribute instances belonging to the same strongly connected component are thus dependent of each other. Each strongly connected component is contracted into a single node to obtain a new graph C(G), which is acyclic and can be ordered topologically and evaluation can follow this order. A vertex in C(G) corresponding to more than one vertex in the original graph represents a set of attribute instances that are all dependent of each other and they will be evaluated in a single fixed-point evaluation."

Exact contribution : exhaustive and incremental evaluation of circular attributes by (i) SCC-decomposing the attribute dependency graph, (ii) contracting to the condensation C(G), (iii) topologically sorting the condensation, (iv) running one fixed-point computation per non-trivial SCC, (v) degenerating gracefully to the standard optimal non-circular algorithm when the graph is acyclic.

What it does NOT do :
- Jones does not classify cycles. The abstract is explicit: the algorithms work "under **any conditions that guarantee finite convergence**". Convergence is a HYPOTHESIS Jones assumes, supplied from outside. He solves the efficiency problem, not the decidability problem.
- Per Magnusson/Hedin, Jones's SCC identification is DYNAMIC ("analyzing the dependency graph dynamically"), i.e. per-tree at evaluation time, not a static grammar-level classification. AuxFlow's analysis is static over the document source. Farrow, not Jones, is the static one.
- No amplification analysis, no variable-size graph, no document/build setting.

Relevance to AuxFlow : direct architectural anticipation of "Tarjan SCC + monotone fixpoint over the condensation + topological order".

ANTICIPATION VERDICT : **FULL ANTICIPATION of the architecture; ORTHOGONAL to the classification question.**

Blunt consequence for AuxFlow: the sentence "AuxFlow finds SCCs with Tarjan and propagates a stable pass number by monotone fixpoint over the graph condensation" describes Jones 1990 with the words changed. **This must be conceded outright and cited, not presented as design.** It is standard technique. AuxFlow's contribution cannot live in the graph algorithm; it can only live in the semantic criterion used to label a component.

### D3. Magnusson and Hedin 2007 - PRIORITY 2, and the DOI correction

Citation : Eva Magnusson and Gorel Hedin, "Circular reference attributed grammars - their evaluation and applications", Science of Computer Programming 68(1):21-37, August 2007. Dept of Computer Science, Lund University.
DOI/URL  : https://doi.org/10.1016/j.scico.2005.06.005
Preprint : https://fileadmin.cs.lth.se/sde/publications/papers/2007-MagnussonEva-CRAGs-SCP-Preprint.pdf (preprint header reads "Preprint submitted to Elsevier Preprint 4 August 2004"; 26 references in the published version)
Access   : full text of the preprint read; published-version metadata via CrossRef.
Evidence label : SOURCED

#### DOI CORRECTION - resolved explicitly, as required

The AuxFlow repository's recorded DOI **10.1016/j.scico.2005.06.005 is CORRECT**. The previous attempt's value 10.1016/j.scico.2007.01.005 is **WRONG** and must not be propagated. Evidence, both from CrossRef:

- `10.1016/j.scico.2005.06.005` -> title "Circular reference attributed grammars — their evaluation and applications", authors Eva Magnusson, Gorel Hedin, Science of Computer Programming, volume 68, issue 1, pages 21-37, published-print 2007-08. Cited-by 45. Its reference list contains Farrow 10.1145/13310.13320, Jones 10.1145/78969.78971, Knuth 10.1007/BF01692511, JastAdd 10.1016/S0167-6423(02)00109-0 - exactly the expected bibliography.
- `10.1016/j.scico.2007.01.005` -> title "ScriptEase: A generative/adaptive programming paradigm for game scripting", authors Cutumisu, Onuczko, McNaughton, Roy, Schaeffer, Schumacher, Siegel, Szafron, Waugh, Carbonaro, Duff, Gillis; Science of Computer Programming, volume 67, issue 1, pages 32-58, published-print 2007-06. Entirely unrelated to attribute grammars.

Note the volume/issue distinction that makes the confusion easy: the correct paper is SCP **68**(1), the decoy is SCP **67**(1). Note also that the published year is 2007 while the DOI suffix says 2005 (the submission year), which is presumably what prompted the previous attempt to "correct" a DOI that was already right.

#### Substance - the convergence condition, stated precisely

Verbatim quote, Section 1 "Introduction":

> "The traditional AG requirement of non circularity is a sufficient but not necessary condition to guarantee that an AG is well defined in the sense that all semantic rules can be satisfied. It suffices that all attributes involved in cyclic dependencies have a fixed point that can be computed with a finite number of iterations. In CAGs, circular dependencies between attributes are allowed provided that such a fixed point is available for all possible trees. This is guaranteed if the values for each attribute on a cycle can be organized in a lattice of finite height and if all the semantic functions involved in computing these attributes are monotonic on the respective lattices."

Verbatim quote, Section 2.2 "Evaluation of circular attribute grammars", with its footnote 3:

> "One way to formulate the constraints is to require that the domain of all attributes involved in cyclic chains can be arranged in a lattice of finite height and that all semantic functions for these attributes are monotonic. [footnote 3] The evaluation of circularly defined attributes can be regarded as a special case of solving the equation X = f(X) for the value of X. By giving X the bottom of the lattice as start value the iterative process Xi+1 = f(Xi) will converge to a least fixed point for which all involved semantic rules are satisfied."

> "[footnote 3] More precisely it is sufficient that the domain of the attributes forms a complete partial order and that the semantic functions satisfy the ascending chain condition."

**PRECISE TERMINATION CONDITION** (answers the assignment's question): fixpoint evaluation is guaranteed to terminate iff, for every attribute on a cycle, (i) the value domain forms a lattice of finite height - more precisely a complete partial order - and (ii) every semantic function computing such an attribute is monotonic, more precisely satisfies the ascending chain condition. Iteration starts at bottom and ascends. Additionally, Section 2.2 records a useful refinement under the heading "Non-monotonic intercomponent dependencies":

> "If two strongly connected components are evaluated in topological order, the dependency between the components does not need to be monotonic. The inner component will then have received its final value before it is used by the outer component, and the monotonicity of the intercomponent dependency is therefore not important."

That refinement matters to AuxFlow: monotonicity is only required WITHIN an SCC, not on edges between SCCs. AuxFlow should adopt it rather than requiring global monotonicity.

Verbatim quote, Section 3.2 "Comparison of algorithms", on the relation to Farrow (the quote the previous attempt flagged - VERIFIED, wording exact):

> "All potentially circular attributes are required to be declared circular. (In Section 3.4 we will discuss how to detect and handle failures of this requirement.) Thus, we have a similar situation as in Farrow's static evaluator where potentially circular attributes are detected by analyzing the productions of the grammar."

Also captured from Section 2.1 "Detection of circularity", high value for AuxFlow's decidability discussion:

> "In [19] Knuth developed a polynomial algorithm for circularity testing. The algorithm is conservative, i.e., circularity is always detected but some noncircular AGs may be reported to be circular. Later [20] Knuth constructed an exact algorithm which is exponential in time and space complexity. Rodeh & Sagiv [25] extended these algorithms to deal with the problem of finding circular attributes. They developed a polynomial approximation algorithm, i.e., all circular attributes are discovered but some noncircular attributes may be reported to be circular. They also constructed an exact algorithm with exponential time complexity and showed that finding the circular attributes is a harder problem than testing for circularity."

> "In [5] he shows that testing remote attribute grammars for circularity is undecidable and examines techniques for approximation."

(The `[5]` is Boyland, "Remote Attribute Grammars", manuscript 2003; `[2]` is Boyland's APS PhD thesis, Berkeley 1996. The undecidability result is for REMOTE attribute grammars - the ones with reference attributes, i.e. the ones structurally analogous to `\ref`/`\pageref` pointing at an arbitrarily distant place in the document. This is important for AuxFlow and is discussed in Part 3 below.)

Exact contribution : combines Reference AGs with Circular AGs into CRAGs; gives a demand-driven (not static) fixpoint evaluator with an `IN_CIRCLE`/`CHANGE` global-flag scheme; implemented in JastAdd; evaluated on grammars up to Java 1.2; applies CRAGs to nullable/first/follow set computation.

What it does NOT do :
- Its evaluator is DEMAND-DRIVEN and dynamic, not a static classifier. Circularity is discovered at evaluation time via a `visited` flag.
- It does not verify its own convergence preconditions (see Section 3.4 check below).
- No amplification analysis; the AST is fixed, as in all AG work.

Relevance to AuxFlow : establishes the exact convergence condition AuxFlow's "benign" label is trying to approximate, and confirms that even the state of the art in circular AGs punts on checking that condition.

#### The decisive admission - Section 3.5 "Comparison to related work"

The previous attempt reported that the paper admits its evaluator does not check the convergence preconditions. VERIFIED, and the location is **Section 3.5**, not 3.4 (Section 3.4, "Robust improved algorithm", is about detecting a *missing* `circular` declaration via SCC-membership tracking - a different check). Exact wording:

> "Our evaluator presently does not check whether circularly defined attributes take their values from a lattice of finite height or if their defining semantic functions are monotonic. Thus there is no guarantee that iterations will converge. Our approach is in this respect similar to that of, e.g., Farrow [9] and means that we rely on the AG author to ensure that the semantic functions involved are properly constrained."

**This single sentence is the most useful thing in area D for AuxFlow, and it cuts in AuxFlow's favour.** Magnusson and Hedin, writing in 2007 with Farrow's paper in hand and citing it, state that Farrow's approach *also* does not check the finite-height and monotonicity conditions, and that both rely on the author. That is independent, peer-reviewed confirmation of the reading of Farrow's abstract given in D1: Farrow's final algorithm allocates the proof obligation, it does not discharge it. **No paper in the circular-AG line performs a static classification of cycles into convergent and non-convergent.** They assume convergence, or they identify who must guarantee it. AuxFlow's benign/amplifying decision is therefore not anticipated as a *decision procedure* - only its framework, vocabulary, and graph machinery are.

Two further quotes from Section 3.5 that AuxFlow must confront, because they are adverse:

> "For ordinary attribute grammars, the dependency graph can be computed from the grammar and constructed before evaluation. The static attribute evaluation algorithms available for ordinary attribute grammars, like OAGs [17], rely on this property in order to compute approximations of the dependency graph before evaluation. The same holds for the static evaluation algorithms for circular attribute grammars, like Farrow's algorithm [9]."

> "Jones algorithm computes the strongly connected components for a given AST before evaluation, based on the actual attribute dependencies. For CRAGs, such pre-evaluation computations are not possible in general, since the reference attributes give rise to attribute dependencies that are not known until after the evaluation of those reference attributes. For this reason, the strongly connected components in CRAGs cannot, in general, be computed before evaluation."

INFERENCE, and important: LaTeX's `\ref` / `\pageref` / `\cite` are *reference attributes* in exactly Magnusson and Hedin's sense - a fact defined by reaching into an arbitrarily distant part of the document. AuxFlow proposes to build a **static instance-level** dependency graph over such facts. The literature says that for reference/remote AGs this is not possible in general, and Boyland's result (quoted in Section 2.1 above) is that circularity testing for remote AGs is outright **undecidable**. Consequences AuxFlow must accept:
- AuxFlow's static graph is necessarily an **approximation**, in Knuth's and Rodeh-Sagiv's sense: it may report cycles that do not occur in the actual run. The `UNKNOWN` verdict is not an escape hatch for engineering convenience, it is theoretically forced.
- The declared-subset restriction on LaTeX is doing all the load-bearing work: it is what makes the reference targets statically resolvable. The paper must state the subset restriction as the enabling condition and must not present static graph construction as generally achievable.
- Sasaki and Sassa's constraint, as Magnusson and Hedin describe it - "they also make the additional assumption that cycles do not appear without remote references, a constraint that facilitates the check for convergence" - is a precedent for exactly this style of restriction-to-make-it-decidable move. AuxFlow's declared subset is the same manoeuvre and should be presented as such.


ANTICIPATION VERDICT : **PARTIAL OVERLAP** - anticipates the convergence criterion and the Farrow-style "detect potentially circular attributes statically" idea, but not a benign/amplifying decision procedure.

## Negative results

### ACM Digital Library full text - Farrow 1986
query    : `read https://dl.acm.org/doi/10.1145/13310.13320` and `read https://dl.acm.org/doi/pdf/10.1145/13310.13320`
outcome  : PAYWALLED / bot-blocked. ACM DL serves an interstitial to non-institutional clients. Abstract obtained instead via CrossRef, which carries the full four-paragraph structured abstract, so the loss is limited to the body text (constraint formalism details, the exact statement of the final algorithm).
status   : SOURCED (that it is inaccessible)

### ACM Digital Library full text - Jones 1990
query    : `read https://dl.acm.org/doi/10.1145/78969.78971`
outcome  : PAYWALLED. Full abstract obtained via CrossRef; algorithm described in detail by Magnusson/Hedin Section 2.2, which is sufficient to establish the SCC-condensation architecture beyond doubt.
status   : SOURCED (that it is inaccessible)

## Outstanding searches

- Full text of Farrow 1986 and Jones 1990 (both paywalled at ACM DL; abstracts obtained via CrossRef).
- Frank Mittelbach's "impossible document" answer: located in an earlier attempt but not re-verified here.
- Analogous domains (spreadsheet circular references, CSS cyclic percentage sizing, ResizeObserver
  depth-monotonicity loop limit, constraint-layout solvability): NOT ATTEMPTED in this pass.


---

## Part 3 - the mechanisms of LaTeX non-convergence, and whether AuxFlow would catch them

Written by the audit lead from primary sources read directly (Gaspar's TUGboat letter,
tex.stackexchange.com/questions/30674, the `labelschanged` documentation taxonomy, the `latexmk`
manual, and the TeX FAQ entry recorded in `area-b-latex-compilation.md`). AuxFlow's taint-seed rule
under test is the one specified in `docs/STATIC-ANALYSIS.md`:

> seeds <- { f : the value of f is read inside the condition or bound of a ControlConstruct, or an
> argument of `\setcounter` whose counter bounds such a construct, or a construct that directly
> emits page material (`\newpage`, `\clearpage`) under the control of such a construct }

### Mechanism table

| # | Mechanism | Behaviour | Example, verified | Would AuxFlow's seeds catch it? |
|---|---|---|---|---|
| M1 | A loop whose bound is a page reference to a label inside the material the loop generates | **Monotone divergence** - the recorded page value increases by exactly one per run, without bound | Gaspar, TUGboat 35:1, p. 16: `\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}` with `\label{l}` after the loop | **YES.** The value is read in the loop bound and the body emits `\newpage`. This is the seed rule's motivating case, and corpus member `b08`. |
| M2 | A conditional selecting between differently sized content, on a page reference | **Period-2 oscillation** | tex.SE 30674, Roelof Spijker: `\ifthenelse{\equal{#1}{1}}{\Huge A}{\small A}` applied to `\pageref{test}` | **YES, but only by over-approximation.** The value is read in a conditional, so it is seeded; the pseudocode then adds a STRUCTURAL edge for every tainted fact regardless of whether the branches differ in *quantity*. Note that no content is generated or removed here - only its size changes - so the criterion catches it for the wrong reason. |
| M3 | The *typeset width* of a resolved reference changes a line break, hence a page break, hence the reference | **Period-2 oscillation**, no conditional and no loop anywhere | tex.SE 30674, accepted answer (`user202729`): `\lipsum[1-48]` plus `\textcolor{red}{\pageref{a}}`, cycle length 2. Also David Carlisle's `cfr-lm` proportional-figures example, and the TeX FAQ's roman-numeral case (`ix` -> `x`) recorded in area B | **NO.** Nothing is read in a condition or bound; no page-emitting construct is under control of anything. This is a **false negative**. |
| M4 | A `[!t]` float plus roman page numbering: float placement and page numbering are mutually unstable | **Period-2 oscillation**, no conditional and no loop | tex.SE 30674, David Carlisle's first example: `\framebox(200,430){}` in `figure[!t]` with `\pagenumbering{Roman}` | **NO.** Float placement is not modelled at all, and no fact value is read in a control construct. **False negative.** |
| M5 | A citation style that selects a shorter form when the previous citation is on the same page | **Period-2 oscillation** | tex.SE 30674 (`mach`), with Paul Stanley's four-step explanation, and tex.SE 81695: `biblatex-icomp` `ibid` across a page break | **ONLY BY REFUSAL.** The feedback lives inside package macros. Under assumption A3 an unmodelled package yields an `OPAQUE` fact and `UNKNOWN`, which is safe. But if `biblatex` were modelled naively as producing `CITE_USE` and `BBL` facts without the same-page feedback edge, this becomes a **false negative**. A3 is doing real work here and must not be weakened. |
| M6 | Packages generating dynamic *textual* references whose length moves the floats they refer to | Oscillation | `labelschanged` documentation, verbatim: "Some packages, such as `varioref`, generate text references which dynamically change depending on the location of each float, and these changing messages may then cause the floats themselves to move." | **NO.** Same class as M3. **False negative** unless `varioref` is modelled with an explicit extent-feedback edge. |
| M7 | References inside margin notes or footnotes | Oscillation | `labelschanged` documentation, verbatim: "References in margin or foot notes may have a similar effect." | **NO.** Same class as M3. |
| M8 | A generated auxiliary file that is not deterministic - e.g. an `.eps` carrying its own creation timestamp | Unbounded rerun loop with no cross-reference cause at all | `latexmk` manual, verbatim: "The file contains a comment line giving its creation date and time. On the next run the time changes, latex sees that the eps file has changed, and therefore reruns latex. This causes an infinite loop" | **NO, and out of model.** Not a cross-reference phenomenon. This is why `SOURCE_DATE_EPOCH` / `FORCE_SOURCE_DATE` are correctness controls in `docs/EVALUATION.md` rather than hygiene. |
| M9 | Active characters in captions or section names defeating the kernel's own change test | **Not real non-convergence** - a false positive of LaTeX's `\@testdef` comparison | `labelschanged` documentation, verbatim: "Due to the way changing labels are detected, problems may also be caused by active characters in captions or section names." | N/A, but important: the *engine's* oracle has false positives as well as false negatives. Any evaluation using the engine warning as baseline B must expect both error directions. |

### Is a static dependency cycle necessary, sufficient, or neither?

**Neither. This is the sharpest technical finding in the whole audit.**

*Not sufficient.* Established and uncontroversial: ordinary documents are cyclic and converge. The
best primary-source statement is the `latexmk` manual (SOURCED, quoted in
`area-c-latex-tools.md`): "This situation, of circular dependencies, is endemic to latex, and is one
of the issues that latexmk is programmed to overcome." latexrun independently draws the cyclic
graph of `latex` and `bibtex` with `.aux`, `.toc` and `.bbl` feedback edges and states that its goal
is to find its fixed point. So a cycle is the normal case, not the pathological one.

*Not necessary - and this is the part AuxFlow's design does not currently admit.* Mechanisms M3, M4,
M6 and M7 are genuinely non-convergent and produce **no cycle in the ARG as specified**. The reason
is structural, not incidental: `docs/IR.md` splits every list-producing fact into an `exists`
component and a `value` component precisely so that `CONTENT_VOLUME` depends only on `exists`. That
split is what makes the analysis non-vacuous. But M3/M4/M6/M7 are cycles *through* `.value*: a
resolved value is typeset, its typeset extent changes pagination, pagination changes the value. The
`exists`/`value` split severs exactly that edge by fiat. It is assumption A2 ("resolving a reference
does not alter pagination"), and A2 is false for a published, reproducible class of documents.

Consequence for the hypotheses, stated bluntly:

- **H1 as written is falsified in advance.** "Structural analysis of the auxiliary-fact graph
  distinguishes potentially non-convergent documents from benignly cyclic ones with zero false
  negatives on the benchmark corpus" can only hold if the corpus excludes M3/M4/M6/M7. If the
  corpus contains any of them - and it should, because they are the published counterexamples that
  do *not* require an artificial `\forloop` - AuxFlow will produce a false negative by construction.
  H1 must be restated as being over the *modelled* mechanism classes, with the unmodelled classes
  named.
- **The dichotomy must be stated in the paper, not buried.** Either (a) `CONTENT_VOLUME` depends on
  every `.value` that is rendered into the body, in which case every document with one `\ref` is a
  single SCC and the analysis is vacuous; or (b) it does not, in which case the analysis is unsound
  for the extent-driven class. There is no third option available to a static analysis that does not
  model line breaking. AuxFlow takes (b). That is defensible only if the excluded class is named
  explicitly, given a corpus member, and reported as a measured false negative rather than
  discovered by a reviewer.

### What additional semantics are required to separate benign from non-convergent?

Three things, in increasing order of difficulty.

1. **A notion of the typeset extent of a resolved value, not just its identity.** Distinguishing
   "the value changed from `??` to `17`" from "the value changed from `ix` to `x`" requires knowing
   that the second changes a box width by a different amount than the first. This is the minimum
   needed for M3/M4/M6/M7 and it requires font metrics. It is out of scope for AuxFlow and should be
   declared out of scope, not silently assumed away.
2. **A bound on the value domain.** This is Farrow's and Magnusson/Hedin's finite-height-lattice
   condition (D1, D3), specialised. For a document of fixed extent, page numbers, counters and list
   entries range over a bounded set, so the lattice has finite height and Kleene iteration
   terminates. Amplification is precisely the mechanism that makes the domain unbounded, because the
   page count becomes a function of the iterate. AuxFlow's taint analysis should be presented in
   exactly these terms: **it is a domain-specific sufficient condition for the finite-height half of
   the classical circular-attribute-grammar convergence obligation.**
3. **Monotonicity of the feedback function.** Required only *within* an SCC, not on edges between
   SCCs - Magnusson and Hedin, verbatim (D3): "If two strongly connected components are evaluated in
   topological order, the dependency between the components does not need to be monotonic." AuxFlow
   should adopt this refinement. Note that M2/M3/M4 are non-monotone (they alternate), whereas M1 is
   monotone-but-unbounded. **Divergence and oscillation are therefore different failure modes with
   different causes**: M1 violates finite height, M2-M4 violate monotonicity. A single `AMPLIFYING`
   label conflates them. Splitting the class would be a genuine, small, defensible refinement.

### What can a static analyser over the declared subset safely claim?

- That an ARG cycle containing a STRUCTURAL edge exists, and which facts and edges constitute it.
  Tarjan is exact on the constructed graph (unchanged).
- That the finite-height precondition of the classical circular-fixpoint theory *may* fail, because
  a value reaches a construct governing content quantity. This is a necessary structural condition
  for the M1 class only.
- That the document is outside the analysable subset, hence `UNKNOWN`.
- **Not** that the absence of a STRUCTURAL cycle implies convergence. M3/M4/M6/M7 are the
  counterexamples and they are published.


## Summary for the audit

- **Farrow 1986 (DOI 10.1145/13310.13320) is the most dangerous single item in this area.** It
  already gives: cyclic dependency graphs over derived facts that are nonetheless well defined;
  monotone successive approximation from a bottom element as the way to compute them; the
  finite-height-lattice-plus-monotonicity termination condition; a *static* generation-time analysis
  that fixes evaluation order in the presence of cycles; and a final algorithm that identifies which
  attributes carry the convergence obligation. A reviewer who knows this paper will read AuxFlow's
  SCC classifier as Farrow's final algorithm transplanted to LaTeX, and that reading is largely
  correct.
- **But Farrow allocates the obligation; he does not discharge it.** Magnusson and Hedin 2007
  Section 3.5 confirm this in writing: "Our evaluator presently does not check whether circularly
  defined attributes take their values from a lattice of finite height or if their defining semantic
  functions are monotonic. Thus there is no guarantee that iterations will converge. Our approach is
  in this respect similar to that of, e.g., Farrow." **No paper in the circular-attribute-grammar
  line performs a static decision procedure separating convergent from potentially non-convergent
  cycles.** That is the surviving gap, and it is narrow.
- **Jones 1990 (DOI 10.1145/78969.78971) fully anticipates AuxFlow's architecture.** Abstract,
  verbatim: the algorithms are "derived from those for noncircular attribute grammars by
  partitioning the underlying attribute dependency graph into its strongly connected components and
  by ordering the evaluations to follow a topological sort of the resulting directed acyclic graph",
  degenerating to the standard optimal algorithm when acyclic. "Tarjan SCC plus monotone fixpoint
  over the condensation in topological order" must be cited, not designed.
- **Jones assumes convergence rather than deciding it** - "under any conditions that guarantee
  finite convergence" - and, per Magnusson and Hedin, his SCC identification is *dynamic*, per-tree.
  Farrow is the static one.
- **DOI correction, resolved.** The repository's recorded `10.1016/j.scico.2005.06.005` for
  Magnusson and Hedin is CORRECT (SCP 68(1):21-37, 2007). The value `10.1016/j.scico.2007.01.005`
  is a different paper entirely (ScriptEase, SCP 67(1)) and must not be propagated.
- **The exact convergence condition AuxFlow's benign label approximates is stated verbatim** by
  Magnusson and Hedin: a fixpoint is guaranteed "if the values for each attribute on a cycle can be
  organized in a lattice of finite height and if all the semantic functions involved in computing
  these attributes are monotonic on the respective lattices", refined in their footnote to a
  complete partial order plus the ascending chain condition. AuxFlow should state its taint analysis
  as a domain-specific sufficient condition for the finite-height half.
- **Monotonicity is required only within an SCC**, not across the condensation's edges (Magnusson
  and Hedin, "Non-monotonic intercomponent dependencies"). AuxFlow should adopt this.
- **AuxFlow lives in a provably undecidable setting and should say so.** LaTeX's `\ref` / `\pageref`
  / `\cite` are *remote reference* attributes; Boyland showed circularity testing for remote
  attribute grammars is undecidable, and Magnusson and Hedin state that for reference attribute
  grammars "the strongly connected components ... cannot, in general, be computed before
  evaluation". The `UNKNOWN` verdict and the declared subset are therefore theoretically forced, not
  engineering convenience. Sasaki and Sassa's restriction ("cycles do not appear without remote
  references, a constraint that facilitates the check for convergence") is a precedent for exactly
  the same manoeuvre and should be cited as such.
- **The genuine difference from all of this work: in an attribute grammar the derivation tree is
  fixed before evaluation, so the graph is invariant across iterations. In LaTeX it is not.** A fact
  value can change the page count, which changes the number of `\pageref` instances, which changes
  the graph. The fixpoint is over a space whose dimension is a function of the iterate. Farrow,
  Jones and Magnusson/Hedin do not cover this. AuxFlow's amplifying/benign split is best framed not
  as "we classify cycles" - which is Farrow - but as **"we detect whether the classical fixed-graph
  fixpoint theory applies at all"**. That is the defensible sentence.
- **The mechanism survey (Part 3) produces a harder result than expected: an ARG cycle is neither
  necessary nor sufficient for non-convergence.** Not sufficient is known. Not necessary is new to
  the project and adverse: four published counterexample classes (reference width changing a line
  break; `[!t]` floats with roman numerals; `varioref`-style dynamic textual references; references
  in margin or foot notes) are non-convergent and produce no STRUCTURAL edge, because AuxFlow's
  `exists`/`value` split severs the extent-feedback edge by fiat. That split is assumption A2, and
  A2 is false for a reproducible, published class.
- **Consequence: H1's "zero false negatives" form is falsified in advance** unless the corpus is
  restricted to the modelled mechanisms. The paper must state the dichotomy - model extent feedback
  and be vacuous, or do not and be unsound for a named class - and choose openly.
- **Divergence and oscillation are distinct failure modes and AuxFlow conflates them.** Gaspar's
  `\forloop` case diverges monotonically (finite height fails); the width-driven and conditional
  cases oscillate with period 2 (monotonicity fails). Splitting `AMPLIFYING` along that line is a
  small, honest refinement that follows directly from the Magnusson/Hedin condition.
