# Static vs dynamic bounding of fixpoint iteration and data-dependent rates

Search area F: compiler and systems literature on statically bounding fixpoint iteration, and on static schedulability when rates are data-dependent. Audit date 2026-08-27.

Purpose: determine whether AuxFlow's central mechanisms (stable-pass numbering by monotone fixpoint over a dependency-graph condensation; the benign-cyclic vs amplifying distinction) are re-derivations of known results in another domain.

## Search log

### CrossRef REST API
query    : `read https://api.crossref.org/works/10.1145/321921.321938`
examined : 1 record
outcome  : Kam & Ullman, "Global Data Flow Analysis and Iterative Algorithms", J. ACM 23(1):158-171, 1976. Full JATS abstract retrieved. The abstract itself frames the Hecht-Ullman iteration bound as pre-existing prior art.
status   : SOURCED

### CrossRef REST API
query    : `read https://api.crossref.org/works/10.1007/BF00290339`
examined : 1 record
outcome  : Kam & Ullman, "Monotone data flow analysis frameworks", Acta Informatica 7(3):305-317, 1977. Metadata + reference list retrieved. NO abstract deposited in CrossRef for this record. Reference list identified the correct source of the iteration bound as Hecht & Ullman, SIAM J. Comput. 4:519-532 (1975), not the SIAM 1972 reducibility paper.
status   : SOURCED (metadata only; no abstract available)

### CrossRef REST API
query    : `read https://api.crossref.org/works/10.1145/512927.512946`
examined : 1 record
outcome  : Hecht & Ullman, POPL '73, pp. 207-217. CrossRef title string is "Analysis of a simple algorithm global data flow problems" (CrossRef has dropped the word "for"). No abstract deposited.
status   : SOURCED (metadata only)

### CrossRef REST API
query    : `read https://api.crossref.org/works/10.1137/0201014`
examined : 1 record
outcome  : Hecht & Ullman, "Flow Graph Reducibility", SIAM J. Comput. 1(2):188-202, 1972. Full abstract retrieved. This paper is about characterising reducibility via two graph transformations - it is NOT the source of the iteration-count bound. Recorded to prevent miscitation.
status   : SOURCED

### CrossRef REST API
query    : `read https://api.crossref.org/works/10.1137/0204044`
examined : 1 record
outcome  : Hecht & Ullman, "A Simple Algorithm for Global Data Flow Analysis Problems", SIAM J. Comput. 4(4):519-532, 1975. Full abstract retrieved, containing the exact definition of the loop-connectedness parameter d. THIS is the journal version of the POPL '73 paper and the primary source for the parameter.
status   : SOURCED

### Ullman's own Dragon Book lecture notes (Stanford InfoLab)
query    : `read http://infolab.stanford.edu/~ullman/dragon/w06/lectures/dfa3.pdf`
examined : full slide deck (336 lines of extracted text)
outcome  : Explicit statement and proof sketch of the depth+2 bound, by one of the two authors of the original result. Quoted below.
status   : SOURCED

### Web search (for the exact bound statement and its variants)
query    : `"loop connectedness" iterative data flow analysis "d + 2" passes reducible reverse postorder bound`
examined : 19 sources returned; 3 followed
outcome  : Both the d+2 and d+3 forms are in circulation. d+2 is the round-robin bound for rapid frameworks with reverse-postorder node visiting (d+1 propagation passes, +1 to detect stability); d+3 is the form attributed to Kam & Ullman in secondary restatements. Confirmed the definition d(G) = max number of retreating/back edges on any acyclic path.
status   : REPORTED for the d+3 attribution; SOURCED for d+2 via Ullman's notes

### bears.ece.ucsb.edu course paper mirror
query    : `read https://bears.ece.ucsb.edu/class/ece253/papers/lee_sdf87.pdf`
examined : full 12-page paper (1044 lines of extracted text)
outcome  : Full text of Lee & Messerschmitt, IEEE Trans. Computers C-36(1):24-35, 1987. All four theorems, the topology matrix, the balance/nullspace condition, and Section V "Limitations of the Model" recovered. Quoted below.
status   : SOURCED

