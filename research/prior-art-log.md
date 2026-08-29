# Prior-art search log

Record of what was searched, where, and what was found — including nothing. A negative result is
evidence only if the query is written down and can be re-run.

Labels follow [README.md](README.md): `MEASURED`, `SOURCED`, `REPORTED`, `INFERENCE`.

## Structure

This file is the **index and the register of outcomes**. The full records — every query string,
every verbatim quote, every access failure — live in [`sources/`](sources/), one file per search
area. Entries here are appended, never edited; a superseded finding gets a new entry that references
the old one.

| File | Search area | Size | Completeness |
|---|---|---|---|
| [`sources/area-a-attribute-grammars.md`](sources/area-a-attribute-grammars.md) | Attribute grammars, multipass evaluation, pass-number assignment, circular and higher-order attribute grammars | 118 KB | complete |
| [`sources/area-b-latex-compilation.md`](sources/area-b-latex-compilation.md) | LaTeX and document compilation as a research subject; the kernel mechanics; pagination literature | 91 KB | complete |
| [`sources/area-c-latex-tools.md`](sources/area-c-latex-tools.md) | Existing LaTeX build and dependency tools, by documentation and source | 44 KB | latexmk, latexrun, Tectonic, Typst, `labelschanged` complete; Rubber, arara, texdepend, graph tools outstanding |
| [`sources/area-d-non-convergence.md`](sources/area-d-non-convergence.md) | Non-convergence, cyclic dependency classification, the mechanism taxonomy | 40 KB | Farrow/Jones/Magnusson-Hedin and the mechanism taxonomy complete; analogous domains outstanding |
| [`sources/area-e-build-systems.md`](sources/area-e-build-systems.md) | Build-system research and practice | 75 KB | complete |
| [`sources/area-f-static-vs-dynamic.md`](sources/area-f-static-vs-dynamic.md) | Static bounds on fixpoint iteration; static schedulability under data-dependent rates | 31 KB | priorities 1 and 2 complete; termination analysis, Datalog, staged computation outstanding |
| [`sources/patent-prior-art.md`](sources/patent-prior-art.md) | Patent search | 50 KB | Part 1 complete; Part 2 partially complete, outstanding items listed in file |
| [`sources/tex-ecosystem-convergence-machinery.md`](sources/tex-ecosystem-convergence-machinery.md) | ConTeXt and `rerunfilecheck` convergence machinery, gathered directly | 8 KB | complete |

## Entry format, for anything appended after this audit

```
### YYYY-MM-DD  <source>
query    : <exact query string>
examined : <n> results
outcome  : <finding, or NOTHING RELEVANT>
status   : SOURCED | REPORTED
```

---

## Audit of 2026-08-27 — outcome register

Every item below is `SOURCED` unless marked otherwise. Each maps to a full record in
[`sources/`](sources/). Consequences for the specification are carried in
[`../docs/RELATED-WORK.md`](../docs/RELATED-WORK.md).

### Verifications requested by the audit and completed

