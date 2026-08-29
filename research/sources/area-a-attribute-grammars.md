# Attribute Grammars, Multipass Evaluation, Pass-Number Assignment, Circular and Fixpoint Attribute Evaluation

Search area A: attribute grammars, multipass attribute evaluation, pass-number assignment, circular attribute grammars, fixed-point attribute evaluation. Audit date 2026-08-27.

Scope note. This area covers the classical AG literature that AuxFlow's architecture (dependency graph over fact instances, per-instance pass numbers by monotone fixpoint, Tarjan SCC, cycle classification, termination question) most directly touches. The headline results are worse for AuxFlow than the pre-audit position assumed: the instance-level relaxation of pass numbering is a *named, dated, complexity-classified* AG class (`pure multi-pass`, Engelfriet and File 1981), the SCC-condensation-plus-fixpoint evaluator architecture is Jones 1990, and the "evaluation generates more content, does it terminate?" problem is Vogt/Swierstra/Kuiper 1989 plus Krishnan and Van Wyk 2012.

---

## Search log

### dl.acm.org (direct DOI resolution)
query    : `https://dl.acm.org/doi/10.1145/359997.359999`
examined : 1 landing page (full metadata + abstract + full reference list rendered)
outcome  : Confirms Bochmann, "Semantic evaluation from left to right", Communications of the ACM, Volume 19, Issue 2, Pages 55-62, published 01 February 1976. DOI 10.1145/359997.359999 resolves to exactly this. Marked "Free access". Abstract captured verbatim. Reference list captured (19 items).
status   : SOURCED

### dblp.org publication search API
query    : `https://dblp.org/search/publ/api?q=Minimizing+the+number+of+evaluation+passes+for+attribute+grammars&h=30&format=json`
examined : 1 hit (total 1)
outcome  : **The title "Minimizing the Number of Evaluation Passes for Attribute Grammars" belongs to a SIAM J. Comput. article, not an ICALP paper.** Rahia and Ukkonen, SIAM J. Comput. 10(4):772-786, 1981, DOI 10.1137/0210060, dblp key `journals/siamcomp/RaihaU81`. Zero ICALP hits under this title.
status   : SOURCED