### ptolemy.berkeley.edu
query    : `read https://ptolemy.berkeley.edu/publications/papers/87/synchronousDataflow/` and `.../93/jbuckThesis/`
examined : 0 (both timed out)
outcome  : NOTHING RETRIEVED - host unreachable from this environment. Worked around via the UCSB mirror for the SDF paper; see Outstanding searches for the thesis.
status   : failed fetch, not a negative result

### Web search (BDF undecidability)
query    : `Buck Lee Boolean dataflow "undecidable" bounded memory scheduling token flow model`
examined : see below
outcome  : see Verified sources F7/F8.
status   : SOURCED / REPORTED as marked

## Verified sources

### F1. Kam & Ullman, "Global Data Flow Analysis and Iterative Algorithms" (J. ACM 1976)

Citation: John B. Kam and Jeffrey D. Ullman, "Global Data Flow Analysis and Iterative Algorithms", Journal of the ACM, vol. 23, no. 1, pp. 158-171, January 1976.
DOI/URL: https://doi.org/10.1145/321921.321938 (metadata + full JATS abstract via https://api.crossref.org/works/10.1145/321921.321938)
Access: metadata and full abstract (CrossRef); full text paywalled at ACM DL.
Verbatim quote (abstract): "Kildall has developed data propagation algorithms for code optimization in a general lattice theoretic framework. In another direction, Hecht and Ullman gave a strong upper bound on the number of iterations required for propagation algorithms when the data is represented by bit vectors and depth-first ordering of the flow graph is used. The present paper combines the ideas of these two papers by considering conditions under which the bound of Hecht and Ullman applies to the depth-first version of Kildall's general data propagation algorithm. It is shown that the following condition is necessary and sufficient: [...] Then (*) (for all f,g,x) [fg(0) >= g(0) ^ f(x) ^ x]. Then it is shown that several of the particular instances of the techniques Kildall found useful do not meet condition (*)."
Exact contribution: gives the necessary and sufficient condition on the transfer-function space under which the Hecht-Ullman iteration-count bound carries over from bit-vector frameworks to Kildall's general lattice framework. Condition (*) is the property later named *rapidity*. Also shows that several useful analyses are NOT rapid, i.e. the structural bound does not always apply.
What it does NOT do: nothing about typesetting, document build passes, or whether propagated values change how much work exists.
Relevance to AuxFlow: this is the canonical statement of AuxFlow's stable-pass-number problem in the abstract - "how many rounds of propagation over a dependency graph before the fixpoint is reached, derived from the structure of the graph, plus the exact algebraic precondition for the structural answer to be valid".
Anticipation verdict: PARTIAL OVERLAP (strong). Anticipates the idea, the technique, and the caveat. Does not anticipate the LaTeX instantiation or the amplification analysis.
Evidence label: SOURCED (metadata + abstract).

### F2. Hecht & Ullman, "A Simple Algorithm for Global Data Flow Analysis Problems" (SIAM J. Comput. 1975)

Citation: Matthew S. Hecht and Jeffrey D. Ullman, "A Simple Algorithm for Global Data Flow Analysis Problems", SIAM Journal on Computing, vol. 4, no. 4, pp. 519-532, December 1975.
DOI/URL: https://doi.org/10.1137/0204044 (metadata + full abstract via https://api.crossref.org/works/10.1137/0204044)
Access: metadata and full abstract (CrossRef); full text paywalled at SIAM.
Verbatim quote (abstract): "A simple, iterative bit propagation algorithm for solving global data flow analysis problems such as 'available expressions' and 'live variables' is presented and shown to be quite comparable in speed to the corresponding interval analysis algorithm. This comparison is facilitated by a result relating two parameters of a reducible flow graph (rfg). Namely, if G is an rfg, d is the largest number of back edges found in any cycle-free path in G, and k is the length of the interval derived sequence of G, then k >= d. (Intuitively, k is the maximum nesting depth of loops in a computer program, while d is a measure of the maximum loop-interconnectedness.) The node ordering employed by the simple algorithm is the reverse of the order in which a node is last visited while growing any depth-first spanning tree of the flow graph."
Exact contribution: defines the loop-connectedness parameter d ("the largest number of back edges found in any cycle-free path in G"), relates it to interval-derived-sequence depth k, and establishes that a reverse-depth-first-order round-robin bit-propagation algorithm is competitive with interval analysis because its pass count is governed by d.
Exact precondition, from the quote: G must be a REDUCIBLE flow graph; the node ordering must be reverse of depth-first-spanning-tree last-visit order (i.e. reverse postorder); and the framework must be a bit-vector (distributive, and in the later terminology rapid) framework.
What it does NOT do: does not address non-reducible graphs (where no such d is well-defined), does not address frameworks that fail rapidity (F1 shows several do), and says nothing about work amplification.
Relevance to AuxFlow: this is the primary source of the parameter that plays exactly the role of AuxFlow's per-fact "stable pass number" upper bound.
Anticipation verdict: PARTIAL OVERLAP (strong) - anticipates "bound the number of propagation rounds by a structural depth parameter of the dependency graph".
Evidence label: SOURCED (metadata + abstract).