| Item previously `REPORTED` | Outcome |
|---|---|
| Bochmann 1976, *CACM* 19(2):55–62, DOI `10.1145/359997.359999` | **Confirmed exactly**, including the quoted pass-counting sentence. Engelfriet and Filè pin the class as *simple multi-pass*, polynomial-time decidable. |
| Räihä and Ukkonen, ICALP 1980, LNCS 85 | **Citation was wrong.** It conflates two papers. ICALP 1980, LNCS 85:500–511, DOI `10.1007/3-540-10003-2_94` is titled "On the optimal assignment of attributes to passes in multi-pass attribute evaluators"; *SIAM J. Comput.* 10(4):772–786, 1981, DOI `10.1137/0210060` is titled "Minimizing the Number of Evaluation Passes for Attribute Grammars". The error traces to Alblas 1981's own reference list. **Cite the SIAM paper**; it carries the NP-completeness result and the `2n−1` bound. |
| Alblas 1981, *Acta Informatica* 16(4):427–464, DOI `10.1007/BF00264495` | **Confirmed.** Coins the *simple* / *pure* distinction. Its algorithms "indicate in case of failure the attributes that cause the rejection of the grammar" — which anticipates AuxFlow's diagnostic idea. |
| The complexity result on deciding pure multipass membership | **Confirmed** (Engelfriet and Filè): inherently exponential; polynomial only for fixed *k*; characterised via paths through dependency graphs. Also: circularity for attribute grammars is **EXPTIME-complete** (hard from Jazayeri, Ogden and Rounds 1975, DOI `10.1145/361227.361231`; membership from Wu 2004, DOI `10.1145/963778.963783`) — "exponential" understates it. |
| `latexmk`'s iteration cap and checksum mechanism | **Confirmed and quoted from the official manual and `latexmk.pl` 4.88.** `$max_repeat`, documented default `5`; a `(time, size, md5)` database over every file in the rule network; `Rerun to get` log scraping as a secondary trigger; the exhausted-cap message is `Maximum runs of <rule> reached without getting stable files` and names no cause. |
| The `latexrun` quote about Rubber's fragility | **Confirmed verbatim**, with a two-line concrete counterexample (`\newcommand{\includegraph}`) that is stronger than the abstract argument. |
| US10025569 (Texas Instruments) | **Confirmed and claim 1 quoted.** Granted 2018-07-17, **active**, fees paid to the eighth year, expiry 2036-07-19. Claim 1 is limited to compiling HLL to MLL via a control flow graph and a named backedge-collapse procedure. |
| US20240272888 (SAP SE) | **Confirmed, and the project's belief corrected.** Still **pending under non-final rejection**. "Diameter" is in the claims, but only the **dependent** ones (3, 4, 10, 11, 17, 18). The independent claims recite a bare parallel topological loop with no bound at all. |
| The three negative results asserted in the previous `RELATED-WORK.md` | **All three re-run with recorded queries and confirmed.** See the negative-results register below. |

### Findings that changed the project

Ordered by severity. These are the reason the audit was worth running.

1. **Krishnan and Van Wyk, "Termination Analysis for Higher-Order Attribute Grammars", SLE 2012,
   LNCS 7745:44–63, DOI `10.1007/978-3-642-36089-3_4`.** A conservative static analysis deciding
   whether attribute evaluation that *generates new content to be evaluated* terminates, explicitly
   distinguished from circularity analysis, using SCC condensation. This is AuxFlow's amplifying
   analysis in a different formalism, in 2012. **The single most dangerous item in the whole audit.**
   Must be read in full before any novelty claim.
2. **Jones, "Efficient evaluation of circular attribute grammars", *TOPLAS* 12(3):429–462, 1990,
   DOI `10.1145/78969.78971`.** Abstract, verbatim: the algorithms partition "the underlying
   attribute dependency graph into its strongly connected components" and order evaluation by "a
   topological sort of the resulting directed acyclic graph", with one fixpoint per component,
   degenerating to the standard optimal algorithm when acyclic. **AuxFlow's entire analysis
   architecture, published in 1990.** Concede outright.
3. **Farrow, DOI `10.1145/13310.13320`, 1986.** Constraints under which a circular dependency graph
   is well defined and computable by successive approximation; a static generation-time evaluator;
   and "a final algorithm […] that tells which individual attributes and functions must satisfy the
   constraints". Anticipates the *skeleton* of AuxFlow's cycle handling. What it does **not** do —
   confirmed in writing by Magnusson and Hedin §3.5 — is discharge the obligation.
4. **latexrun's README falsifies hypothesis H3.** Verbatim: output comparison "runs latex too many
   times; it will have already produced its final output one iteration before this approach can
   figure out that it's done. Instead, latexrun models latex and bibtex as deterministic functions of
   the file system state […] if the *inputs* […] do not change over one iteration, then latexrun can
   guarantee that the output also will not change, and stop." Tectonic independently avoids the extra
   run via same-run `ReadThenWritten` comparison. **The extra run is a property of output-comparison
   detectors, not of dynamic detection.**