### dblp.org publication search API
query    : `https://dblp.org/search/publ/api?q=Ukkonen+attribute+grammars&h=50&format=json`
examined : 1 hit (total 1)
outcome  : Ukkonen has exactly one dblp-indexed record matching "attribute grammars" by title keyword: the SIAM 1981 paper. No ICALP record surfaces under a title-keyword search. (Ukkonen's dblp author page has 160 records, overwhelmingly bioinformatics/string algorithms from the 1990s onward.)
status   : SOURCED

### dblp.org ICALP 1980 proceedings table of contents
query    : `https://dblp.org/db/conf/icalp/icalp80.html`
examined : full TOC of 7th ICALP 1980, LNCS 85
outcome  : **Decisive.** The paper at LNCS 85 pages 500-511 is Kari-Jouko Rahia, Esko Ukkonen, "On the Optimal Assignment of Attributes to Passes in Multi-Pass Attribute Evaluators". Also in the same volume: Joost Engelfriet, Gilberto File, "Formal Properties of One-Visit and Multi-Pass Attribute Grammars", pages 182-194; Erik Meineche Schmidt, "Space-Restricted Attribute Grammars", pages 436-448. Editors: J. W. de Bakker, Jan van Leeuwen, LNCS 85, Springer 1980, ISBN 3-540-10003-2.
status   : SOURCED

### dblp.org record page
query    : `https://dblp.org/rec/conf/icalp/RaihaU80.html`
examined : 1 record
outcome  : Confirms title "On the Optimal Assignment of Attributes to Passes in Multi-Pass Attribute Evaluators", Rahia and Ukkonen (1980), DOI 10.1007/3-540-10003-2_94.
status   : SOURCED

### link.springer.com (Springer LNCS 85 book page)
query    : `https://link.springer.com/book/10.1007/3-540-10003-2`
examined : book front matter + partial chapter list
outcome  : Confirms LNCS volume 85, Softcover ISBN 978-3-540-10003-4, eBook ISBN 978-3-540-39346-7, X+671 pages, "Automata, Languages and Programming, Seventh Colloquium, Noordwijkerhout, The Netherlands, July 14-18, 1980". Confirms Engelfriet/File chapter DOI `_70` at pages 182-194, titled with "(extended abstract)" suffix on Springer.
status   : SOURCED

### epubs.siam.org (direct DOI resolution)
query    : `https://epubs.siam.org/doi/10.1137/0210060`
examined : 1 landing page (abstract + keywords + full reference list + history)
outcome  : **Resolves the miscitation.** SIAM J. Comput. Volume 10, Issue 4, November 1981, Pages 772-786. Submitted 19 December 1979, accepted 20 November 1980. Abstract captured verbatim. Reference [17] of this very paper cites the ICALP version under its *correct* title with Crossref DOI 10.1007/3-540-10003-2_94. Reference [19] is Tarjan 1972 (DFS/SCC).
status   : SOURCED

### doi.org / CrossRef API
query    : `https://doi.org/10.1007/3-540-10003-2_94`
examined : 1 CrossRef record
outcome  : Resolves to "On the optimal assignment of attributes to passes in multi-pass attribute evaluators", Rahia and Ukkonen, Lecture Notes in Computer Science, Springer Berlin Heidelberg, 1980, book chapter. No abstract available in CrossRef.
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/article/10.1007/BF00264495`
examined : 1 landing page (full metadata + abstract + partial reference list in page metadata)
outcome  : Confirms Alblas, "A characterization of attribute evaluation in passes", Acta Informatica, volume 16, issue 4, pages 427-464, cover date 1981/12/01, Springer-Verlag, author affiliation Twente University of Technology. Abstract captured verbatim. **Critically, one of the embedded `citation_reference` metadata entries is the source of the propagated miscitation** (see "The Rahia and Ukkonen miscitation" section below).
status   : SOURCED

### api.semanticscholar.org graph API by DOI
query    : `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/S0019-9958(81)90466-6?fields=title,year,venue,abstract,openAccessPdf`
examined : 1 record
outcome  : **Answers the "which paper has the pure-multipass complexity result" question.** Returns the publisher abstract of Engelfriet and File, Information and Control 1981, containing the inherently-exponential-time result. Captured verbatim below.
status   : SOURCED

### ris.utwente.nl institutional repository (open access full text)
query    : `https://ris.utwente.nl/ws/files/6563081/Engelfriet82simple.pdf`
examined : full 32-page article
outcome  : **Most important single find in this area.** Engelfriet and File, "Simple Multi-Visit Attribute Grammars", JCSS 24, 283-314 (1982). Contains the definitive verbatim definitions of `pure m-pass` versus `simple m-pass`, the complete complexity taxonomy of all four pass/visit classes, and the explicit statement that Bochmann's class is `simple` multi-pass.
status   : SOURCED

### fileadmin.cs.lth.se (Lund University author preprint, open access)
query    : `https://fileadmin.cs.lth.se/sde/publications/papers/2007-MagnussonEva-CRAGs-SCP-Preprint.pdf`
examined : full preprint (~24 pages)
outcome  : Magnusson and Hedin CRAG paper full text. Yields the exact termination condition (lattice of finite height + monotone semantic functions; footnote: CPO + ascending chain condition), the explicit admission that the evaluator does not check it and therefore has no convergence guarantee, and a SOURCED description of Jones's SCC-condensation fixpoint algorithm and Boyland's undecidability result.
status   : SOURCED

### www-users.cse.umn.edu (University of Minnesota author copy, open access)
query    : `https://www-users.cse.umn.edu/~evw/pubs/krishnan12sle/krishnan12sle.pdf`
examined : full 20-page paper including related work
outcome  : **The single most dangerous piece of prior art in this area.** Krishnan and Van Wyk, "Termination Analysis for Higher-Order Attribute Grammars". A conservative static analysis whose entire purpose is to decide whether attribute evaluation that *generates new content to be evaluated* terminates, explicitly distinguished from circularity analysis. Captured verbatim.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Higher order attribute grammars Vogt Swierstra Kuiper`
examined : 4 hits
outcome  : Three distinct records for the same work: ACM SIGPLAN Notices 24(7):131-145, 1989, DOI 10.1145/74818.74830; PLDI 1989 proceedings, pages 131-145, DOI 10.1145/73141.74830; LNCS (SAGA 1991) chapter, pages 256-296, DOI 10.1007/3-540-54572-7_10. Also surfaces Vogt/Swierstra/Kuiper, "Efficient incremental evaluation of higher order attribute grammars", LNCS 1991, pages 231-242, DOI 10.1007/3-540-54444-5_102.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Ordered attributed grammars Kastens`
examined : 3 hits
outcome  : Kastens, "Ordered attributed grammars", Acta Informatica 13(3):229-256, 1980, DOI 10.1007/BF00288644. (Note: the widely circulated citation omits the issue number and gives "13 (1980), 229-256"; CrossRef supplies issue 3.)
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Semantics of context-free languages Knuth`
examined : 4 hits
outcome  : Knuth, "Semantics of context-free languages", Mathematical Systems Theory 2(2):127-145, 1968, DOI 10.1007/BF01692511. Knuth, "Semantics of context-free languages: Correction", Mathematical Systems Theory 5(2):95-96, 1971, DOI 10.1007/BF01702865. **CrossRef says issue 2 for the correction; almost every secondary citation says 5(1).**
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/article/10.1007/BF01702865`
examined : 1 landing page metadata
outcome  : Springer authoritative metadata: `citation_issue: 2`, `prism.number: 2`, `dc.source: Mathematical systems theory 1971 5:2`, cover date 1971/06/01, pages 95-96. **The near-universal "5(1), 95-96" citation is wrong; it is 5(2).** No abstract (it is a two-page correction).
status   : SOURCED

### dblp.org publication search API
query    : `https://dblp.org/search/publ/api?q=circularity+attribute+grammars&h=30&format=json`
examined : 12 hits (total 12)
outcome  : Full circularity-complexity chain verified: Jazayeri/Ogden/Rounds CACM 18(12):697-706 1975 (DOI 10.1145/361227.361231) and POPL 1975 pages 119-129 (DOI 10.1145/512976.512989, open access); Jazayeri JACM 28(4):715-720 1981 (DOI 10.1145/322276.322283); Dill JACM 36(1):92-96 1989 counter-example (DOI 10.1145/58562.77393); Engelfriet SIGACT News 20(3):57-59 1989 (DOI 10.1145/70642.70645); Rahia and Saarinen Acta Informatica 17:185-192 1982 (DOI 10.1007/BF00288969); Deransart/Jourdan/Lorho Acta Informatica 21:375-391 1984 (DOI 10.1007/BF00264616); Wu TOPLAS 26(1):186-190 2004 (DOI 10.1145/963778.963783); Wu arXiv cs/0010015; Wu and Wang TOPLAS 17(2):228-232 1995 (DOI 10.1145/201059.201064); Sagiv/Edelstein/Francez/Rodeh POPL 1989 pages 36-48 (DOI 10.1145/75277.75281).
status   : SOURCED

### dblp.org publication search API
query    : `https://dblp.org/search/publ/api?q=author%3AHenk_Alblas%3A+attribute&h=50&format=json`
examined : 12 hits (total 12)
outcome  : Confirms Alblas Acta Informatica 16:427-464 1981 (DOI 10.1007/BF00264495); Alblas SIAM J. Comput. 14(4):889-914 1985 "Finding Minimal Pass Sequences for Attribute Grammars" (DOI 10.1137/0214063); Alblas Acta Informatica 27(1):1-40 1989 "Iteration of Transformation Passes over Attributed Program Trees" (DOI 10.1007/BF00263499); Alblas IPL 32(6):289-295 1989 "Optimal Incremental Simple Multi-Pass Attribute Evaluation" (DOI 10.1016/0020-0190(89)90020-3); Alblas SAGA 1991 chapters (DOIs 10.1007/3-540-54572-7_1, `_3`, `_8`); LNCS 545 volume DOI 10.1007/3-540-54572-7.
status   : SOURCED

### dblp.org publication search API
query    : `https://dblp.org/search/publ/api?q=Engelfriet+File+attribute+grammars&h=50&format=json`
examined : 4 hits (total 4)
outcome  : The Engelfriet/File pass-and-visit corpus: ICALP 1980 pages 182-194 (DOI 10.1007/3-540-10003-2_70); Acta Informatica 16:275-302 1981 "The Formal Power of One-Visit Attribute Grammars" (DOI 10.1007/BF00289307); JCSS 24(3):283-314 1982 "Simple Multi-Visit Attribute Grammars" (DOI 10.1016/0022-0000(82)90030-7, open access); JACM 36(4):841-869 1989 "Passes, sweeps, and visits in attribute grammars" (DOI 10.1145/76359.76366). Note: the Information and Control 1981 "Passes and paths" paper does not appear in this dblp keyword search and had to be found via CrossRef.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Passes and paths of attribute grammars Engelfriet File`
examined : 4 hits
outcome  : Engelfriet and File, "Passes and paths of attribute grammars", Information and Control 49(2):125-169, 1981, DOI 10.1016/S0019-9958(81)90466-6. Confirms the paper the task asked about exists with exact pages.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Automatic generation of fixed-point-finding evaluators for circular but well-defined attribute grammars Farrow`
examined : 4 hits
outcome  : Farrow, SIGPLAN '86 Symposium on Compiler Construction, pages 85-98, DOI 10.1145/12276.13320 (proceedings) and ACM SIGPLAN Notices 21(7):85-98, DOI 10.1145/13310.13320 (journal). Also surfaces Sasaki and Sassa, "Circular attribute grammars with remote attribute references and their evaluators", New Generation Computing 22(1):37-60, 2004, DOI 10.1007/BF03037280.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Efficient evaluation of circular attribute grammars Jones`
examined : 4 hits
outcome  : Jones, "Efficient evaluation of circular attribute grammars", ACM Transactions on Programming Languages and Systems 12(3):429-462, 1990, DOI 10.1145/78969.78971.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Remote attribute grammars Boyland Journal of the ACM`
examined : 4 hits
outcome  : Boyland, "Remote attribute grammars", Journal of the ACM 52(4):627-687, 2005, DOI 10.1145/1082036.1082042.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Termination Analysis for Higher-Order Attribute Grammars`
examined : 1 hit
outcome  : Lecture Notes in Computer Science, pages 44-63, 2013, DOI 10.1007/978-3-642-36089-3_4 (SLE 2012, LNCS 7745, published 2013).
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/chapter/10.1007/978-3-319-02654-1_17`
examined : 1 landing page (abstract + full 27-item reference list)
outcome  : Soderberg and Hedin, "Circular Higher-Order Reference Attribute Grammars", SLE 2013, LNCS 8225, pages 302-321. Abstract captured verbatim. Reference list independently corroborates Krishnan/Van Wyk SLE 2012 LNCS 7745 pages 44-63; Jones TOPLAS 12(3):429-462 1990; Boyland JACM 52(4):627-687 2005; Ekman and Hedin ECOOP 2004 LNCS 3086 pages 147-171; Knuth 1968 2(2):127-145 with correction "5(1), 95-96".
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/chapter/10.1007/3-540-54572-7_10`
examined : 1 landing page (abstract + full 25-item reference list)
outcome  : **Definitive on the "does an attribute value change the tree" question.** Swierstra and Vogt, "Higher Order Attribute Grammars", SAGA School 1991, LNCS 545, pages 256-296. Abstract captured verbatim, and it states directly that the parse-tree/attribute domain distinction has disappeared. Reference list corroborates Vogt/Swierstra/Kuiper PLDI 1989 pages 131-145, Kastens Acta Informatica 13:229-256 1980, and surfaces Teitelbaum and Chapman, "Higher-Order Attribute Grammars and Editing Environments", PLDI 1990, pages 197-208.
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/chapter/10.1007/3-540-54572-7_3`
examined : 1 landing page (abstract + full 40+-item reference list)
outcome  : Alblas, "Attribute evaluation methods", SAGA School 1991, LNCS 545, pages 48-113. Abstract captured verbatim. Reference list independently corroborates Bochmann CACM 19:55-62 1976; Alblas Acta Informatica 16:427-464 1981; Alblas SIAM J. Comput. 14:889-914 1985; Engelfriet and File Information and Control 49:125-169 1981; Engelfriet and File Acta Informatica 16:275-302 1981; Engelfriet and File JCSS 24:283-314 1982; Kastens Acta Informatica 13:229-256 1980; Farrow SIGPLAN '86 pages 85-98; and surfaces Engelfriet and File, "Passes, sweeps and visits in attribute grammars", 8th ICALP, LNCS 115 (1981), pages 193-207.
status   : SOURCED

### link.springer.com (direct DOI resolution)
query    : `https://link.springer.com/article/10.1007/BF00263499`
examined : 1 landing page metadata + abstract
outcome  : **Second-most-dangerous find.** Alblas, "Iteration of transformation passes over attributed program trees", Acta Informatica 27(1):1-40, 1989. Abstract captured verbatim: alternating attribute-evaluation and tree-transformation phases, consistent versus approximate attribute values, and an explicit statement that the strategy resembles circular-AG evaluation methods.
status   : SOURCED

### arxiv.org API
query    : `https://arxiv.org/abs/cs/0010015`
examined : 1 record
outcome  : Wu, "On Exponential-Time Completeness of the Circularity Problem for Attribute Grammars", arXiv cs/0010015, 2000. Abstract captured verbatim; closes the EXPTIME-*complete* (not merely hard) question.
status   : SOURCED

### creichen.net (author-maintained BibTeX bibliography)
query    : `https://creichen.net/bibtex.html`
examined : full bibliography
outcome  : Riouak, Fors, Oqvist, Hedin, Reichenbach, "Efficient Demand Evaluation of Fixed-Point Attributes using Static Analysis", SLE '24, pages 56-69, DOI 10.1145/3687997.3695644, ISBN 9798400711800, Pasadena CA. Author-supplied abstract captured verbatim.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Rewritable reference attributed grammars Ekman Hedin ECOOP 2004`
examined : 2 hits
outcome  : Ekman and Hedin, "Rewritable Reference Attributed Grammars", LNCS (ECOOP 2004), pages 147-171, DOI 10.1007/978-3-540-24851-4_7.
status   : SOURCED

### api.crossref.org bibliographic query
query    : `query.bibliographic=Strategic tree rewriting in attribute grammars`
examined : 2 hits
outcome  : "Strategic tree rewriting in attribute grammars", SLE 2020, pages 210-229, DOI 10.1145/3426425.3426943. (Authors not captured in the selected fields; Kramer and Van Wyk per the venue, marked REPORTED.)
status   : REPORTED

### web_search
query    : `Vogt Swierstra Kuiper "Higher order attribute grammars" PLDI 1989 SIGPLAN pages DOI`
examined : 20 sources
outcome  : Surfaced the Krishnan and Van Wyk termination-analysis paper (the critical find) and the dual ACM DOIs for the HAG paper. Confirms SIGPLAN Not. 24(7):131-145, June 1989.
status   : REPORTED (used only for discovery; every claim then verified against CrossRef/Springer/author copies)

### web_search
query    : `Magnusson Hedin "Circular reference attributed grammars" fixed-point iteration termination lattice finite height JastAdd`
examined : 25 sources
outcome  : Located the Lund author preprint (then read directly) and the Wisconsin thesis "Statically Scheduling Circular Remote Attribute Grammars", plus Soderberg and Hedin 2013 and Riouak et al. 2024.
status   : REPORTED (used only for discovery)

### web_search
query    : `Boyland "Remote attribute grammars" JACM 2005 "undecidable" circularity approximation abstract`
examined : 10 sources
outcome  : Boyland's undecidability result restated in secondary summaries. Could not open the ACM abstract page (403 / Cloudflare). The claim is however independently confirmed by two primary sources I read in full (Magnusson and Hedin 2007 preprint; Krishnan and Van Wyk 2012).
status   : REPORTED for Boyland's own wording; SOURCED for the fact via two citing primary sources

### web_search
query    : `attribute grammar analysis classify cycles "benign" convergent versus divergent fixpoint taint influence tree size`
examined : 18 sources
outcome  : NOTHING RELEVANT in the sense of an AG paper that classifies cycles into "converges" versus "may diverge" *by tracking whether cycle-carried values influence how much content is generated*. The literature splits the problem differently: circularity analysis (does a cycle exist), well-definedness by lattice/monotonicity (does a cycle converge, assumed rather than proved), and higher-order termination analysis (does tree creation stop). No taint-style influence analysis on this question surfaced.
status   : REPORTED (negative)

### ACM Digital Library full-text retrieval attempts
query    : `https://dl.acm.org/doi/pdf/10.1145/359997.359999`, `https://dl.acm.org/doi/pdf/10.1145/74818.74830`, `https://dl.acm.org/doi/pdf/10.1145/3687997.3695644`, `https://dl.acm.org/doi/10.1145/1082036.1082042`, `https://dl.acm.org/doi/10.1145/78969.78971`
examined : 5 attempts, including one via a real Chromium instance
outcome  : NOTHING RETRIEVED. Cookie-absent redirect, HTTP 403, and a Cloudflare "Just a moment..." interstitial that did not clear within 90 seconds. Bochmann's abstract and reference list were captured earlier from the DOI *landing* page before the block; the full PDFs of Bochmann 1976, Vogt et al. 1989, Jones 1990, Boyland 2005 and Riouak et al. 2024 were not read.
status   : REPORTED (access failure, explicitly recorded)

### www.sciencedirect.com
query    : `https://www.sciencedirect.com/science/article/pii/0022000082900307`
examined : 1 attempt
outcome  : HTTP 403. Worked around via the University of Twente institutional repository open-access copy (`ris.utwente.nl`), which yielded the full text.
status   : REPORTED (access failure, worked around)

### epubs.siam.org
query    : `https://epubs.siam.org/doi/10.1137/0214063`
examined : 1 attempt
outcome  : Cookie-absent redirect. Alblas 1985 "Finding Minimal Pass Sequences for Attribute Grammars" is therefore **metadata-only**: verified title/venue/volume/pages/DOI via dblp and via Alblas's own 1991 reference list, but the abstract was NOT read.
status   : REPORTED (access failure, explicitly recorded)

---

## The Rahia and Ukkonen citation: resolved, and it was wrong

The pre-audit citation was: *K.-J. Rahia and E. Ukkonen, "Minimizing the number of evaluation passes for attribute grammars", ICALP 1980, LNCS 85.*

**Verdict: that citation is a conflation of two distinct publications, and it is what circulates in the literature. Both underlying papers are real.**

| | Title | Venue | Pages | Year | DOI |
|---|---|---|---|---|---|
| Conference version | On the Optimal Assignment of Attributes to Passes in Multi-Pass Attribute Evaluators | 7th ICALP, LNCS 85 | 500-511 | 1980 | 10.1007/3-540-10003-2_94 |
| Journal version | Minimizing the Number of Evaluation Passes for Attribute Grammars | SIAM J. Comput. 10(4) | 772-786 | 1981 | 10.1137/0210060 |

So: the *pages* (500-511), *venue* (ICALP 1980, LNCS 85) and *year* (1980) in the pre-audit citation are correct for the conference paper, but the *title* belongs to the 1981 SIAM journal paper.

**The provenance of the error is traceable to Alblas 1981 itself.** The Springer landing page for `10.1007/BF00264495` exposes Alblas's own reference list in its `citation_reference` metadata, and one entry reads verbatim:

> "Rahia, K.-J., Ukkonen, E.: Minimizing the number of evaluation passes for attribute grammars. Proc. 7th Int. Colloq. on Automata, Languages and Programming 1980, Lecture Notes in Computer Science 85, pp. 500-511. Berlin-Heidelberg-New York: Springer 1980"

(SOURCED, `link.springer.com/article/10.1007/BF00264495`, page metadata `citation_reference`. Note the transcription is otherwise faithful, including the pages, so Alblas evidently had the ICALP paper in hand and cited it under the title of the journal submission that was then in review -- the SIAM paper was submitted 19 December 1979, i.e. *before* ICALP 1980.)

Rahia and Ukkonen's own SIAM paper cites the ICALP version under its correct title (reference [17], with the Crossref link to `_94`), which is the cleanest possible confirmation.

**Recommendation for AuxFlow.** Cite the SIAM J. Comput. 1981 paper, not the ICALP one, since the journal version carries the NP-completeness result and the `2n-1` worst-case bound. If both are wanted, cite them under their correct distinct titles. Reproducing the conflated citation would be a visible bibliographic error to any AG reviewer.

---

## Verified sources

### A1. Bochmann 1976 -- the origin of static pass-number assignment

- **Citation**: Gregor V. Bochmann. "Semantic evaluation from left to right". *Communications of the ACM*, Volume 19, Issue 2, pages 55-62, February 1976.
- **DOI / URL**: 10.1145/359997.359999 -- <https://doi.org/10.1145/359997.359999>. **DOI verified to resolve to exactly this article.**
- **Access**: Abstract, full bibliographic metadata, keyword list and full 19-item reference list read from the ACM DOI landing page. Marked "Free access" by ACM, but the PDF itself could not be retrieved (Cloudflare). Full text NOT read.
- **Verbatim quote** (abstract, complete):
  > "This paper describes attribute grammars and their use for the definition of programming languages and compilers; a formal definition of attribute grammars and a discussion of some of its important aspects are included. The paper concentrates on the evaluation of semantic attributes in a few passes from left to right over the derivation tree of a program. A condition for an attribute grammar is given which assures that the semantics of any program can be evaluated in a single pass over the derivation tree, and an algorithm is discussed which decides how many passes from left to right are in general necessary, given the attribute grammar. These notions are explained in terms of an example grammar which describes the scope rules of Algol 60. Practical questions, such as the relative efficiency of different evaluation schemes, and the ease of adapting the attribute grammar of a given programming language to the left-to-right evaluation scheme are discussed."
  ACM-assigned keywords, verbatim: "attribute grammars; left-to-right parsing; multipass compilers; semantic attributes; semantic conditions; semantic evaluation; semantics of programming languages".
- **Exact contribution**: (a) a one-pass (left-to-right) evaluability condition on an attribute grammar; (b) **an algorithm that, given the grammar alone and with no input tree, decides how many left-to-right passes are in general necessary** -- i.e. static pass counting; (c) a worked Algol 60 scope-rules example; (d) practical discussion of evaluation-scheme efficiency and of retrofitting an existing language's AG onto left-to-right evaluation.

  What the algorithm computes, established from primary sources other than Bochmann's own text: Engelfriet and File (JCSS 1982, page 284, read in full) state verbatim that "Note that the class of simple multi-pass AG is that actually considered in [2]" where [2] is Bochmann 1976, and that "The simple multi-pass property is decidable in polynomial time by the algorithm in [2]." So Bochmann's algorithm assigns **one pass number per attribute of per nonterminal** -- a per-attribute-kind numbering, uniform across all instances in all trees -- and runs in polynomial time. Alblas's 1981 abstract independently confirms this reading of the terminology, and Alblas's own reference list cites Bochmann as the source of the "simple multi-pass" strategy.
- **What it does NOT do**: it does not assign pass numbers per *attribute instance*; it does not admit right-to-left or mixed pass directions (Alblas 1981 adds those); it does not handle cyclic dependencies at all (non-circularity is presupposed); it does not decide the *pure* multi-pass property, which is a strictly larger class and, as of Engelfriet and File 1981, EXPTIME-complete; it has no notion of an attribute value changing how much tree there is.
- **Relevance to AuxFlow**: This is the direct ancestor of AuxFlow's "propagate a per-fact stable pass number by monotone fixpoint over a dependency graph whose edges carry a pass lag". The lag-1 edge ("written in run p, readable in run p+1") is exactly the mechanism by which a left-to-right pass evaluator defers an attribute to the next pass. AuxFlow's pass-number step is a re-derivation of Bochmann's, not an invention.
- **Anticipation verdict**: **FULL ANTICIPATION** of static, grammar-only, dependency-graph-based pass-count computation. AuxFlow must not claim this.
- **Evidence label**: SOURCED (metadata, abstract, keywords, reference list); the characterisation of *what* the algorithm computes is SOURCED from Engelfriet and File 1982 and Alblas 1981 rather than from Bochmann's body text.

### A2. Rahia and Ukkonen 1980 -- conference version

- **Citation**: Kari-Jouko Rahia, Esko Ukkonen. "On the optimal assignment of attributes to passes in multi-pass attribute evaluators". In J. W. de Bakker and Jan van Leeuwen (eds.), *Automata, Languages and Programming, 7th Colloquium, Noordwijkerhout, The Netherlands, July 14-18, 1980, Proceedings*, Lecture Notes in Computer Science 85, Springer, 1980, pages 500-511. ISBN 3-540-10003-2.
- **DOI / URL**: 10.1007/3-540-10003-2_94 -- <https://doi.org/10.1007/3-540-10003-2_94>. Confirmed to resolve to this title via CrossRef, and independently listed with this DOI on dblp (`conf/icalp/RaihaU80`) and in the SIAM 1981 paper's own reference [17].
- **Access**: Metadata only (CrossRef + dblp + Springer volume page + citing reference lists). No abstract exists in CrossRef; the chapter is paywalled and was not read.
- **Verbatim quote**: none available. The closest primary-source evidence of content is the SIAM journal version's abstract (A3), which supersedes it.
- **Exact contribution**: Presumed to be the conference presentation of the results appearing in A3. **UNVERIFIED as to whether the ICALP and SIAM contents differ.** The SIAM version was submitted 19 December 1979 and accepted 20 November 1980, straddling ICALP 1980 (July 1980), so the two are contemporaneous rather than the usual conference-then-journal sequence.
- **What it does NOT do**: unknown in detail; see A3.
- **Relevance to AuxFlow**: bibliographic only. Cite A3 instead.
- **Anticipation verdict**: PARTIAL OVERLAP (subsumed by A3).
- **Evidence label**: SOURCED for all bibliographic fields; content UNVERIFIED.

### A3. Rahia and Ukkonen 1981 -- pass minimisation is NP-complete

- **Citation**: Kari-Jouko Rahia, Esko Ukkonen. "Minimizing the Number of Evaluation Passes for Attribute Grammars". *SIAM Journal on Computing*, Volume 10, Issue 4, pages 772-786, November 1981. Submitted 19 December 1979; accepted 20 November 1980.
- **DOI / URL**: 10.1137/0210060 -- <https://doi.org/10.1137/0210060>
- **Access**: Abstract, keywords, publication history and full 19-item reference list read from the SIAM landing page. Full text paywalled and NOT read.
- **Verbatim quote** (abstract, complete):
  > "The problem of constructing multi-pass evaluators for attribute grammars is studied. We show that the construction algorithm used heretofore can in the worst case produce evaluators which perform $2n - 1$ passes over the parse tree, where *n* is the minimum number of passes required. Furthermore, the problem of constructing an optimal evaluation order is shown to be NP-complete. We then develop a new characterization for attribute grammars evaluable in passes. It can be directly applied as an efficient membership test. Finally, the characterization is used for deriving a polynomial time construction algorithm for a large subclass of pass-oriented attribute grammars. The subclass is argued to be of practical importance."
  SIAM-assigned keywords, verbatim: "attribute grammars; multi-pass evaluators; NP-completeness; approximation algorithms".
- **Exact contribution**: (a) shows Bochmann's construction can be a factor of ~2 off optimal ($2n-1$ passes where $n$ suffice); (b) proves **constructing an optimal (minimum-pass) evaluation order is NP-complete**; (c) gives a new characterisation of pass-evaluable AGs usable as an efficient membership test; (d) gives a polynomial-time construction for a practically important subclass. Reference [19] of the paper is Tarjan 1972, "Depth-first search and linear graph algorithms" -- i.e. Rahia and Ukkonen were already using Tarjan's algorithm in this setting.
- **What it does NOT do**: does not address circular AGs; does not address per-instance pass numbers; does not address attribute values affecting tree size.
- **Relevance to AuxFlow**: Two things. First, if AuxFlow claims its build plan is *minimal* in the number of passes, that claim runs into an NP-completeness result. AuxFlow's monotone-fixpoint pass numbering is the cheap, possibly-suboptimal construction whose suboptimality this paper quantifies. Second, Tarjan-based SCC machinery in the pass-assignment setting is 1980s standard, not novel.
- **Anticipation verdict**: **FULL ANTICIPATION** of the optimality/complexity question for multi-pass scheduling. AuxFlow may not claim minimality without either proving its restricted setting is easier or citing this.
- **Evidence label**: SOURCED.

### A4. Alblas 1981 -- simple versus pure multi-pass, and source-level blame

- **Citation**: Henk Alblas. "A characterization of attribute evaluation in passes". *Acta Informatica*, Volume 16, Issue 4, pages 427-464, December 1981. Springer-Verlag. Author affiliation: Department of Applied Mathematics, Twente University of Technology, Enschede, The Netherlands.
- **DOI / URL**: 10.1007/BF00264495 -- <https://doi.org/10.1007/BF00264495>. **DOI verified.** Volume 16, issue 4, pages 427-464 all confirmed against Springer `citation_*` metadata.
- **Access**: Full metadata and complete abstract read from the Springer landing page; part of the reference list exposed in page metadata. Full text paywalled and NOT read.
- **Verbatim quote** (abstract, complete):
  > "This paper describes the evaluation of semantic attributes in a bounded number of passes from left-to-right and/or from right-to-left over the derivation tree of a program. Evaluation strategies where different instances of the same attribute in any derivation tree are restricted to be evaluated in one pass, with for every derivation tree the same pass number, are referred to as simple multi-pass whereas the unrestricted pass-oriented strategies are referred to as pure multi-pass. A graph theoretic characterization is given, showing in which cases an attribute grammar meets the simple multi-pass requirements and what are the minimal pass numbers of its attributes for a given sequence of pass directions. For the special cases where only left-to-right passes are made or where left-to-right and right-to-left passes strictly alternate, new algorithms are developed that associate minimal pass numbers with attributes and indicate in case of failure the attributes that cause the rejection of the grammar. Mixing of a simple multi-pass strategy with other evaluation strategies, in case the grammar is not simple multi-pass, is discussed."
- **Exact contribution**: (a) **coins and separates the terms `simple multi-pass` (one pass number per attribute, uniform over all instances and all trees) and `pure multi-pass` (unrestricted; instances of the same attribute may land in different passes)**; (b) a graph-theoretic characterisation of simple multi-pass membership and of the minimal pass numbers for a given sequence of pass directions; (c) algorithms that assign minimal pass numbers, for the left-to-right-only case and for the strictly alternating LR/RL case; (d) **on failure, the algorithms "indicate ... the attributes that cause the rejection of the grammar"** -- i.e. source-level blame attribution naming the offending attributes; (e) discussion of falling back to a mixed strategy when the grammar is not simple multi-pass.
- **What it does NOT do**: does not give a decision procedure for pure multi-pass (that is Engelfriet and File 1981); does not handle cycles; does not consider attribute values affecting the amount of tree.
- **Relevance to AuxFlow**: Directly anticipates two AuxFlow features. (1) The `simple`/`pure` distinction *is* AuxFlow's kind-level-versus-instance-level distinction, named and analysed in 1981. AuxFlow's "nodes are individual auxiliary fact instances, not fact kinds" is the pure multi-pass setting. (2) AuxFlow's "source-level diagnosis naming the offending facts" is exactly Alblas's "indicate in case of failure the attributes that cause the rejection of the grammar".
- **Anticipation verdict**: **FULL ANTICIPATION** of (i) the instance-level versus kind-level pass-numbering distinction and (ii) failure diagnostics that name the offending attributes.
- **Evidence label**: SOURCED.

### A5. Engelfriet and File 1981 -- pure multi-pass is inherently exponential

- **Citation**: Joost Engelfriet, Gilberto File. "Passes and paths of attribute grammars". *Information and Control*, Volume 49, Issue 2, pages 125-169, 1981.
- **DOI / URL**: 10.1016/S0019-9958(81)90466-6 -- <https://doi.org/10.1016/S0019-9958(81)90466-6>
- **Access**: Publisher abstract retrieved verbatim via the Semantic Scholar graph API (which returns the publisher-supplied abstract). Full text NOT read; ScienceDirect returned HTTP 403. Bibliographic fields cross-confirmed against CrossRef and against Alblas's 1991 reference list ("*Information and Control* **49** (1981), pp. 125-169").
  Note: the Semantic Scholar record renders the title as "Passes and Paths of Attributive Grammars"; CrossRef, and Alblas's own reference list, both give "attribute grammars". Treat "attribute" as correct.
- **Verbatim quote** (abstract, as returned; the API truncated the final sentence with an ellipsis):
  > "An attribute grammar is pure (left-to-right) multi-pass if a bounded number of left-to-right passes over the derivation tree suffice to compute all its attributes. There is no requirement, as for the usual multi-pass attribute grammars, that all occurrences of the same attribute are computed in the same pass. It is shown that the problem of determining whether an arbitrary attribute grammar is pure multipass, is of inherently exponential time complexity. For fixed k > 0, it can be decided in polynomial time whether an attribute grammar is pure k-pass. The proofs are based on a characterization of pure multi-pass attribute grammars in terms of paths through their dependency graphs. A general result on dependency paths of attribute grammars relates the..."
- **Exact contribution**: (a) defines pure multi-pass and states explicitly that it drops the requirement "that all occurrences of the same attribute are computed in the same pass"; (b) **proves that deciding whether an arbitrary AG is pure multi-pass has inherently exponential time complexity**; (c) proves that for each *fixed* k, deciding pure k-pass is polynomial-time; (d) achieves this via a characterisation in terms of *paths* through the dependency graphs.
- **What it does NOT do**: does not treat cycles, fixpoints, or content generation; the complexity result is about the grammar-level decision problem, not about any single input tree.
- **Relevance to AuxFlow**: **This is the paper that prices AuxFlow's central design choice.** AuxFlow's move from fact *kinds* to fact *instances* is precisely the move from simple multi-pass to pure multi-pass. That move is (i) already named, (ii) already characterised via dependency-graph paths -- the same technique AuxFlow uses -- and (iii) already known to be inherently exponential in general, while polynomial for any fixed pass bound k. If AuxFlow's per-fact pass propagation is polynomial, then either AuxFlow's LaTeX subset is a restricted class in which the general lower bound does not apply (which needs an argument), or AuxFlow is computing a conservative approximation (which needs saying), or AuxFlow is effectively answering the fixed-k question rather than the unbounded one.
- **Anticipation verdict**: **FULL ANTICIPATION** of the instance-level ("pure") multi-pass property, of its dependency-path characterisation, and of its complexity.
- **Evidence label**: SOURCED (abstract). The truncated tail of the abstract and the body are UNVERIFIED.

### A6. Engelfriet and File 1982 -- the complete complexity taxonomy of pass and visit classes

- **Citation**: Joost Engelfriet, Gilberto File. "Simple Multi-Visit Attribute Grammars". *Journal of Computer and System Sciences*, Volume 24, Issue 3, pages 283-314, 1982. Received 30 October 1980. Department of Applied Mathematics, Twente University of Technology, 7500 AE Enschede, The Netherlands.
- **DOI / URL**: 10.1016/0022-0000(82)90030-7 -- <https://doi.org/10.1016/0022-0000(82)90030-7>. Open-access copy: <https://ris.utwente.nl/ws/files/6563081/Engelfriet82simple.pdf>
- **Access**: **Full text read** (open access, University of Twente institutional repository).
- **Verbatim quote 1** (page 284, the complexity taxonomy -- the single most useful paragraph in this area):
  > "Concerning the complexity of deciding these properties of AG the following can be said: The pure multi-pass property is exponential-time complete [5]. The simple multi-pass property is decidable in polynomial time by the algorithm in [2]. The pure multi-visit property is exponential-time complete, because it coincides with the property of noncircularity [7]; in fact, for every noncircular AG there is a tree-walking evaluator which makes a bounded number of visits to any node of a derivation tree. Finally, as previously said, we shall prove in this paper that the simple multi-visit property is NP-complete, even if the number of visits is restricted to two (the one-visit property can be decided in polynomial time)."
  ([5] = Engelfriet and File, Information and Control 1981; [2] = Bochmann 1976; [7] = Jazayeri, Ogden and Rounds.)
- **Verbatim quote 2** (page 288, the definitions):
  > "An AG G is pure m-pass, m > 0, iff for each complete derivation tree t of G m (left-to-right) passes over t are sufficient to evaluate all its attributes.
  > An AG G is simple m-pass, m > 0, iff there exists, for each nonterminal F of G, a partition A_1(F),...,A_m(F) of the set of attributes A(F) such that for any complete derivation tree t of G all the attributes of t can be evaluated in m (left-to-right) passes over t and in the jth pass all and only the attributes in A_j(F) are computed, j in [1, m].
  > Clearly an AG G is pure (simple) multi-pass iff it is pure (simple) m-pass for some m > 0. **Note that the class of simple multi-pass AG is that actually considered in [2].**"
  (Emphasis added. [2] = Bochmann 1976. This sentence is what pins Bochmann's algorithm to the *simple* class.)
- **Verbatim quote 3** (page 284, on the origin of the terminology):
  > "The adjective simple was added by Alblas [1] to stress the fact that each attribute of a nonterminal has a fixed pass-number. This provided us with another motivation to introduce the simple multi-visit AG, in which each attribute has a fixed visit-number. Dropping the restriction of a fixed pass- (or visit-) number for each attribute, but keeping the bounds on the number of passes (or visits), the larger classes of pure multi-pass AG [1] and pure multi-visit AG are obtained."
- **Exact contribution**: (a) defines simple multi-visit AGs; (b) proves simple multi-visit is equivalent to Kastens's 1-ordered AGs; (c) proves every noncircular AG can be transformed into an equivalent simple multi-visit AG using the same semantic operations; (d) proves that for a *given* distribution of visit numbers, checking evaluability is polynomial (by acyclicity checks on constructed graphs), while deciding simple multi-visit membership is **NP-complete**, even for two visits; (e) assembles the four-way complexity taxonomy quoted above; (f) introduces "Bochmann normal form" as a standing assumption.
- **What it does NOT do**: no cycles, no fixpoints, no content generation. Explicitly presupposes non-circularity throughout.
- **Relevance to AuxFlow**: (1) It is the authoritative source for the claim that "static multipass / pass-number analysis is decades-old prior art", far more precise than a bare citation to Bochmann. (2) It gives AuxFlow the vocabulary it needs to state its actual position honestly: AuxFlow does pure (instance-level) pass numbering, which is the EXPTIME-complete class, on a restricted domain. (3) The "given a candidate assignment, check for cycles in constructed graphs, polynomial" pattern is exactly AuxFlow's verification step.
- **Anticipation verdict**: **FULL ANTICIPATION** of the taxonomy and complexity landscape that AuxFlow's pass-number component lives in.
- **Evidence label**: SOURCED (full text).

### A7. Alblas 1985 -- minimal pass sequences

- **Citation**: Henk Alblas. "Finding Minimal Pass Sequences for Attribute Grammars". *SIAM Journal on Computing*, Volume 14, Issue 4, pages 889-914, 1985.
- **DOI / URL**: 10.1137/0214063 -- <https://doi.org/10.1137/0214063>
- **Access**: **Metadata only.** dblp record read; independently confirmed by Alblas's own 1991 reference list ("*SIAM Journ. on Computing* **14** (1985), pp. 889-914"). SIAM landing page returned a cookie-absent redirect; abstract NOT read.
- **Verbatim quote**: none obtained.
- **Exact contribution**: **UNVERIFIED.** By title, minimisation of pass sequences (including, presumably, the choice of pass *directions*, which Alblas 1981 took as given).
- **What it does NOT do**: unknown.
- **Relevance to AuxFlow**: directly on-topic for any minimality claim about AuxFlow's build plan. AuxFlow should cite it but must not characterise its content without reading it.
- **Anticipation verdict**: PARTIAL OVERLAP (probable; UNVERIFIED).
- **Evidence label**: SOURCED for bibliography; content UNVERIFIED.

### A8. Alblas 1989 -- iterated passes over a tree that is being transformed

- **Citation**: Henk Alblas. "Iteration of transformation passes over attributed program trees". *Acta Informatica*, Volume 27, Issue 1, pages 1-40, November 1989. Springer-Verlag. Department of Computer Science, University of Twente.
- **DOI / URL**: 10.1007/BF00263499 -- <https://doi.org/10.1007/BF00263499>
- **Access**: Full metadata and complete abstract read from the Springer landing page. Full text paywalled and NOT read.
- **Verbatim quote** (abstract, complete):
  > "Transformations of attributed program trees form an essential part of compiler optimizations. A strategy of repeatedly applying alternate attribute evaluation and tree transformation phases is discussed. An attribute evaluation phase consists of a sequence of passes over the tree. A tree transformation phase consists of a single pass, which is never interrupted to carry out a re-evaluation. Both phases can be performed in parallel. This strategy requires a distinction between consistent (i.e., correct) and approximate attribute values. Tree transformations can be considered safe if they guarantee that the attribute values everywhere in the program tree will remain consistent or will become at least approximations of the consistent values, so that subsequent transformations can be applied correctly. **This attribute evaluation and tree transformation strategy shows similarities with the evaluation methods for circular attribute grammars.**"
  (Emphasis added.)
- **Exact contribution**: a strategy of alternating attribute-evaluation phases (each a sequence of passes) with tree-transformation phases, iterated to a stable point; a distinction between *consistent* and *approximate* attribute values; a safety criterion for transformations (they must leave values consistent or at least approximating); an explicit observation that this whole arrangement resembles circular-AG evaluation.
- **What it does NOT do**: does not decide whether the iteration terminates, does not classify which transformations cause divergence, and does not analyse whether transformations *grow* the tree without bound. Safety here is about value correctness, not about termination.
- **Relevance to AuxFlow**: This is AuxFlow's setting almost verbatim, from the compiler-optimisation side rather than the document-typesetting side. Alternating "evaluate attributes in passes" with "change the tree", iterated, with values that are only approximations until the process stabilises, and an explicit link to circular-AG evaluation. AuxFlow's `benign cyclic` case is Alblas's "values converge to consistent"; AuxFlow's `amplifying` case is the case Alblas does not analyse. AuxFlow's framing that "in classical AGs no attribute value alters the shape of the derivation tree, and this is what makes our setting different" is directly weakened by this paper: the AG community was iterating evaluation over a *mutating* tree in 1989.
- **Anticipation verdict**: **PARTIAL OVERLAP**, and dangerous. It anticipates the *setting* (iterated passes over a changing tree, with approximate-then-consistent values, related to circular AGs) but, on the evidence of the abstract, not the *termination decision* AuxFlow claims.
- **Evidence label**: SOURCED (abstract). Body UNVERIFIED, so the "does not decide termination" claim is an INFERENCE from the abstract's silence and should be confirmed before AuxFlow relies on it.

### A9. Kastens 1980 -- ordered attributed grammars

- **Citation**: Uwe Kastens. "Ordered attributed grammars". *Acta Informatica*, Volume 13, Issue 3, pages 229-256, 1980.
- **DOI / URL**: 10.1007/BF00288644 -- <https://doi.org/10.1007/BF00288644>
- **Access**: Metadata only via CrossRef. Cross-confirmed by Alblas 1991 reference [34] and by Swierstra and Vogt 1991 reference [9], both giving "Acta Informatica, 13, pages 229-256, 1980". Abstract NOT read.
- **Verbatim quote**: none from Kastens directly. Engelfriet and File 1982 (SOURCED, full text) characterise the class as follows, page 283:
  > "An attribute grammar (AG) G is ordered if for each nonterminal a linear order of its attributes exists with the property that for every node of a derivation tree of G its attributes can be evaluated in that order. The ordered AG are attractive because (1) they include naturally the multi-pass AG of [2,8], and (2) they have a simple attribute evaluation method."
  And, page 283-284, a caveat worth noting:
  > "In [9] a wrong proof was given to show that it takes polynomial time to decide whether an AG is ordered. To overcome this difficulty the notion of ordered AG was redefined in [10] and called OAG; the class of OAG is a proper subclass of the original class of ordered AG which we shall henceforth call 1-ordered AG. It takes polynomial time to decide whether an attribute grammar is an OAG. In this paper we shall show that to the contrary, deciding whether an AG is 1-ordered, is an NP-complete problem."
  ([9] = Kastens's 1978 Karlsruhe report; [10] = Kastens 1980.)
- **Exact contribution**: introduces ordered / OAG attribute grammars: per-nonterminal linear attribute orders enabling a simple, low-overhead tree-walking evaluator that decides what to do purely from the current visit number. Properly generalises multi-pass AGs. Deciding OAG membership is polynomial; deciding the original 1-ordered property is NP-complete (Engelfriet and File 1982).
- **What it does NOT do**: no cycles, no fixpoints, no content generation, no instance-level numbering.
- **Relevance to AuxFlow**: Background. It matters because it shows the AG community's static-scheduling design space is much richer than "pass numbers", and because a reviewer will expect AuxFlow to know that the standard practical class is OAG, not multi-pass. Orthogonal to AuxFlow's cycle-classification contribution.
- **Anticipation verdict**: INFORMS ONLY.
- **Evidence label**: SOURCED for bibliography and for Engelfriet and File's characterisation; Kastens's own text UNVERIFIED.

### A10. Knuth 1968 and the 1971 correction -- origin of AGs and of the circularity test

- **Citation**: Donald E. Knuth. "Semantics of context-free languages". *Mathematical Systems Theory*, Volume 2, Issue 2, pages 127-145, 1968.
  Donald E. Knuth. "Semantics of context-free languages: Correction". *Mathematical Systems Theory*, Volume 5, Issue 2, pages 95-96, June 1971. Stanford University.
- **DOI / URL**: 10.1007/BF01692511 and 10.1007/BF01702865
- **Access**: CrossRef metadata for both. Springer landing page for the correction read in full (metadata only; a two-page correction has no abstract). The 1968 paper's body was NOT read.
- **Verbatim quote**: none from Knuth. The content is however characterised by two primary sources read in full. Magnusson and Hedin 2007 preprint:
  > "In [19] Knuth developed a polynomial algorithm for circularity testing. The algorithm is conservative, i.e., circularity is always detected but some noncircular AGs may be reported to be circular. Later [20] Knuth constructed an exact algorithm which is exponential in time and space complexity."
  ([19] = Knuth 1968; [20] = Knuth 1971.) Krishnan and Van Wyk 2012:
  > "In Knuth's original work on attribute grammars [8] he gave a circularity analysis. In the attribute grammar community it is not uncommon to extend this analysis when new features are added to the attribute grammar paradigm."
- **Exact contribution**: introduces attribute grammars (synthesized and inherited attributes over a context-free derivation tree). The 1968 paper gives a polynomial but *conservative* circularity test; the 1971 correction replaces it with an exact test that is exponential in time and space.
- **What it does NOT do**: nothing about passes, fixpoints, or tree growth.
- **Relevance to AuxFlow**: the root of the field, and the reason AuxFlow's `UNKNOWN` verdict is respectable: conservative approximation of circularity has been the norm since 1968. Also the correct precedent for AuxFlow admitting a conservative analysis rather than claiming completeness.
- **Anticipation verdict**: INFORMS ONLY (foundational).
- **Evidence label**: SOURCED for bibliography (with the issue-number correction below); content SOURCED via two citing primary sources.
- **Bibliographic warning**: Springer's authoritative metadata for the correction gives **volume 5, issue 2, pages 95-96**. Secondary citations overwhelmingly say 5(1) -- including Krishnan and Van Wyk 2012, Soderberg and Hedin 2013, Swierstra and Vogt 1991, and Magnusson and Hedin's reference list. AuxFlow should use 5(2) and cite the DOI.

### A11. Jazayeri, Ogden and Rounds 1975 -- circularity is intrinsically exponential

- **Citation**: Mehdi Jazayeri, William F. Ogden, William C. Rounds. "The Intrinsically Exponential Complexity of the Circularity Problem for Attribute Grammars". *Communications of the ACM*, Volume 18, Issue 12, pages 697-706, December 1975.
  Conference version: same authors, "On the Complexity of the Circularity Test for Attribute Grammars", *Conference Record of the 2nd ACM Symposium on Principles of Programming Languages (POPL 1975)*, Palo Alto, California, January 20-22 1975, pages 119-129.
- **DOI / URL**: CACM: 10.1145/361227.361231. POPL: 10.1145/512976.512989 (marked open access by dblp).
- **Access**: dblp metadata for both, plus the POPL version's full citation as it appears verbatim in Bochmann 1976's own reference [18] (read from the ACM landing page): "Jazayeri, M., Ogden, W.F., and Rounds, W.C. On the Complexity of the circularity test for attribute grammars. In Conf. Record, ACM Symp. on Principles of Programming Languages, Palo Alto, Calif., Jan. 20-22, 1975, pp. 119-129." Abstracts NOT read.
- **Verbatim quote**: none from the papers. Engelfriet and File 1982 (SOURCED, full text) uses the result thus, page 284: "The pure multi-visit property is exponential-time complete, because it coincides with the property of noncircularity [7]" ([7] = Jazayeri/Ogden/Rounds).
- **Exact contribution**: the circularity problem for AGs requires exponential time -- not merely that Knuth's algorithm is exponential, but that no algorithm can avoid it. Sharpened later: Jazayeri, JACM 28(4):715-720, 1981, DOI 10.1145/322276.322283 gives a simpler construction; Dill, JACM 36(1):92-96, 1989, DOI 10.1145/58562.77393 gives a counter-example to that construction; Engelfriet, SIGACT News 20(3):57-59, 1989, DOI 10.1145/70642.70645 comments on the counter-example; **Wu closes the question by proving EXPTIME-completeness** (A12).
- **What it does NOT do**: says nothing about whether a *given* cycle converges, and nothing about tree growth. Circularity existence, not circularity behaviour.
- **Relevance to AuxFlow**: sets the complexity floor for AuxFlow's SCC-detection step *in the general AG setting*. AuxFlow works on an instance-level graph for one concrete document, where SCC finding is linear (Tarjan). The exponential result is about the grammar-level, all-trees question. AuxFlow should state which of the two it is answering; conflating them would be a serious error in either direction.
- **Anticipation verdict**: INFORMS ONLY (bounds the general problem; AuxFlow's per-document instance graph is a different, easier question).
- **Evidence label**: SOURCED for bibliography; the content statement is SOURCED via Engelfriet and File 1982.

### A12. Wu 2000/2004 -- circularity is EXPTIME-complete

- **Citation**: Pei-Chi Wu. "On exponential-time completeness of the circularity problem for attribute grammars". *ACM Transactions on Programming Languages and Systems*, Volume 26, Issue 1, pages 186-190, 2004. DOI 10.1145/963778.963783.
  Preprint: Pei-Chi Wu, "On Exponential-Time Completeness of the Circularity Problem for Attribute Grammars", arXiv cs/0010015, 10 October 2000.
- **DOI / URL**: 10.1145/963778.963783 -- <https://doi.org/10.1145/963778.963783>. Open preprint: <https://arxiv.org/abs/cs/0010015>
- **Access**: arXiv abstract read verbatim. TOPLAS version metadata via dblp; TOPLAS full text NOT read.
- **Verbatim quote** (arXiv abstract, complete):
  > "Attribute grammars (AGs) are a formal technique for defining semantics of programming languages. Existing complexity proofs on the circularity problem of AGs are based on automata theory, such as writing pushdown acceptor and alternating Turing machines. They reduced the acceptance problems of above automata, which are exponential-time (EXPTIME) complete, to the AG circularity problem. These proofs thus show that the circularity problem is EXPTIME-hard, at least as hard as the most difficult problems in EXPTIME. However, none has given a proof for the EXPTIME-completeness of the problem. This paper first presents an alternating Turing machine for the circularity problem. The alternating Turing machine requires polynomial space. Thus, the circularity problem is in EXPTIME and is then EXPTIME-complete."
- **Exact contribution**: shows the AG circularity problem is *in* EXPTIME (via a polynomial-space alternating Turing machine), completing the EXPTIME-completeness result that prior work had left at EXPTIME-hard.
- **What it does NOT do**: nothing about convergence, fixpoints, or generation.
- **Relevance to AuxFlow**: if AuxFlow states the complexity of grammar-level circularity testing, the correct modern statement is "EXPTIME-complete (Jazayeri/Ogden/Rounds 1975 for hardness; Wu 2004 for membership)", not "exponential".
- **Anticipation verdict**: INFORMS ONLY.
- **Evidence label**: SOURCED (arXiv abstract).

### A13. Rodeh and Sagiv 1999, and Sagiv et al. 1989 -- finding the circular attributes, and resolving circularity

- **Citation**: Michael Rodeh, Mooly Sagiv. "Finding circular attributes in attribute grammars". *Journal of the ACM*, Volume 46, Issue 4, pages 556-575, 1999. DOI 10.1145/320211.320243.
  Shmuel Sagiv, Orit Edelstein, Nissim Francez, Michael Rodeh. "Resolving Circularity in Attribute Grammars with Applications to Data Flow Analysis". *POPL 1989*, pages 36-48. DOI 10.1145/75277.75281 (marked open access by dblp).
- **DOI / URL**: as above.
- **Access**: dblp and CrossRef metadata. Abstracts NOT read. The Rodeh and Sagiv result is however characterised by a primary source read in full -- Magnusson and Hedin 2007 preprint:
  > "Rodeh & Sagiv [25] extended these algorithms to deal with the problem of finding the attributes taking part in cycles. They developed a polynomial approximation algorithm, i.e., all circular attributes are discovered but some noncircular attributes may be reported to be circular. They also constructed an exact algorithm with exponential time complexity and showed that finding the circular attributes is a harder problem than testing for circularity."
- **Exact contribution** (Rodeh and Sagiv): moves from "is the grammar circular?" to "**which attributes are on cycles?**"; gives a polynomial conservative approximation (complete but not sound: all circular attributes found, some non-circular ones falsely flagged) and an exact exponential algorithm; **proves that finding the circular attributes is strictly harder than testing for circularity**.
  (Sagiv et al. 1989): resolving circularity in AGs, applied to data-flow analysis. Content UNVERIFIED.
- **What it does NOT do**: does not classify a found cycle as convergent or divergent.
- **Relevance to AuxFlow**: **This is the closest prior art to AuxFlow's "source-level diagnosis naming the offending facts".** AuxFlow does not merely detect that a document is cyclic; it names the facts responsible. That is the Rodeh and Sagiv problem, and it is known to be harder than circularity detection, with a known polynomial conservative approximation. AuxFlow's diagnosis component is therefore in a well-studied place, and if AuxFlow's diagnosis is exact and polynomial, that needs a restriction argument.
- **Anticipation verdict**: **PARTIAL OVERLAP**, strongly. Anticipates "identify the attributes/facts on the cycle, conservatively, in polynomial time".
- **Evidence label**: SOURCED for bibliography; Rodeh and Sagiv's content SOURCED via Magnusson and Hedin's primary text; Sagiv et al. 1989 content UNVERIFIED.

### A14. Farrow 1986 -- automatic fixpoint-finding evaluators for circular AGs

- **Citation**: Rodney Farrow. "Automatic generation of fixed-point-finding evaluators for circular, but well-defined, attribute grammars". *Proceedings of the 1986 SIGPLAN Symposium on Compiler Construction*, Palo Alto, California, pages 85-98. Also ACM SIGPLAN Notices 21(7):85-98, 1986.
- **DOI / URL**: 10.1145/12276.13320 (proceedings), 10.1145/13310.13320 (SIGPLAN Notices).
- **Access**: CrossRef metadata for both DOIs; cross-confirmed by Alblas 1991 reference [21], Magnusson and Hedin reference [9], and Soderberg and Hedin reference [13], all giving pages 85-98. Abstract and full text NOT read.
- **Verbatim quote**: none from Farrow. Characterised by Magnusson and Hedin 2007 (SOURCED, full text):
  > "Farrow [9] introduced a static evaluation technique based on the one by Katayama [18], but modified to compute the fixed point for attributes which potentially have circular dependencies. His scheme is also limited to traditional AGs without remote references since it depends on deriving the attribute dependencies statically from the productions of the grammar."
  And, on the residual gap:
  > "Our evaluator presently does not check whether circularly defined attributes take their values from a lattice of finite height or if their defining semantic functions are monotonic. Thus there is no guarantee that iterations will converge. **Our approach is in this respect similar to that of, e.g., Farrow [9]** and means that we rely on the AG author to ensure that the semantic functions involved are properly constrained."
  (Emphasis added.)
- **Exact contribution**: **the first automatic generator of fixpoint-finding evaluators for circular-but-well-defined AGs**, statically derived from the grammar productions. Potentially-circular attributes are identified by static analysis of the grammar; the generated evaluator iterates those to a fixed point.
- **What it does NOT do**: does not verify the well-definedness precondition. Termination is assumed, not decided -- the grammar author is trusted to supply a finite-height lattice and monotone functions.
- **Relevance to AuxFlow**: (1) Static identification of potentially-circular attributes from the grammar alone is Farrow 1986. (2) Farrow is the standing precedent for "we compute a fixpoint and trust that it converges", which is what a `BENIGN_CYCLIC` verdict amounts to if AuxFlow's benignity test is not itself a proof of convergence. (3) The gap Farrow leaves open -- nobody checks the convergence precondition -- is precisely the gap AuxFlow would have to fill to claim novelty here.
- **Anticipation verdict**: **FULL ANTICIPATION** of static detection of potentially-circular attributes plus generated fixpoint evaluation. AuxFlow's remaining room is in *deciding* convergence, not in performing it.
- **Evidence label**: SOURCED for bibliography; content SOURCED via Magnusson and Hedin's primary text; Farrow's own text UNVERIFIED.

### A15. Jones 1990 -- SCC condensation plus topological order plus fixpoint per component

- **Citation**: Larry G. Jones. "Efficient evaluation of circular attribute grammars". *ACM Transactions on Programming Languages and Systems*, Volume 12, Issue 3, pages 429-462, 1990.
- **DOI / URL**: 10.1145/78969.78971 -- <https://doi.org/10.1145/78969.78971>
- **Access**: CrossRef and dblp metadata. Cross-confirmed by Magnusson and Hedin reference [15] and Soderberg and Hedin reference [15]. Semantic Scholar reports the abstract as elided by the publisher; ACM DL returned cookie-absent. Abstract and full text NOT read.
- **Verbatim quote**: none from Jones. Characterised in detail by Magnusson and Hedin 2007 (SOURCED, full text):
  > "Jones [15] proposes a dynamic evaluation algorithm derived from the underlying attribute dependency graph. **Optimal dynamic evaluation for circular AGs is obtained by analyzing the dependency graph dynamically to identify its strongly connected components.** A strongly connected component is a maximal set of vertices in which there is a path from any one vertex in the set to any other vertex in the set. All attribute instances belonging to the same strongly connected component are thus dependent of each other. **Each strongly connected component is contracted into a single node to obtain a new graph C(G), which is acyclic and can be ordered topologically and evaluation can follow this order.** A vertex in C(G) corresponding to more than one vertex in the original graph represents a set of attribute instances that are all dependent of each other and they will be evaluated in a single fixed-point evaluation. The graphs must be constructed initially. When the attribute grammar is acyclic, Jones' algorithm reduces to a standard optimal algorithm for noncircular evaluation."
  (Emphasis added.) And later: "the dynamic algorithm of Jones [15] is optimal. Jones algorithm computes the strongly connected components for a given AST before evaluation, based on the actual attribute dependencies."
- **Exact contribution**: builds the **instance-level** attribute dependency graph for a given tree, finds its SCCs, condenses them, topologically orders the condensation, and evaluates component by component -- each multi-vertex component by a single fixpoint iteration. Reduces to the standard optimal non-circular algorithm when there are no cycles. Shown optimal.
- **What it does NOT do**: does not decide whether a component's fixpoint iteration terminates; does not classify components; does not handle reference attributes (dependencies unknown until evaluation) or tree growth.
- **Relevance to AuxFlow**: **This is the most direct architectural anticipation of AuxFlow's pipeline.** "Build an instance-level dependency graph, find SCCs (Tarjan), condense, order topologically, fixpoint each non-trivial component" is Jones 1990, and it is instance-level, exactly as AuxFlow is. AuxFlow's graph-construction, SCC and fixpoint steps are a re-derivation. What Jones does *not* do -- decide whether a component converges, and classify components by whether their values influence how much content exists -- is the only place AuxFlow's architecture has room.
- **Anticipation verdict**: **FULL ANTICIPATION** of AuxFlow's instance-graph + Tarjan-SCC + condensation + per-component fixpoint architecture.
- **Evidence label**: SOURCED for bibliography; content SOURCED via Magnusson and Hedin's primary text (a detailed, technical, first-hand description in a peer-reviewed journal paper); Jones's own text UNVERIFIED.

### A16. Magnusson and Hedin 2007 -- circular RAGs, and the exact convergence condition

- **Citation**: Eva Magnusson, Gorel Hedin. "Circular reference attributed grammars -- their evaluation and applications". *Science of Computer Programming*, Volume 68, Issue 1, pages 21-37, August 2007. Dept of Computer Science, Lund University.
  Earlier version: same authors, same title, LDTA at ETAPS 2003, Electronic Notes in Theoretical Computer Science, pages 532-554, DOI 10.1016/S1571-0661(05)82627-1.
- **DOI / URL**: 10.1016/j.scico.2005.06.005 -- <https://doi.org/10.1016/j.scico.2005.06.005>. **DOI verified via CrossRef.** Volume 68, issue 1, pages 21-37 verified via dblp. Author preprint (open): <https://fileadmin.cs.lth.se/sde/publications/papers/2007-MagnussonEva-CRAGs-SCP-Preprint.pdf>
- **Access**: **Full author preprint read** (dated "Preprint submitted to Elsevier Preprint 4 August 2004"; content corresponds to the LDTA/SCP paper). The final Elsevier version was NOT read; page-level citation to the published version should be checked before quoting page numbers.
- **Verbatim quote 1** (the exact termination condition, section 1):
  > "The traditional AG requirement of non circularity is a sufficient but not necessary condition to guarantee that an AG is well defined in the sense that all semantic rules can be satisfied. It suffices that all attributes involved in cyclic dependencies have a fixed point that can be computed with a finite number of iterations. In CAGs, circular dependencies between attributes are allowed provided that such a fixed point is available for all possible trees. **This is guaranteed if the values for each attribute on a cycle can be organized in a lattice of finite height and if all the semantic functions involved in computing these attributes are monotonic on the respective lattices.**"
  (Emphasis added.)
- **Verbatim quote 2** (footnote 3, the weaker sufficient condition):
  > "More precisely it is sufficient that the domain of the attributes forms a complete partial order and that the semantic functions satisfy the ascending chain condition."
- **Verbatim quote 3** (section 2.2, the iteration):
  > "The evaluation of circularly defined attributes can be regarded as a special case of solving the equation X = f(X) for the value of X. By giving X the bottom of the lattice as start value the iterative process X_{i+1} = f(X_i) will converge to a least fixed point for which all involved semantic rules are satisfied."
- **Verbatim quote 4** (section 3.5, the crucial admission):
  > "**Our evaluator presently does not check whether circularly defined attributes take their values from a lattice of finite height or if their defining semantic functions are monotonic. Thus there is no guarantee that iterations will converge.** Our approach is in this respect similar to that of, e.g., Farrow [9] and means that we rely on the AG author to ensure that the semantic functions involved are properly constrained."
  (Emphasis added.)
- **Verbatim quote 5** (section 3.4, error detection when a cycle is not declared):
  > "Using the information about which attributes are declared circular, it is possible to keep track of which nodes in the dependency graph might belong to the same strongly connected component. If a visited node belonging to another component is encountered, then an error has ocurred. ... Thus, in case of a missing circular declaration, the algorithm will detect the error, identify the attributes involved, and raise an exception."
- **Verbatim quote 6** (section 4.2, on cases with no fixpoint at all):
  > "Should some constants be part of circular definitions like in the example above, this is a programming error that should be caught by the compiler. **To use circular attributes is not an option here since there does not, in general, exist any fixed-point solution.**"
- **Exact contribution**: combines Reference AGs (attributes may be references to arbitrarily distant nodes) with Circular AGs (fixpoint-evaluated cyclic attributes) into CRAGs; gives a demand-driven recursive evaluator with `IN_CIRCLE` / `CHANGE` / `READY` global state; optimises it to avoid nested iterations, avoid re-iterating definitely-non-circular attributes, evaluate SCCs in topological order where detectable, and skip iteration for actually-non-circular instances; adds a *robust* variant that detects a missing `circular` declaration by tracking SCC membership and raises an error naming the involved attributes; implemented in JastAdd; evaluated on grammars up to Java 1.2 against hand-coded iterative code (comparable, and faster on the large grammar). Applications: nullable/first/follow, constants-used-before-declaration, live-variable analysis. Also introduces the distinction `definitely noncircular` / `potentially circular` / `actually circular`.
- **What it does NOT do**: **does not decide convergence.** It states the sufficient condition (finite-height lattice + monotone functions; or CPO + ascending chain condition) and then explicitly declines to check it, delegating to the grammar author. It also does not handle attribute values that generate new tree material -- that is Soderberg and Hedin 2013 (A19).
- **Relevance to AuxFlow**: (1) **This is the exact condition AuxFlow's benign/amplifying distinction is a domain-specific instance of.** A table of contents shifting page numbers is monotone over a finite-height lattice; a page reference bounding a content-generating loop breaks the finite-height assumption because the value domain grows with the content. AuxFlow should state its classification in these terms, because the AG community will read it that way. (2) The `definitely noncircular` / `potentially circular` / `actually circular` trichotomy maps onto AuxFlow's `CERTIFIED` / `UNKNOWN` / `BENIGN_CYCLIC` verdicts. (3) The "identify the attributes involved and raise an exception" behaviour anticipates AuxFlow's source-level diagnosis. (4) Quote 4 is the honest statement of the open problem, and it is 2007: nobody in this line checks the convergence precondition. That is the one place where AuxFlow could legitimately claim to be doing something new -- and A20 shows even that ground is partly taken.
- **Anticipation verdict**: **PARTIAL OVERLAP**, decisive on the framing. Fully anticipates the fixpoint-over-SCCs machinery and the convergence *criterion*; does not anticipate a decision procedure for it.
- **Evidence label**: SOURCED (full author preprint).

### A17. Vogt, Swierstra and Kuiper 1989, and Swierstra and Vogt 1991 -- higher-order AGs: attribute values ARE tree

- **Citation**: Harald H. Vogt, S. Doaitse Swierstra, Matthijs F. Kuiper. "Higher order attribute grammars". *Proceedings of the ACM SIGPLAN 1989 Conference on Programming Language Design and Implementation (PLDI '89)*, Portland, Oregon, June 1989, pages 131-145. Also ACM SIGPLAN Notices 24(7):131-145, June 1989.
  Tutorial/extended version: Doaitse Swierstra, Harald Vogt. "Higher Order Attribute Grammars". In H. Alblas and B. Melichar (eds.), *Attribute Grammars, Applications and Systems*, International Summer School SAGA, Prague, June 4-13 1991, Lecture Notes in Computer Science 545, Springer, pages 256-296.
- **DOI / URL**: PLDI proceedings: 10.1145/73141.74830. SIGPLAN Notices: 10.1145/74818.74830. SAGA chapter: 10.1007/3-540-54572-7_10.
- **Access**: **SAGA 1991 chapter: full abstract and complete 25-item reference list read from the Springer landing page.** PLDI 1989 paper: bibliographic metadata verified via CrossRef under both DOIs and corroborated by the reference lists of Swierstra and Vogt 1991, Soderberg and Hedin 2013, and Krishnan and Van Wyk 2012, all giving pages 131-145. **The PLDI paper's own text was NOT read** -- ACM DL blocked (cookie-absent, then a Cloudflare interstitial that did not clear).
- **Verbatim quote 1** (SAGA 1991 abstract, complete -- and this is the decisive quote for AuxFlow):
  > "**Higher Order Attribute Grammars (HAGs) are an extension of normal attribute grammars in the sense that the distinction between the domain of parse-trees and the domain of attributes has disappeared: parse trees may be computed in attributes and grafted to the parse tree at various places.** As a result semantic functions may be described by attribute evaluation.
  > We will present the basic definitions for HAGs, and compare them with attribute coupled grammars, extended affix grammars and functional programming languages. We will indicate how multi-pass compilers and a compiler for supercombinators can be described this way.
  > It will be shown that, especially in the case of incremental evaluation, the conventional execution model has to be generalised. Such a model, based on function caching, hash-consing and combinator construction will be discussed."
  (Emphasis added.)
- **Verbatim quote 2** (Krishnan and Van Wyk 2012, SOURCED full text, on what the 1989 paper contains):
  > "In 1989 Vogt et al. introduced higher-order attribute grammars (HOAGs) [17] in which syntax trees can be computed and passed around a syntax tree as attribute values. These trees may also be decorated with attributes which are then evaluated. ... According to Vogt et al., a well-defined higher-order attribute grammar is one that: is complete so that every synthesized, inherited and local instance on a node has a definition; is non-circular so that no attribute value depends on itself, either directly or indirectly; **and has a finite number of new trees created during attribute evaluation.** For the first two conditions, Vogt et al. specify extended versions of Knuth's tests for completeness and circularity, which prevents abnormal termination of attribute evaluation. **But unlike with attribute grammars without higher-order attributes, attribute evaluation for a complete, non-circular HOAG may not terminate since creating an unbounded number of trees during higher-order attribute evaluation can lead to non-termination.** For example, Fig. 1 gives a grammar (borrowed from [17]) for which an infinite number of trees may be created. This explains why Vogt et al. included the third condition in their definition of well-definedness."
  (Emphasis added.)
- **Verbatim quote 3** (Krishnan and Van Wyk 2012, related work, on the 1989 paper's termination lemma):
  > "In Vogt et al.'s original paper on HOAGs they define 'well-definedness' to include termination of tree construction and state a lemma [17, **Lemma 3.2, page 142**] that imposes a condition that would ensure termination of tree construction. This condition requires that non-terminal attributes (the terminology used for higher-order attributes) do not appear more than once in a path in their formulation of trees. This is similar to our imposition of an ordering on non-terminals for higher-order inherited attributes. But our use of rewrite rules for local and synthesized higher order attributes is less restricting and allows for a more precise analysis. In other work [16] they drop this termination requirement for grammars to be considered 'well-defined'."
  (Emphasis added. [16] = Vogt's 1989 Utrecht PhD thesis.)
- **Exact contribution**: introduces higher-order attribute grammars, in which **the parse-tree domain and the attribute domain are the same domain**: attributes may hold trees, and those trees are grafted into the tree and then themselves attributed. Extends Knuth's completeness and circularity tests to this setting. Defines well-definedness to include a *third* condition -- finitely many new trees created during evaluation -- and states a sufficient condition for it (Lemma 3.2, page 142): non-terminal attributes must not appear more than once along a path.
- **What it does NOT do**: per Krishnan and Van Wyk, the Lemma 3.2 condition "does not seem to have been implemented or evaluated", and Vogt's thesis subsequently dropped the termination requirement from well-definedness. So the 1989 paper poses the problem and states a restrictive sufficient condition, but does not deliver a practical, implemented analysis. It also does not classify *why* generation diverges, and does not combine tree generation with circular/fixpoint attributes (that is Soderberg and Hedin 2013).
- **Relevance to AuxFlow**: **This is where AuxFlow's headline framing claim collapses.** AuxFlow asserts that in classical AGs "no attribute value alters the shape of the derivation tree", and that this is what makes AuxFlow's setting different. The first half is true of *Knuth-classical* AGs. The second half is false as a novelty claim: the AG community removed exactly that restriction in 1989, named the resulting formalism, observed that it breaks the termination guarantee that non-circularity used to provide, and made "finitely many trees created" a named well-definedness condition. AuxFlow's "a fact value can bound a loop that generates pages" is a HOAG-style dependency in a typesetting costume.
- **Anticipation verdict**: **FULL ANTICIPATION** of the setting "attribute values determine how much tree there is to attribute" and of the recognition that this destroys the termination guarantee. **PARTIAL** on deciding it: Vogt et al. state a sufficient condition but, on Krishnan and Van Wyk's account, do not implement or evaluate an analysis.
- **Evidence label**: SOURCED for the SAGA 1991 abstract and for both papers' bibliography. The 1989 paper's own text, including Lemma 3.2, is **REPORTED via Krishnan and Van Wyk 2012** -- a peer-reviewed primary source that cites it by lemma number and page, which is strong, but is not the paper itself. **AuxFlow must read the PLDI 1989 paper before making claims about Lemma 3.2.**

### A18. Krishnan and Van Wyk 2012 -- static termination analysis for content-generating attribute evaluation

**This is the single most dangerous piece of prior art in area A.**

- **Citation**: Lijesh Krishnan, Eric Van Wyk. "Termination Analysis for Higher-Order Attribute Grammars". In K. Czarnecki and G. Hedin (eds.), *Software Language Engineering, 5th International Conference (SLE 2012)*, Lecture Notes in Computer Science 7745, Springer, pages 44-63. (CrossRef publication year 2013; conference 2012.) Department of Computer Science and Engineering, University of Minnesota.
- **DOI / URL**: 10.1007/978-3-642-36089-3_4 -- <https://doi.org/10.1007/978-3-642-36089-3_4>. Author copy (open): <https://www-users.cse.umn.edu/~evw/pubs/krishnan12sle/krishnan12sle.pdf>
- **Access**: **Full text read** (author copy at the University of Minnesota).
- **Verbatim quote 1** (abstract, complete):
  > "This paper describes a conservative analysis to detect non-termination in higher-order attribute grammar evaluation caused by the creation of an unbounded number of (finite) trees as local tree-valued attributes, which are then themselves decorated with attributes. **This type of non-termination is not detected by a circularity analysis for higher-order attribute grammars.** The analysis presented here uses term rewrite rules to model the creation of new trees on which attributes will be evaluated. If the rewrite rules terminate then only a finite number of trees will be created. To handle higher-order inherited attributes, the analysis places an ordering on non-terminals to schedule their use and ensure a finite number of passes over the generated trees. When paired with the traditional completeness and circularity analyses and the assumption that each attribute equation defines a terminating computation, this analysis can be used to show that attribute grammar evaluation will terminate normally. This analysis is applicable to a wide range of common attribute grammar idioms and has been used to show that evaluation of our specification of Java 1.4 terminates."
  (Emphasis added.)
- **Verbatim quote 2** (section 1, the separation of the two questions -- this is AuxFlow's cyclic-versus-amplifying distinction):
  > "**Circularity analysis prevents, among other problems, specifications that would cause the construction of infinite syntax trees, but it does not prevent the creation of an infinite number of finite trees**, as seen in the example in Fig. 1. Any analysis to detect the creation of an unbounded number of trees will be conservative; consider the conditional expression in the example. An analysis to guarantee that no evaluation sequences exist with infinitely many tree creation steps, combined with the completeness and circularity tests, would be sufficient to ensure higher-order attribution termination. While Vogt et al. describe a condition required to ensure non-termination, it does not seem to have been implemented or evaluated. **The analysis presented here is the first, to our knowledge, that uses the structure of the equations and not just the attribute dependencies imposed by them in an analysis for termination of tree creation.**"
  (Emphasis added.)
- **Verbatim quote 3** (section 3, reduction to a finite-generation question):
  > "Theorem 1: For a tree in a complete, non-circular grammar with terminating functions, if there is an improper evaluation sequence, then there is an infinite tree creation sequence."
  > "For a complete, non-circular grammar with terminating functions, any evaluation sequence that does not terminate normally contains an infinite number of local tree creation steps. ... As each tree has only a finite number of attribute instances, an infinite number of trees must be created via local creation steps."
- **Verbatim quote 4** (section 5, the SCC-based non-terminal ordering procedure):
  > "Procedure A: 1. Construct a directed graph G_NT whose vertexes correspond to the non-terminals in NT, and with an edge <X, Y> if and only if S(X, Y). 2. Construct a directed graph G_SCC whose vertexes correspond to the strongly connected components (SCC) of G_NT, and with an edge <S_X, S_Y> if and only if there exist X in S_X and Y in S_Y where either I(X, Y), or S(X, Y) and not S(Y, X). 3. If G_SCC has cycles, return failure, the required ordering does not exist. 4. The desired ordering is defined as follows: X >= Y if and only if there is a (possibly trivial) path in G_SCC from X's SCC to Y's SCC."
- **Verbatim quote 5** (section 6, on conservatism and undecidability):
  > "The problem of showing termination, whether for attribute evaluation or term rewriting systems, is undecidable, so our goal is an approximate solution."
  > "The termination analysis is conservative, in that there are terminating grammars for which the analysis fails."
- **Verbatim quote 6** (section 6, on the limit of the technique):
  > "Finally, since the analysis assumes that the grammar is non-circular, it does not handle reference attribute grammars since the circularity problem is undecidable in that setting."
- **Exact contribution**: a conservative *static* analysis that decides whether higher-order attribute evaluation terminates, where the specific failure mode is **evaluation generating an unbounded amount of new content that must itself be evaluated**. Mechanism: (a) prove that in a complete, non-circular grammar with terminating functions, non-termination implies an infinite tree-creation sequence (via the "tree of locals" plus Koenig's Lemma); (b) generate term rewrite rules from the higher-order attribute equations, so that rule termination implies finiteness of tree creation, and discharge rule termination with an off-the-shelf tool (AProVE); (c) handle higher-order *inherited* attributes by constructing a well-founded ordering on non-terminals via SCC condensation of a non-terminal graph (Procedure A above), which bounds the number of inherited tree-creation steps. Implemented in Silver; validated on ableJ, a full attribute grammar for Java 1.4.
- **What it does NOT do**: it is conservative, so it rejects some terminating grammars; it works on a restricted class (RHOAG) and excludes Silver's `case` constructs and same-production-name generation; **it explicitly does not handle reference attribute grammars, because circularity there is undecidable**; and it assumes non-circularity, so it does not combine cyclic fixpoint attributes with content generation (that is Soderberg and Hedin 2013).
- **Relevance to AuxFlow**: This paper occupies AuxFlow's claimed intellectual position almost exactly.

  | AuxFlow component | Krishnan and Van Wyk 2012 |
  |---|---|
  | Values that determine how much content the document generates | Local tree-valued attributes whose values are new trees to be decorated |
  | Circularity is not the whole story; a non-cyclic document can still fail to converge | "This type of non-termination is not detected by a circularity analysis" (verbatim) |
  | Separating benign cyclic from amplifying | Separating circularity analysis from unbounded-tree-creation analysis |
  | Static, conservative, with an `UNKNOWN`/reject verdict | "conservative, in that there are terminating grammars for which the analysis fails" (verbatim) |
  | Tarjan SCC condensation as a scheduling device | Procedure A: SCCs of the non-terminal graph, condensed, checked acyclic, used to build a well-founded order |
  | Evaluated on a real corpus | Evaluated on ableJ, a Java 1.4 attribute grammar |

  The differences that remain are real but narrower than AuxFlow's framing implies: Krishnan and Van Wyk require non-circularity and therefore cannot classify a *cyclic* document as benign-versus-amplifying, which is precisely AuxFlow's headline case; and they use term rewriting plus an external termination prover rather than a taint/influence analysis.
- **Anticipation verdict**: **FULL ANTICIPATION** of (i) the problem "does an evaluation that generates more content to evaluate terminate?", (ii) the framing that this is a *different* question from circularity, (iii) a static conservative analysis answering it, and (iv) SCC-condensation-based ordering as the scheduling device. **PARTIAL** on AuxFlow's specific combination of *cyclic* dependencies with content generation, which they exclude by assumption.
- **Evidence label**: SOURCED (full text).

### A19. Soderberg and Hedin 2013 -- circular AND higher-order together

- **Citation**: Emma Soderberg, Gorel Hedin. "Circular Higher-Order Reference Attribute Grammars". In *Software Language Engineering (SLE 2013)*, Lecture Notes in Computer Science 8225, Springer, Cham, pages 302-321. Department of Computer Science, Lund University.
- **DOI / URL**: 10.1007/978-3-319-02654-1_17 -- <https://doi.org/10.1007/978-3-319-02654-1_17>
- **Access**: Full abstract and complete 27-item reference list read from the Springer landing page. Full text paywalled and NOT read. (The authors advertise supplementary examples at `fileadmin.cs.lth.se/sde/publications/papers/2013-Soderberg-SLE-CircularNTA`, per reference [8] of the paper.)
- **Verbatim quote** (abstract, complete):
  > "Reference attribute grammars (RAGs) provide a practical declarative means to implement programming language compilers and other tools. RAGs have previously been extended to support both circular attributes and context-dependent declarative rewrites of the abstract syntax tree. **In this previous work, dependencies between circular attributes and rewrites are not considered. In this paper, we investigate how these extensions can interact, and still be well defined. We introduce a generalized evaluation algorithm that can handle grammars where circular attributes and rewrites are interdependent. To this end, we introduce circular higher-order attributes, and show how RAG rewrites are a special form of such attributes.**"
  (Emphasis added.)
- **Exact contribution**: identifies exactly the gap AuxFlow occupies -- that circular (fixpoint) attributes and tree rewrites had been studied separately, with their *interdependence* unaddressed -- and closes it with a generalised evaluation algorithm for grammars where circular attributes and rewrites are mutually dependent, via the notion of circular higher-order attributes, showing rewrites to be a special case.
- **What it does NOT do**: on the evidence of the abstract, this is an *evaluation* algorithm and a well-definedness account, not a static classifier that decides in advance whether a given input converges. Whether it also supplies a decision procedure is **UNVERIFIED** (full text not read).
- **Relevance to AuxFlow**: **This is the closest thing in the AG literature to AuxFlow's exact configuration**: cyclic dependencies whose values drive changes to how much tree there is, mutually dependent, with a well-definedness question attached. AuxFlow's assertion that combining cycles with content generation is a new setting is not defensible: Soderberg and Hedin named it in 2013. Their reference list also cites Krishnan and Van Wyk 2012, so the two lines were already in contact.
- **Anticipation verdict**: **FULL ANTICIPATION** of the *setting* (interdependent circular attributes and tree rewrites, and its well-definedness). **UNVERIFIED** whether it anticipates a static up-front classification.
- **Evidence label**: SOURCED (abstract, bibliography). Body UNVERIFIED. **AuxFlow must read this paper in full before claiming any novelty on the cyclic-plus-generating combination.**

### A20. Riouak, Fors, Oqvist, Hedin and Reichenbach 2024 -- static meta-analysis that proves attributes non-circular

- **Citation**: Idriss Riouak, Niklas Fors, Jesper Oqvist, Gorel Hedin, Christoph Reichenbach. "Efficient Demand Evaluation of Fixed-Point Attributes using Static Analysis". *Proceedings of the 17th ACM SIGPLAN International Conference on Software Language Engineering (SLE '24)*, October 20-21 2024, Pasadena, CA, USA. Pages 56-69. ISBN 9798400711800. Distinguished Paper Award and Distinguished Artifact Award, SLE 2024.
- **DOI / URL**: 10.1145/3687997.3695644 -- <https://doi.org/10.1145/3687997.3695644>. Artifact: <https://zenodo.org/records/13365896>
- **Access**: Author-supplied abstract read verbatim from Christoph Reichenbach's own maintained BibTeX bibliography at <https://creichen.net/bibtex.html>. Pages, ISBN, venue and DOI cross-confirmed against CrossRef. **ACM full text NOT read** (Cloudflare block).
- **Verbatim quote** (author-supplied abstract, complete):
  > "Declarative approaches to program analysis promise a number of practical advantages over imperative approaches, from eliminating manual worklist management to increasing modularity. Reference Attribute Grammars (RAGs) are one such approach. One particular advantage of RAGs is the automatic generation of on-demand implementations, suitable for query-based interactive tooling as well as for client analyses that do not require full evaluation of underlying analyses. While historically aimed at compiler frontend construction, the addition of circular (fixed-point) attributes also makes them suitable for dataflow problems. However, prior algorithms for on-demand circular RAG evaluation can be inefficient or even impractical for dataflow analysis of realistic programming languages like Java. We propose a new demand algorithm for attribute evaluation that addresses these weaknesses, and apply it to a number of real-world case studies. **Our algorithm exploits the fact that some attributes can never be circular, and we describe a static meta-analysis that identifies such attributes**, and obtains a median steady-state performance speedup of ~2.5x and ~22x for dead-assignment and null-pointer dereference analyses, respectively."
  (Emphasis added.) Author-supplied keywords, verbatim: "Attribute Grammars, Circular Attributes, Demand Analysis, Fixpoint Computations, Static Analysis".
- **Exact contribution**: a new demand-driven evaluation algorithm for circular RAGs, plus **a static meta-analysis that proves certain attributes can never be circular**, used to skip fixpoint machinery for those. Large measured speedups on real Java dataflow analyses.
- **What it does NOT do**: proves *non*-circularity (AuxFlow's `CERTIFIED` verdict), not convergence of the circular ones. On the abstract's evidence it does not decide whether a fixpoint iteration terminates.
- **Relevance to AuxFlow**: This is 2024, from the JastAdd group, and it is a **static analysis of fixed-point attributes that partitions them by whether they can be circular** -- i.e. exactly AuxFlow's `CERTIFIED` versus `cyclic` split, in the same formal setting, with a published performance evaluation. It shows the field is actively working this exact seam right now. If AuxFlow claims "we statically classify which facts are involved in cycles and which are certified acyclic", this paper has that.
- **Anticipation verdict**: **PARTIAL OVERLAP**, and it is recent and prominent. Anticipates static classification of fixpoint attributes into never-circular versus possibly-circular. Does not appear to anticipate the benign-versus-amplifying split among the possibly-circular ones.
- **Evidence label**: SOURCED for the abstract via the author's own bibliography and for bibliography via CrossRef. Body UNVERIFIED.

### A21. Boyland 2005 -- circularity for remote/reference AGs is undecidable

- **Citation**: John Tang Boyland. "Remote attribute grammars". *Journal of the ACM*, Volume 52, Issue 4, pages 627-687, July 2005.
- **DOI / URL**: 10.1145/1082036.1082042 -- <https://doi.org/10.1145/1082036.1082042>
- **Access**: CrossRef metadata; cross-confirmed by Soderberg and Hedin reference [5] and Krishnan and Van Wyk reference [2], both giving 52(4):627-687. ACM landing page returned HTTP 403; abstract and full text NOT read.
- **Verbatim quote**: none from Boyland. The result is stated by two primary sources I read in full. Magnusson and Hedin 2007 preprint, section 2.1:
  > "In [2] Boyland has defined an extension to traditional AGs called remote attribute grammars, which supports reference attributes like in RAGs and also additional features like collection attributes that can be written from remote locations. **In [5] he shows that testing remote attribute grammars for circularity is undecidable and examines techniques for approximation.**"
  Krishnan and Van Wyk 2012, section 7:
  > "**In the case of reference and remote attributes [6, 2], it is not possible to have a precise circularity analysis, as the problem is undecidable [2].**"
  ([2] = Boyland, JACM 52(4), 2005.)
- **Exact contribution**: defines remote attribute grammars (reference attributes plus collection attributes writable from remote locations); **proves that deciding circularity for them is undecidable**; develops a family of conservative non-circularity tests and shows how to use them to schedule a remote AG with standard techniques.
- **What it does NOT do**: does not address convergence or content generation.
- **Relevance to AuxFlow**: **This is the strongest available support for AuxFlow's `UNKNOWN` verdict, and simultaneously a caution.** LaTeX's `\ref`/`\label` mechanism is remote reference par excellence -- a fact written at one point in the document is read at an arbitrarily distant point -- so AuxFlow's setting is the remote AG setting, in which exact circularity testing is *undecidable*. AuxFlow therefore cannot claim a complete classifier without a restriction argument, and `UNKNOWN` is not a weakness but the only defensible design. Equally, "conservative approximation plus scheduling" for remote dependencies is Boyland 2005, so AuxFlow may not claim it.
- **Anticipation verdict**: **PARTIAL OVERLAP** / INFORMS ONLY. Anticipates the undecidability that justifies AuxFlow's conservatism and the conservative-test-then-schedule design.
- **Evidence label**: **REPORTED** for Boyland's own wording (his paper was not opened). **SOURCED** for the fact itself, via two independent peer-reviewed primary sources read in full, both citing this paper by number for this exact result. AuxFlow should still open the paper before quoting a theorem number.

### A22. Ekman and Hedin 2004; Kramer and Van Wyk 2020 -- rewriting inside attribute evaluation

- **Citation**: Torbjorn Ekman, Gorel Hedin. "Rewritable Reference Attributed Grammars". In M. Odersky (ed.), *ECOOP 2004*, Lecture Notes in Computer Science 3086, Springer, pages 147-171.
  "Strategic tree rewriting in attribute grammars". *Proceedings of the 13th ACM SIGPLAN International Conference on Software Language Engineering (SLE 2020)*, pages 210-229. (Authors REPORTED as Kramer and Van Wyk; not captured in the CrossRef fields I selected.)
- **DOI / URL**: 10.1007/978-3-540-24851-4_7 and 10.1145/3426425.3426943.
- **Access**: CrossRef metadata only. Ekman and Hedin cross-confirmed by Soderberg and Hedin reference [9] (ECOOP 2004, LNCS 3086, pages 147-171). Abstracts and full texts NOT read.
- **Verbatim quote**: none from either paper. Magnusson and Hedin 2007 preprint mentions ReRAGs, verbatim: "In [8] a formalism for rewriting abstract syntax trees is presented. The formalism, Rewritable Reference Attributed Grammars (ReRAGs), has been implemented in our aspect-oriented compiler tool JastAdd. We plan to merge this extension of JastAdd with our CRAG extension." ([8] = Ekman and Hedin ECOOP 2004.)
- **Exact contribution**: **UNVERIFIED.** By title and by the ReRAG name, declarative context-dependent rewriting of the AST interleaved with attribute evaluation, in JastAdd; and in the 2020 paper, strategic rewriting in an AG setting.
- **What it does NOT do**: unknown.
- **Relevance to AuxFlow**: ReRAGs are the other half of what Soderberg and Hedin 2013 combines with circular attributes, and they are the mechanism by which attribute evaluation changes the tree in the JastAdd line. AuxFlow should be aware that "evaluation rewrites the tree, then re-evaluates" is a named, implemented, twenty-year-old formalism.
- **Anticipation verdict**: PARTIAL OVERLAP (probable; UNVERIFIED).
- **Evidence label**: SOURCED for bibliography (Ekman and Hedin); REPORTED for the SLE 2020 authorship; content UNVERIFIED for both.

### A23. Alblas 1991 -- the survey and taxonomy

- **Citation**: Henk Alblas. "Attribute evaluation methods". In H. Alblas and B. Melichar (eds.), *Attribute Grammars, Applications and Systems, International Summer School SAGA, Prague, Czechoslovakia, June 4-13, 1991, Proceedings*, Lecture Notes in Computer Science 545, Springer, pages 48-113.
  Companion: Henk Alblas, "Introduction to Attributed Grammars", same volume, pages 1-15, DOI 10.1007/3-540-54572-7_1. Volume DOI: 10.1007/3-540-54572-7. Volume ISBN 978-3-540-38490-8.
- **DOI / URL**: 10.1007/3-540-54572-7_3 -- <https://doi.org/10.1007/3-540-54572-7_3>
- **Access**: Complete abstract and full 40+-item reference list read from the Springer landing page. Full text paywalled and NOT read.
- **Verbatim quote** (abstract, complete):
  > "This paper surveys the main evaluation strategies for non-circular attribute grammars, i.e., passes, sweeps, visits and plans. **Attention is also focused on the iteration of evaluation passes for circular attribute grammars.**"
  (Emphasis added.)
- **Exact contribution**: the canonical taxonomy of AG evaluation strategies -- passes, sweeps, visits, plans -- plus coverage of iterating evaluation passes for circular AGs. Written by the author who coined `simple` versus `pure` multi-pass, in a volume he co-edited, alongside Swierstra and Vogt's HAG tutorial (A17).
- **What it does NOT do**: a survey; no new results.
- **Relevance to AuxFlow**: **the correct single citation for "static multipass analysis is a mature, taxonomised field".** It also demonstrates something awkward for AuxFlow: as of 1991, one LNCS volume contained both the pass/sweep/visit/plan taxonomy including iterated passes for circular AGs (Alblas, pages 48-113) and higher-order AGs where attribute values are tree (Swierstra and Vogt, pages 256-296). Both halves of AuxFlow's setting were textbook material in the same summer-school proceedings, thirty-five years ago.
- **Anticipation verdict**: INFORMS ONLY (survey), but citation-critical.
- **Evidence label**: SOURCED (abstract, bibliography).

---

## Negative results

Exact queries that found nothing relevant, recorded so they can be re-run.

1. `https://dblp.org/search/publ/api?q=Minimizing+the+number+of+evaluation+passes+for+attribute+grammars&h=30&format=json`
   -- Zero ICALP records. Exactly one hit, and it is SIAM J. Comput. 1981. **This is a positive finding disguised as a negative: the ICALP citation under this title does not exist.**

2. `https://dblp.org/search/publ/api?q=Ukkonen+attribute+grammars&h=50&format=json`
   -- One hit only (the SIAM paper). No further Rahia/Ukkonen AG-minimisation papers in dblp beyond the ICALP 1980 and SIAM 1981 pair. **Answers the task's "check whether there is a related journal version" question: yes, SIAM J. Comput. 10(4), and that is the only one.**

3. `attribute grammar analysis classify cycles "benign" convergent versus divergent fixpoint taint influence tree size` (web_search)
   -- NOTHING RELEVANT. No AG paper surfaced that classifies dependency cycles into "converges" versus "may diverge" by analysing whether cycle-carried values influence the *quantity of content generated*. The literature partitions the space differently: circularity existence (Knuth, Jazayeri et al., Wu), which attributes are on cycles (Rodeh and Sagiv), whether a cycle converges (Farrow, Jones, Magnusson and Hedin -- all *assume* a finite-height lattice rather than prove it), and whether tree creation terminates (Vogt et al., Krishnan and Van Wyk). **The specific bridge -- an influence/taint analysis from cycle-carried values to content quantity, used to split cycles into benign and amplifying -- did not surface in this area.** This is AuxFlow's most promising remaining novelty seam, but see the caveat in the summary.

4. `https://dblp.org/search/publ/api?q=Termination+Analysis+for+Higher-Order+Attribute+Grammars&h=10&format=json` and the de-hyphenated variant `...q=Termination+Analysis+Higher+Order+Attribute+Grammars...`
   -- Both returned socket-closed errors, as did several other dblp API calls in the same window (apparent rate limiting after ~8 successful calls). NOT a content-negative result; the record was verified via CrossRef instead. Re-runnable.

5. `https://dl.acm.org/doi/pdf/10.1145/359997.359999`, `.../74818.74830`, `.../3687997.3695644`; `https://dl.acm.org/doi/10.1145/1082036.1082042`, `.../78969.78971`
   -- All blocked (cookie-absent redirect, HTTP 403, or an unclearing Cloudflare interstitial, including from a real Chromium instance). Bochmann's abstract and reference list were captured from the DOI landing page in an earlier window before the block took effect.

6. `https://www.sciencedirect.com/science/article/pii/0022000082900307`
   -- HTTP 403. Worked around via `ris.utwente.nl` open access, which yielded the full text.

7. `https://epubs.siam.org/doi/10.1137/0214063`
   -- Cookie-absent redirect. Alblas 1985 remains metadata-only.

8. `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/78969.78971?fields=...abstract...`
   -- Abstract explicitly elided by the publisher ("Notice: The following paper fields have been elided by the publisher: {'abstract'}"). Jones 1990's own abstract is not obtainable through this route.

---

## Summary for the audit

1. **The Rahia and Ukkonen citation as circulated is wrong, and the error traces to Alblas 1981's own reference list.** There are two papers: ICALP 1980 / LNCS 85 / pages 500-511 / DOI `10.1007/3-540-10003-2_94`, titled "On the optimal assignment of attributes to passes in multi-pass attribute evaluators"; and SIAM J. Comput. 10(4):772-786, 1981 / DOI `10.1137/0210060`, titled "Minimizing the Number of Evaluation Passes for Attribute Grammars". Cite the SIAM paper. Reproducing the conflation is a visible error to any AG reviewer. (SOURCED)

2. **Bochmann 1976 is confirmed exactly as stated**, CACM 19(2):55-62, DOI verified, and its algorithm "decides how many passes from left to right are in general necessary, given the attribute grammar" -- static, grammar-only pass counting. Engelfriet and File 1982 pin it precisely: Bochmann's class is `simple multi-pass` (one pass number per attribute per nonterminal, uniform across instances and trees), decidable in polynomial time. (SOURCED)

3. **AuxFlow's instance-level pass numbering is a named, dated, complexity-classified AG class, and it is the hard one.** Alblas 1981 coined the distinction: `simple` = one pass number per attribute; `pure` = "no requirement that all occurrences of the same attribute are computed in the same pass". Engelfriet and File 1981 proved deciding `pure multi-pass` is **of inherently exponential time complexity**, polynomial only for fixed k, via a characterisation in terms of *paths through dependency graphs* -- the same technique AuxFlow uses. AuxFlow's move from fact kinds to fact instances is not a novel refinement; it is the 1981 pure-multipass setting, and it is EXPTIME-complete in general. AuxFlow owes a restriction argument or an explicit statement that it computes a conservative approximation. (SOURCED)

4. **Rahia and Ukkonen 1981 prices any minimality claim: constructing an optimal (minimum-pass) evaluation order is NP-complete**, and the standard construction can be a factor of ~2 off ($2n-1$ passes where $n$ suffice). AuxFlow must not claim its build plan is minimal without addressing this. Alblas 1985 (SIAM J. Comput. 14(4):889-914, metadata-only in this audit) is squarely on the same question and should be read. (SOURCED)

5. **AuxFlow's source-level diagnosis naming the offending facts is anticipated twice.** Alblas 1981, verbatim: the algorithms "indicate in case of failure the attributes that cause the rejection of the grammar". And Rodeh and Sagiv (JACM 46(4), 1999) studied exactly "which attributes are on cycles", gave a polynomial conservative approximation and an exact exponential algorithm, and **proved that finding the circular attributes is strictly harder than testing for circularity**. Magnusson and Hedin's robust CRAG evaluator likewise "detect[s] the error, identif[ies] the attributes involved, and raise[s] an exception". (SOURCED)

6. **AuxFlow's whole architectural pipeline is Jones 1990.** Build the instance-level attribute dependency graph for a given tree, find its strongly connected components, contract each into one node, topologically order the condensation, evaluate component by component with a single fixpoint iteration per non-trivial component, degrading to the standard optimal algorithm when acyclic. Shown optimal. Described in technical detail, verbatim, in the Magnusson and Hedin paper I read in full. AuxFlow may claim no novelty in graph construction, Tarjan SCC, condensation, or per-component fixpoint. (SOURCED via Magnusson and Hedin; Jones's own text UNVERIFIED)

7. **The exact convergence criterion AuxFlow's benign/amplifying split is a domain instance of is stated verbatim by Magnusson and Hedin**: a fixpoint is "guaranteed if the values for each attribute on a cycle can be organized in a lattice of finite height and if all the semantic functions involved in computing these attributes are monotonic on the respective lattices", with the footnote refinement "a complete partial order and ... the ascending chain condition". A table of contents shifting page numbers satisfies this; a page reference bounding a content-generating loop violates finite height because the value domain grows with the generated content. AuxFlow should state its classification in these terms. (SOURCED)

8. **Nobody in the circular-AG line checks that condition, and they say so.** Magnusson and Hedin 2007, verbatim: "Our evaluator presently does not check whether circularly defined attributes take their values from a lattice of finite height or if their defining semantic functions are monotonic. Thus there is no guarantee that iterations will converge. Our approach is in this respect similar to that of, e.g., Farrow." So Farrow 1986 and JastAdd 2007 both assume convergence. **That is the real gap AuxFlow could fill** -- deciding the precondition rather than assuming it. Note this independently corroborates correction 5: some inputs may not converge, and practitioners know it. Magnusson and Hedin even give a case where "there does not, in general, exist any fixed-point solution". (SOURCED)

9. **AuxFlow's claim that "in classical AGs no attribute value alters the shape of the derivation tree, and this is what makes our setting different" must be withdrawn as a novelty claim.** The first clause is true of Knuth-classical AGs. The second is false: higher-order attribute grammars removed exactly that restriction in 1989. Swierstra and Vogt 1991, verbatim: HAGs are an extension "in the sense that the distinction between the domain of parse-trees and the domain of attributes has disappeared: parse trees may be computed in attributes and grafted to the parse tree at various places." AuxFlow may still say *classical* AGs do not do this -- but must immediately concede that non-classical AGs have done it for 37 years, or a reviewer will do it for them. (SOURCED)

10. **Vogt et al. 1989 already identified that content generation destroys the termination guarantee, and made it a well-definedness condition.** Per Krishnan and Van Wyk, verbatim: a well-defined HOAG must be complete, non-circular, *and* create "a finite number of new trees during attribute evaluation"; and "attribute evaluation for a complete, non-circular HOAG may not terminate since creating an unbounded number of trees during higher-order attribute evaluation can lead to non-termination." Vogt et al. state a sufficient condition (Lemma 3.2, page 142) but apparently never implemented or evaluated it, and Vogt's thesis dropped the requirement. (SOURCED via Krishnan and Van Wyk; the PLDI 1989 text is REPORTED and **must be read directly** before AuxFlow cites Lemma 3.2.)

11. **THE SINGLE MOST DANGEROUS PIECE OF PRIOR ART IN THIS AREA: Krishnan and Van Wyk, "Termination Analysis for Higher-Order Attribute Grammars", SLE 2012, LNCS 7745, pages 44-63, DOI 10.1007/978-3-642-36089-3_4.** It is a *conservative static analysis* whose sole purpose is to decide whether attribute evaluation that *generates new content to be evaluated* terminates; it explicitly separates that question from circularity ("This type of non-termination is not detected by a circularity analysis for higher-order attribute grammars"); it uses SCC condensation of a non-terminal graph as its scheduling device (Procedure A); it is openly conservative ("there are terminating grammars for which the analysis fails"); and it is validated on a full attribute grammar for Java 1.4. Every structural element of AuxFlow's pitch -- static, conservative, separates cyclic from amplifying, SCC-based, real-corpus evaluation, three-way verdict including a reject -- is present. **AuxFlow's remaining distinction is narrow and must be stated precisely: Krishnan and Van Wyk assume non-circularity, so they cannot classify a *cyclic* input as benign versus amplifying, which is AuxFlow's headline case. That is the claim to make, and nothing broader.** (SOURCED, full text)

12. **Soderberg and Hedin, SLE 2013, closes even that gap at the setting level.** "Circular Higher-Order Reference Attribute Grammars", LNCS 8225, pages 302-321, DOI 10.1007/978-3-319-02654-1_17, abstract verbatim: "In this previous work, dependencies between circular attributes and rewrites are not considered. In this paper, we investigate how these extensions can interact, and still be well defined. We introduce a generalized evaluation algorithm that can handle grammars where circular attributes and rewrites are interdependent." That is cyclic dependencies interdependent with tree changes, plus a well-definedness account -- AuxFlow's configuration, named in 2013. Whether they also give a static up-front *classifier* is UNVERIFIED. **This paper must be read in full before AuxFlow claims any novelty on the cyclic-plus-generating combination.** (SOURCED abstract; body UNVERIFIED)

13. **The field is active on this exact seam right now.** Riouak, Fors, Oqvist, Hedin and Reichenbach, SLE 2024 (Distinguished Paper), DOI 10.1145/3687997.3695644, describe "a static meta-analysis that identifies" attributes that "can never be circular", in order to skip fixpoint machinery -- i.e. AuxFlow's `CERTIFIED` versus `cyclic` partition, in the same formalism, with measured speedups on real Java dataflow analyses. AuxFlow cannot present static partitioning of fixpoint attributes by circularity as new. (SOURCED abstract via author bibliography)

14. **Alblas 1989 anticipates AuxFlow's *setting* from the compiler-optimisation side, and it is uncomfortably close.** "Iteration of transformation passes over attributed program trees", Acta Informatica 27(1):1-40, DOI 10.1007/BF00263499, abstract verbatim: alternating attribute-evaluation phases (each a sequence of passes) with tree-transformation phases, iterated; "requires a distinction between consistent (i.e., correct) and approximate attribute values"; and closing with "This attribute evaluation and tree transformation strategy shows similarities with the evaluation methods for circular attribute grammars." Iterated passes over a mutating tree with approximate-then-consistent values, explicitly linked to circular AGs, in 1989. Body UNVERIFIED. (SOURCED abstract)

15. **Boyland 2005 both licenses and constrains AuxFlow's `UNKNOWN` verdict.** Circularity for remote/reference attribute grammars is **undecidable** (JACM 52(4):627-687; confirmed by two primary sources read in full). LaTeX's `\label`/`\ref` is remote reference par excellence, so AuxFlow lives in the undecidable setting. `UNKNOWN` is therefore not a shortcoming but the only honest design -- and AuxFlow should say so explicitly, citing Boyland. Conversely, "conservative non-circularity tests plus standard scheduling" is Boyland's own contribution, so AuxFlow may not claim that pattern either. (SOURCED via two citing primary sources; Boyland's own text REPORTED)

16. **Two bibliographic corrections AuxFlow should adopt.** (a) Knuth's correction is *Mathematical Systems Theory* **5(2)**:95-96, 1971, DOI 10.1007/BF01702865, per Springer's authoritative metadata -- not 5(1), which is what Krishnan and Van Wyk, Soderberg and Hedin, Swierstra and Vogt, and Magnusson and Hedin all print. (b) The correct modern statement of circularity complexity is **EXPTIME-complete**: EXPTIME-hard from Jazayeri, Ogden and Rounds, CACM 18(12):697-706, 1975, DOI 10.1145/361227.361231; membership in EXPTIME from Wu, TOPLAS 26(1):186-190, 2004, DOI 10.1145/963778.963783 (arXiv cs/0010015). Saying merely "exponential" understates what is known. (SOURCED)

17. **What survives for AuxFlow in this area, stated conservatively.** Not: pass-number assignment (Bochmann 1976), instance-level pass numbers (Alblas 1981, Engelfriet and File 1981), minimality (Rahia and Ukkonen 1981, Alblas 1985), instance dependency graph + Tarjan SCC + condensation + per-component fixpoint (Jones 1990), static identification of potentially-circular attributes (Farrow 1986, Riouak et al. 2024), naming the offending attributes (Alblas 1981, Rodeh and Sagiv 1999), the finite-height-lattice convergence criterion (Farrow 1986, Magnusson and Hedin 2007), values generating new content to be evaluated (Vogt et al. 1989), static conservative termination analysis of that generation (Krishnan and Van Wyk 2012), or the interdependence of circular attributes with tree rewrites (Soderberg and Hedin 2013). What may survive: (i) a *taint/influence* analysis from cycle-carried values to the quantity of generated content, used to split cycles into benign and amplifying -- negative result 3 found no AG paper doing this, and Krishnan and Van Wyk explicitly note that theirs is the first to use "the structure of the equations and not just the attribute dependencies", which is adjacent but rewriting-based rather than influence-based; and (ii) the instantiation of all of the above to a declared LaTeX subset with a concrete evaluation against checksum-based dynamic convergence detection. **Both are modest, domain-transfer-shaped claims, not foundational ones. On the evidence of this area, AuxFlow's defensible contribution is an application of the AG multipass/circular/higher-order canon to LaTeX auxiliary-file convergence, plus at most one new analysis component -- and that component's novelty is contingent on reading Soderberg and Hedin 2013 in full.**