Note on the POPL version: the conference version is Matthew S. Hecht and Jeffrey D. Ullman, POPL '73, pp. 207-217, https://doi.org/10.1145/512927.512946 . CrossRef records the title as "Analysis of a simple algorithm global data flow problems" (the word "for" is missing in the CrossRef string; the paper is commonly cited as "Analysis of a simple algorithm for global data flow problems"). No abstract is deposited, so I could not quote it. Evidence label: SOURCED for metadata; the CrossRef title string is verbatim as retrieved.

Note on a NEAR-MISS that must not be miscited: Hecht & Ullman, "Flow Graph Reducibility", SIAM J. Comput. 1(2):188-202, 1972, https://doi.org/10.1137/0201014 . Abstract (verbatim): "The structure of programs can often be described by a technique called 'interval analysis' on their flow graphs. Here, we characterize the set of flow graphs that can be analyzed in this way in terms of two very simple transformations on graphs. We then give a necessary and sufficient condition for analyzability and apply it to 'goto-less programs,' showing that they all meet the criterion." This paper supplies the REDUCIBILITY precondition but NOT the iteration bound. Evidence label: SOURCED.

### F3. Kam & Ullman, "Monotone data flow analysis frameworks" (Acta Informatica 1977)

Citation: John B. Kam and Jeffrey D. Ullman, "Monotone data flow analysis frameworks", Acta Informatica, vol. 7, no. 3, pp. 305-317, 1977.
DOI/URL: https://doi.org/10.1007/BF00290339 (metadata via https://api.crossref.org/works/10.1007/BF00290339)
Access: metadata and full reference list only. NO abstract is deposited in CrossRef for this record; full text paywalled at Springer. I did not obtain the text, so I make no quoted claim about its contents.
Verbatim quote: none available - CrossRef deposits no abstract for this record.
Exact contribution (REPORTED, standard in the literature and consistent with its citation pattern - 241 citations recorded): generalises Kildall's distributive lattice framework to merely MONOTONE frameworks, shows the iterative algorithm still converges to the maximum fixed point (MFP) rather than the meet-over-all-paths (MOP) solution, and shows MOP is in general undecidable for monotone frameworks.
What it does NOT do: not verified here.
Relevance to AuxFlow: the monotone-framework result is precisely the setting AuxFlow's "monotone fixpoint over the graph condensation" lives in. The MFP-vs-MOP gap is the reason a static analysis of this shape is necessarily conservative - which is the same reason AuxFlow needs an UNKNOWN class.
Anticipation verdict: INFORMS ONLY as verified here; likely PARTIAL OVERLAP if the full text is read.
Evidence label: metadata SOURCED; contribution REPORTED / UNVERIFIED.

### F4. Ullman's own restatement of the bound (Dragon Book lecture notes, Stanford)