5. **An ARG cycle is neither necessary nor sufficient for non-convergence.** Four published
   mechanisms — reference width changing a line break; `[!t]` floats with roman page numbering;
   `varioref`-style dynamic textual references; references in margin or foot notes — are
   non-convergent and produce no structural edge, because the `exists`/`value` split severs the
   extent-feedback edge by construction. **Falsifies H1's "zero false negatives" form in advance.**
   Full mechanism table in [`sources/area-d-non-convergence.md`](sources/area-d-non-convergence.md)
   Part 3.
6. **Typst fully anticipates AuxFlow's diagnostic output form.** `MAX_ITERS = 5` in
   `introspection/convergence.rs`; 128-bit hash comparison; and per-fact warnings carrying byte
   spans, full per-iteration value histories, and a secondary "created here" span. Its test suite
   contains AuxFlow's amplifying case verbatim, with the observed counts `0,1,2,3,4,5`. Typst has
   also removed the build-orchestration problem entirely.
7. **Mädje, MSc thesis, TU Berlin, 2022, §6.3.** Formalises document-introspection stability as a
   recurrence, **proves undecidability via Rice's theorem**, gives AuxFlow's benign and amplifying
   exemplars as worked examples, and prescribes a cap plus "a user-facing error message at the guilty
   locate call".
8. **Pluto — Erdweg, Lichter and Weiel, OOPSLA 2015, DOI `10.1145/2814270.2814316`.** LaTeX/BibTeX
   running example; the aux self-cycle identified explicitly; a `FixpointCycleHandler`; a BibTeX
   stamper that parses the aux file for citation keys (fact-level granularity, dynamically); and the
   published judgement, §3.3: "In the case of Latex where even parsing is undecidable, soundly
   detecting dependencies is a lost cause."
9. **US8181129B2 / US20090044157A1 (Mentor Graphics, now Siemens), "Acyclic modeling of combinational
   loops".** Claim 1 determines whether a combinational loop is monotonic; claim 6 notifies the user
   when it is not; claim 7 recites the loop being contained in a strongly connected component. **The
   most dangerous patent record found, and it was not one of the two on file.** Expires 2026-12-25.
10. **Hecht and Ullman, *SIAM J. Comput.* 4(4):519–532, 1975, DOI `10.1137/0204044`**, plus Ullman's
    own lecture notes: "if we use DF order to visit nodes, we converge in depth+2 passes",
    decomposed as "Depth+1 passes to follow that number of increasing segments" plus "1 more pass to
    realize we converged". **AuxFlow's build plan, stated as settled undergraduate pedagogy.**
11. **Lee and Messerschmitt, IEEE TC C-36(1):24–35, 1987, DOI `10.1109/TC.1987.5009446`.** Static
    schedulability holds exactly when production and consumption rates are "specified a priori",
    i.e. data-independent; a node whose output rate depends on data "is an asynchronous node" and
    leaves the model. **AuxFlow's benign/amplifying dividing line, in full generality, in 1987.**
12. **Söderberg and Hedin, SLE 2013, DOI `10.1007/978-3-319-02654-1_17`.** Circular attributes
    interdependent with tree rewrites, with a well-definedness account. **AuxFlow's exact
    configuration, named in 2013.** Must be read in full.
13. **`labelschanged` (CTAN, Brian Dunn after David Carlisle).** Already reports the offending label
    *instances* with old and new values, and ships a first-party taxonomy of causes naming
    `varioref`, margin and foot notes, and active characters in captions. **Anticipates
    instance-level fact identity in the LaTeX domain.**
14. **`rerunfilecheck.dtx`** states in its own documentation that base LaTeX's rerun warnings "are
    not given for the table of contents and other data stored in the aux files or other auxiliary
    files". **Motivation 3 is now sourced rather than measured.**