Citation: Jeffrey D. Ullman, lecture notes accompanying Aho, Lam, Sethi & Ullman, "Compilers: Principles, Techniques, and Tools" (2nd ed.); deck "Flow Graph Theory / Depth-First Ordering / Efficiency of Iterative Algorithms / Reducible Flow Graphs".
DOI/URL: http://infolab.stanford.edu/~ullman/dragon/w06/lectures/dfa3.pdf
Access: full text (PDF, read in full).
Verbatim quotes:
- "The depth of a flow graph is the greatest number of retreating edges along any acyclic path."
- "For RD, if we use DF order to visit nodes, we converge in depth+2 passes."
- "Depth+1 passes to follow that number of increasing segments." / "1 more pass to realize we converged."
- "The depth+2 bound works for any monotone framework, as long as information only needs to propagate along acyclic paths."
- "A flow graph is reducible if every retreating edge in any DFST for that flow graph is a back edge."
- "Proper ordering of nodes during iterative algorithm assures number of passes limited by the number of 'nested' back edges."
- "Normal control-flow constructs produce reducible flow graphs with the number of back edges at most the nesting depth of loops"
Exact contribution: states the bound in its modern textbook form (depth+2), decomposes it into "depth+1 to propagate, 1 to notice convergence", and states the precondition in the loosest useful form: any monotone framework where information only needs to propagate along acyclic paths.
What it does NOT do: is a restatement, not a new result; does not treat non-reducible graphs or work amplification.
Relevance to AuxFlow: this is a co-author of the original result stating the bound as settled pedagogy. The decomposition "N passes to propagate + 1 pass to confirm" is EXACTLY AuxFlow's build-plan structure (run until the stable pass number, then one confirming run).
Anticipation verdict: FULL ANTICIPATION of the abstract mechanism "derive the number of fixpoint rounds from a depth parameter of the dependency graph, add one round to confirm convergence".
Evidence label: SOURCED.

Modern textbook restatements, secondary and REPORTED (I did not open the printed textbooks; these are as summarised by course notes that quote them):
- The d+2 form with the "rapid" precondition, and the d(G) definition "maximum number of retreating edges on any acyclic path on graph G ... called the degree of loop interconnectiveness", appears in K. McKinley's CS 380C notes, https://www.cs.utexas.edu/~mckinley/380C/lecs/04.pdf , verbatim: "'Rapid' data-flow problems stabilize in at most d(G)+2 passes over the control flow graph". Evidence label: SOURCED for the notes; REPORTED as a restatement of Kam-Ullman/Hecht-Ullman.
- The d+3 form is attributed to Kam & Ullman in Cooper, Harvey & Kennedy-lineage restatements: "They showed a class of problems that a round-robin iterative algorithm, visiting nodes in reverse postorder, can solve in d(G) + 3 passes over a graph G", from "Iterative Dataflow Analysis, Revisited" (Cooper, Harvey & Kennedy, Rice TR). Evidence label: REPORTED (search-surfaced quotation; I did not open the TR).
The d+2 / d+3 discrepancy is an accounting difference over whether the initialisation pass and the confirming pass are both counted. Do not present either number as canonical without saying which convention is in use.

### PRIORITY 1 ANSWER: is "compute the number of rounds to a dataflow fixpoint from the structure of the dependency graph" solved and textbook?

Yes. Plainly and completely, for the general mechanism. Since 1975 the compiler literature has had:
1. a structural parameter of the dependency graph (loop-connectedness d, "the largest number of back edges found in any cycle-free path", Hecht & Ullman SIAM 1975);
2. a proven round-count bound of the form d+2 (or d+3 under a different accounting) for round-robin iteration in reverse postorder;
3. an exact algebraic precondition for the bound to hold (rapidity, Kam & Ullman JACM 1976), together with the observation that useful analyses can fail it;
4. the generalisation to merely monotone frameworks and the MFP/MOP conservativeness gap (Kam & Ullman 1977);
5. all of the above restated in undergraduate compiler textbooks and their lecture notes for forty years, including the exact "N passes to propagate, one more to notice you have converged" decomposition that AuxFlow's build plan uses.
AuxFlow's stable-pass numbering is this machinery transplanted to a new dependency graph. That is not novel as a method. It can only be novel as an application, and only if the LaTeX-specific parts (which facts exist, what a pass lag is, what the fact-instance nodes are) are what carries the contribution. AuxFlow must cite Hecht & Ullman 1975 and Kam & Ullman 1976 explicitly and must not present static pass-count derivation as its own invention.

### F5. Lee & Messerschmitt, "Static Scheduling of Synchronous Data Flow Programs for Digital Signal Processing" (IEEE Trans. Computers 1987)