15. **The LaTeX kernel sources establish the pass lag mechanically.** `ltfiles.dtx`: `\document`
    executes `\@input{\jobname.aux}` **before** `\immediate\openout\@mainaux`. Also
    `\let\@writefile\@gobbletwo` during the aux read, so `\newlabel` facts survive into the next
    run's memory while `.toc`/`.lof`/`.lot` records do not — an asymmetry the state-equivalence
    definition (D6) must handle.
16. **Riouak et al., SLE 2024, DOI `10.1145/3687997.3695644`** describe "a static meta-analysis that
    identifies" attributes that "can never be circular", to skip fixpoint machinery. AuxFlow's
    `CERTIFIED`-versus-cyclic partition, in the same formalism, with measured speedups. The field is
    active on this exact seam.

### Negative-results register

Each is `SOURCED`; the exact queries are in the per-area files.

| Negative result | Where the queries are | Strength |
|---|---|---|
| No tool or publication statically derives the number of engine runs for a document | area B, six web queries plus arXiv and DBLP, ~70 sources examined | strong |
| No work performs static, subset-restricted, conservative convergence analysis of document compilation. The only work treating it as a static problem (Mädje 2022) does so to *deny* it in general | area B | strong |
| No attribute-grammar paper classifies dependency cycles by whether cycle-carried values influence the quantity of generated content | area A, negative result 3, exact query recorded | moderate — the adjacent work (Krishnan and Van Wyk) is rewriting-based rather than influence-based, so the distinction is fine and may not survive a full read |
| No build-system work bounds the number of iterations to a fixpoint, beyond Miller 1998's single qualitative sentence about recursive Make | area E | strong |
| No build-system work classifies cyclic build dependencies as benign versus divergent | area E | strong |
| No patent on static convergence classification of document compilation | patents, Concept 7 queries | moderate; keyword-only, no CPC-scoped search |
| No patent on classifying dependency cycles by whether a value affects the quantity of generated work. Targeted query `"taint analysis" "loop bound" "amount of" output generated static` returns **zero** | patents, Concept 4 and 7 | moderate |
| No patent on cloud or automated LaTeX compilation as such | patents, 87 results examined | moderate |
| The attribute-grammar multipass literature has **no reachable US patent footprint at all** | patents, Concept 1 | notable: the strongest anticipations of AuxFlow are papers no examiner has had to consider |
| No formal semantics of TeX exists; Knuth's own disclaimer (*TUGboat* 35:3, p. 239) is the primary evidence | area B | strong |
| No MSc or PhD thesis and no peer-reviewed paper on LaTeX build automation, LaTeX dependency analysis, or document compilation scheduling was located. "Incremental typesetting" as a research keyword is empty between 1988 and 2022 | area B | strong |
| No research publication statically derives the number of ConTeXt passes | tex-ecosystem file | moderate |

### Bibliographic corrections to propagate

1. Räihä and Ukkonen: two papers, not one. See above.
2. Magnusson and Hedin: DOI `10.1016/j.scico.2005.06.005` (*SCP* **68**(1):21–37, 2007) is
   **correct**. The value `10.1016/j.scico.2007.01.005` is a different paper (*SCP* **67**(1),
   "ScriptEase") and must not be used. The confusion is easy because the DOI suffix carries the
   submission year while the publication year is 2007.
3. Knuth's 1971 correction is *Mathematical Systems Theory* **5(2)**:95–96, DOI
   `10.1007/BF01702865` — not 5(1), which is what most citing papers print.
4. Circularity for attribute grammars is **EXPTIME-complete**, not merely "exponential".
5. Licker and Rice, ICSE 2019, is DOI `10.1109/ICSE.2019.00125`. The MAKAO tool demo is DOI
   `10.1109/ICSM.2007.4362678`.
6. Marriott, Moulder and Hurst, DocEng 2007, is DOI `10.1145/1284420.1284455` (Venkatesan's TUGboat
   reference list gives a wrong suffix).