Citation: Edward Ashford Lee and David G. Messerschmitt, "Static Scheduling of Synchronous Data Flow Programs for Digital Signal Processing", IEEE Transactions on Computers, vol. C-36, no. 1, pp. 24-35, January 1987.
DOI/URL: https://doi.org/10.1109/TC.1987.5009446 ; full text read at https://bears.ece.ucsb.edu/class/ece253/papers/lee_sdf87.pdf
Access: full text (12 pages) plus CrossRef metadata (938 citations recorded).
Verbatim quotes (from the read PDF; OCR of the two-column scan is imperfect, quotes below are the clean passages):
- Abstract: "Synchronous data flow (SDF) differs from traditional data flow in that the amount of data produced and consumed by a data flow node is specified a priori for each input and output. This is equivalent to specifying the relative sample rates in signal processing system. This means that the scheduling of SDF nodes need not be done at runtime, but can be done at compile time (statically), so the runtime overhead evaporates."
- Section III, the definition of synchrony: "A block is said to be synchronous if we can specify a priori the number of input samples consumed on each input and the number of output samples produced on each output each time the block is invoked."
- Section IV-A, the topology matrix: "The (i, j)th entry in the matrix is the amount of data produced by node j on arc i each time it is invoked. If node j consumes data from arc i, the number is negative, and if it is not connected to arc i, then the number is zero."
- Buffer state recurrence: "b(n+1) = b(n) + Gamma u(n)."
- Definition 1: "An admissible sequential schedule phi is a nonempty ordered list of nodes such that if the nodes are executed in the sequence given by phi, the amount of data in the buffers ('buffer sizes') will remain nonnegative and bounded."
- Theorem 1: "For a connected SDF graph with s nodes and topology matrix Gamma, rank(Gamma) = s - 1 is a necessary condition for a PASS to exist." And in the discussion: "The rank of the topology matrix indicates a sample rate inconsistency in the graph."
- Theorem 2: "For a connected SDF graph with s nodes and topology matrix Gamma, and with rank(Gamma) = s - 1, we can find a positive integer vector q != 0 such that Gamma q = 0 [...] This vector tells us how many times we should invoke each node in one period of a PASS."
- Theorem 3: "Given a SDF graph with topology matrix Gamma and given a positive integer vector q s.t. Gamma q = 0, if a PASS of period p = 1^T q exists [...] any class S algorithm will find such a PASS."
- Theorem 4 / corollary: a PASS of period p exists iff a PASS of period Np exists, and the choice of nullspace vector does not matter - so one may take the smallest positive integer q.
- Section V-A, "Conditionals": "The SDF model permits conditional control flow within a node, but not on a greater scale."
- Section V-A, on data-dependent output rate: "Such a node is an asynchronous node because it is not possible to specify a priori how many samples will be produced on each output when the node is invoked."
Exact contribution:
(a) STATIC SCHEDULABILITY CONDITION. An SDF graph is statically schedulable exactly when production/consumption rates are fixed and data-INDEPENDENT ("specified a priori"), and, given that, when the topology matrix has rank s-1. Rank s means sample-rate inconsistency and NO bounded periodic schedule exists at any period.
(b) BALANCE EQUATIONS AND REPETITION VECTOR. Gamma q = 0 is the system of balance equations; its positive integer nullspace solution q is the repetition vector giving each node's firing count in one schedule period; the period is p = 1^T q. Rank s-1 makes the nullspace one-dimensional, so q is unique up to scale, and the smallest positive integer q gives the minimum period.
(c) SEPARATION OF CONSISTENCY FROM DEADLOCK. Rank s-1 (consistency) is necessary but NOT sufficient: Fig. 7 shows consistent graphs with no admissible schedule - "Networks with insufficient delays in directed loops are not computable." So the analysis has two independent failure modes: rate inconsistency (unbounded buffers) and insufficient initial tokens in a cycle (deadlock).
(d) WHAT HAPPENS WHEN RATES BECOME DATA-DEPENDENT. The node becomes "asynchronous" in their terminology, and it leaves the model. The static schedule cannot be constructed because the a-priori rate specification no longer exists. Data-dependent RUNTIME is handled separately and benignly (Section V-D: schedule with worst-case runtimes); data-dependent RATE is not.
What it does NOT do: does not decide the data-dependent case; does not compute how many passes anything takes (SDF asks how many FIRINGS per period, not how many global rounds); nothing about documents or self-referential text.
Relevance to AuxFlow: SDF's dividing line - can a value influence HOW MANY firings occur, or only WHAT the firings compute - is structurally the same dividing line as AuxFlow's benign-cyclic vs amplifying. In SDF terms, AuxFlow's "benign cyclic" document is one where the auxiliary values only change the CONTENT of a fixed amount of generated material, and "amplifying" is one where an auxiliary value sets a production rate.
Anticipation verdict: PARTIAL OVERLAP (strong, and structurally the most dangerous item in this area). The DISTINCTION is anticipated in full generality. The instantiation in a document build is not.
Evidence label: SOURCED (full text).

### F6. Lee & Messerschmitt, "Synchronous data flow" (Proc. IEEE 1987)

Citation: E. A. Lee and D. G. Messerschmitt, "Synchronous data flow", Proceedings of the IEEE, vol. 75, no. 9, pp. 1235-1245, September 1987.
DOI/URL: https://doi.org/10.1109/PROC.1987.13876 (metadata via https://api.crossref.org/works/10.1109/PROC.1987.13876 ; 1394 citations recorded)
Access: metadata only. No abstract deposited in CrossRef; ptolemy.berkeley.edu (the author's own copy) timed out from this environment; I did not read the text.
Verbatim quote: none - no abstract deposited, text not obtained.
Exact contribution (REPORTED): the companion tutorial paper; same model, presented for a general engineering audience, with the same synchrony definition and the same static-scheduling result.
Relevance to AuxFlow: same as F5; cite F5 for anything load-bearing since that is the copy actually read.
Anticipation verdict: same as F5 by construction, but not independently verified here.
Evidence label: metadata SOURCED; content REPORTED.

## Negative results

### Hecht "Flow Analysis of Computer Programs" (1977, Elsevier/North-Holland)
query    : `read https://api.crossref.org/works/10.1137/0201014` (as reducibility candidate) plus the searches above
outcome  : NOT USED as the source of the iteration bound. The bound's primary source is the SIAM J. Comput. 1975 paper (F2), identified from Kam & Ullman 1977's own reference list, which cites "Hecht, M. S., Ullman, J. D.: A simple algorithm for global flow analysis problems. SIAM J. Computing 4, 519-532 (1975)". The 1977 monograph restates the result; I did not obtain it and make no claim about its wording. Not a negative result about the bound, only about my access to the book.
status   : REPORTED

### ptolemy.berkeley.edu author copies
query    : `read https://ptolemy.berkeley.edu/publications/papers/87/synchronousDataflow/`, `read https://ptolemy.berkeley.edu/publications/papers/93/jbuckThesis/`
outcome  : NOTHING RETRIEVED. Both requests timed out. This is an access failure, not evidence of absence.
status   : failed fetch

## Outstanding searches

- Full text of Kam & Ullman, Acta Informatica 7(3):305-317, 1977 - to quote the monotone-framework convergence theorem and the MOP undecidability result directly rather than relying on the standard REPORTED summary.
- Full text of Lee & Messerschmitt, Proc. IEEE 75(9), 1987, from a mirror other than ptolemy.berkeley.edu.
- Printed textbook restatements opened directly: Aho/Lam/Sethi/Ullman 2nd ed. Section 9.6.7; Nielson, Nielson & Hankin "Principles of Program Analysis" Chapter 6; Cooper & Torczon "Engineering a Compiler" Section 9.5. Only lecture-note quotations of these were obtained.
- Priority 4 (Datalog semi-naive round bounds; reactive-programming topological stratification and glitch freedom) - NOT ATTEMPTED.
- Priority 5 (macro-expansion termination, C++ template instantiation depth limits, term-rewriting termination) - NOT ATTEMPTED.

## Summary for the audit

- **Deriving the number of fixpoint rounds from a structural parameter of the dependency graph is a
  fifty-year-old textbook result.** Hecht & Ullman, SIAM J. Comput. 4(4):519-532, 1975, DOI
  10.1137/0204044, define loop-connectedness d as "the largest number of back edges found in any
  cycle-free path in G" and relate it to the round count of reverse-postorder round-robin iteration
  over a *reducible* flow graph. Kam & Ullman, JACM 1976, DOI 10.1145/321921.321938, supply the
  algebraic precondition (rapidity) and show useful analyses can fail it.
- **Ullman's own restatement makes the anticipation exact, including AuxFlow's plan shape.** From
  his Dragon Book lecture notes: "The depth of a flow graph is the greatest number of retreating
  edges along any acyclic path"; "if we use DF order to visit nodes, we converge in depth+2 passes";
  "Depth+1 passes to follow that number of increasing segments" plus "1 more pass to realize we
  converged"; and the precondition in its loosest useful form, "The depth+2 bound works for any
  monotone framework, as long as information only needs to propagate along acyclic paths."
  AuxFlow's build plan is literally "N passes to propagate, one more to confirm". **FULL
  ANTICIPATION of the mechanism.** AuxFlow must cite Hecht & Ullman 1975 and Kam & Ullman 1976 and
  must not present static pass-count derivation as its own.
- **Do not quote a canonical constant.** d+2 and d+3 both circulate, differing on whether the
  initialisation and confirming passes are counted. Say which convention is in use or say neither.
- **The second-most dangerous item, and structurally the closest analogue of AuxFlow's central
  distinction, is synchronous dataflow.** Lee & Messerschmitt, IEEE Trans. Computers C-36(1):24-35,
  1987, DOI 10.1109/TC.1987.5009446, verbatim: "Synchronous data flow (SDF) differs from traditional
  data flow in that the amount of data produced and consumed by a data flow node is specified a
  priori for each input and output. [...] This means that the scheduling of SDF nodes need not be
  done at runtime, but can be done at compile time (statically), so the runtime overhead
  evaporates." And their definition: "A block is said to be synchronous if we can specify a priori
  the number of input samples consumed on each input and the number of output samples produced on
  each output each time the block is invoked."
- **SDF's dividing line is AuxFlow's dividing line, stated in 1987 and in full generality:** can a
  value determine *how many* firings occur, or only *what* they compute? A node whose output rate
  depends on data "is an asynchronous node because it is not possible to specify a priori how many
  samples will be produced on each output when the node is invoked", and it leaves the statically
  schedulable model. AuxFlow's "benign cyclic" is the fixed-rate case; "amplifying" is the
  data-dependent-rate case. **PARTIAL OVERLAP, strong.** The distinction is anticipated; the
  instantiation in a document build is not.
- **SDF also supplies two things AuxFlow should borrow.** First, the separation of *rate
  consistency* (rank of the topology matrix = s-1; failure means no bounded schedule exists at any
  period) from *deadlock* (insufficient initial tokens in a directed loop) - two independent static
  failure modes, which is a better-factored taxonomy than AuxFlow's single `AMPLIFYING` label.
  Second, the treatment of data-dependent *runtime* as benign (schedule with worst-case runtimes)
  while data-dependent *rate* is fatal - exactly the `exists`/`value` distinction AuxFlow makes, and
  a citable precedent for making it.
- **Kam & Ullman 1977 (Acta Informatica 7(3):305-317, DOI 10.1007/BF00290339) is the setting for
  AuxFlow's "monotone fixpoint" wording**, and its MFP-versus-MOP gap is the formal reason a static
  analysis of this shape must be conservative - i.e. the reason an `UNKNOWN` class is required
  rather than optional. Metadata verified; no abstract is deposited, so the contribution is REPORTED
  here and must be read before being cited for a specific claim.
- **Blunt verdict on how much of AuxFlow's static analysis is a re-derivation.** Essentially all of
  the machinery: the graph-structural round bound (Hecht & Ullman 1975), the monotone-framework
  fixpoint (Kam & Ullman 1976/1977), the "one extra round to notice convergence" accounting
  (Ullman's own notes), the SCC-decomposition-plus-condensation strategy (Sharir 1981, cited on the
  face of US10025569B2; Jones 1990 in the attribute-grammar setting), and the fixed-rate versus
  data-dependent-rate schedulability distinction (Lee & Messerschmitt 1987). What is *not* a
  re-derivation is the specific instantiation: which facts exist in a LaTeX document, what a pass
  lag of 1 means mechanically, that fact instances rather than fact kinds are the right nodes, and
  the empirical comparison against the deployed dynamic detectors. **AuxFlow's static analysis
  should be presented as an application of settled compiler theory, with the contribution located
  entirely in the domain model and the evaluation.**
- **One thing this area does NOT anticipate, and it is worth stating.** All of the above assumes the
  graph is fixed while the fixpoint runs. SDF's rank test decides whether a *given* graph is
  schedulable; Hecht & Ullman's d is a property of a *given* flow graph. AuxFlow's amplifying case is
  the one where the graph itself grows as a function of the iterate. SDF handles this by excluding
  such nodes from the model, not by analysing them. That exclusion boundary is where AuxFlow sits.