7. **A TUG 2026 preprint cites "Bour, TeXpresso, *TUGboat* 44(2):185–192, 2023" at a URL that 404s,
   and no such article exists in the TUGboat title index, author index, or either candidate issue's
   file list. Do not propagate that citation.**
8. The Plass thesis PDF hosted at tug.org is scanned page images with no text layer. Do not quote it;
   its NP-completeness result is `REPORTED` via Brüggemann-Klein et al. 1995.
9. Any note describing an open or closed pull request for `labelschanged` is unsupported and must be
   struck: the GitHub API reports zero pull requests of any state and zero issues.

### `REPORTED` items still outstanding

Must be confirmed against primary sources before appearing in a report.

- **Krishnan and Van Wyk 2012 and Söderberg and Hedin 2013, full text.** Blocking: open decision D14
  in [`../docs/PROJECT.md`](../docs/PROJECT.md) makes the entire amplifying-analysis novelty claim
  contingent on these two reads.
- **Farrow 1986, full text.** Abstract obtained via CrossRef; ACM DL blocks non-institutional
  clients. The constraint formalism and the exact statement of the final algorithm are not read.
- **Jones 1990, full text.** Same; the architecture is established beyond doubt via Magnusson and
  Hedin's detailed description, but the paper itself is unread.
- **Vogt, Swierstra and Kuiper, PLDI 1989**, and Vogt's thesis. The well-definedness condition on
  finite tree creation is known only through Krishnan and Van Wyk.
- **Boyland, *JACM* 52(4), 2005**, on undecidability for remote attribute grammars. Known through two
  citing primary sources.
- **Kam and Ullman, *Acta Informatica* 7(3), 1977.** Metadata verified; no abstract deposited; the
  monotone-framework theorem and the MOP undecidability result are the standard summary, unread.
- **Alblas 1985 (*SIAM J. Comput.* 14(4):889–914)** and **Alblas 1989 (*Acta Informatica* 27(1):1–40,
  DOI `10.1007/BF00263499`)**. The 1989 paper — iterated transformation passes over a mutating
  attributed tree, explicitly linked to circular attribute grammars — is uncomfortably close and is
  metadata-only.
- **Rubber's own documentation.** Two fetch attempts returned 404. Its characterisation rests on
  latexrun's README, which is a competitor.
- **`xreferences`** (github.com/thiagomael/xreferences). Known only from a search snippet. Must be
  inspected before any claim about cross-reference graph extraction.
- **Full granted claim sets** for US20110314365A1, US20210232492A1, US20220197616A1, US11829738B2.
- **`arara`, `texdepend`, `latex-dependency-grapher`, `proofgraph`, KnowTeX's arXiv identifier,
  `ChkTeX`, `lacheck`.**
- **Frank Mittelbach's "impossible document" answer**, located in an earlier pass and not
  re-verified.
- **Analogous-domain check**: spreadsheet circular-reference classification, CSS cyclic percentage
  sizing, the ResizeObserver depth-monotonicity loop limit, constraint-layout solvability. Not
  attempted. This is the largest unexplored anticipation surface remaining.

### Searches worth repeating before publication

The prior-art landscape moves, and three of the audit's negatives are keyword-only.

- Static determination of build or pass schedules for document compilation.
- Static classification of fixpoint cycles by whether values influence the quantity of generated
  work — the one query that returns zero, and therefore the one most worth re-running.
- CPC-scoped patent searches in G06F8/41, G06F8/71, G06F40/106 and G06F30/327, rather than keyword
  searches.
- SLE, GPCE, DocEng and TUGboat proceedings from 2024 onward. Riouak et al. 2024 shows the attribute
  grammar community is active on the static-partition-by-circularity question right now.
- Typst's `introspection/convergence.rs` and its test suite. It is under active development and its
  diagnostics are the closest deployed competitor to AuxFlow's output.
