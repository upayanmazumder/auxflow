# LaTeX / document compilation literature

Search area B: academic and technical literature on LaTeX and document compilation — multi-pass
structure, cross-reference resolution and the `.aux` round trip, incremental typesetting,
document build automation as a research subject, dependency analysis for TeX/LaTeX, convergence
and fixpoint behaviour of document compilation, pagination fixpoints, and formalisation of TeX.
Audit date 2026-08-27.

## Headline answers to the two acceptance questions

**Q1. Does any published work statically derive the number of engine runs for a document?**
No. Nothing found. Every system located — latexmk-class tools, `llmk`, `arara`, Typst, Scribble —
determines the run count *dynamically*, by re-running and comparing state, under a fixed iteration
cap. The exact queries establishing this are in [Negative results](#negative-results).

**Q2. Does any published work treat LaTeX (or document) convergence as a static-analysis problem?**
Yes, but only to *deny* that it can be done in general, and only for Typst rather than LaTeX.
Mädje's MSc thesis (TU Berlin, 2022) formalises document introspection convergence as a recurrence
relation and proves via Rice's theorem that stability is undecidable for arbitrary code, concluding
that the compiler must instead stop after a constant number of tries. That is the single most
dangerous piece of prior art in this area and it is fully sourced below. No work was found that
performs a *conservative, subset-restricted, sound* static analysis of document convergence — which
is the only defensible remaining position for AuxFlow.

## Search log

### GitHub — LaTeX kernel source (`latex3/latex2e`, branch `develop`)
```
query    : file_read base/ltxref.dtx
examined : 1 file (full)
outcome  : Primary source for \label / \ref / \pageref / \newlabel / \@setref. Establishes that
           \label writes \newlabel to \@auxout during the run and \ref reads only \r@<key>,
           i.e. values from a previously-read .aux.
status   : SOURCED
```
```
query    : file_read base/ltfiles.dtx
examined : 1 file (full, 1843 lines)
outcome  : Primary source for the round trip. \document reads \jobname.aux and only THEN reopens
           it for writing; \include redirects \@auxout to a per-part .aux and writes counter
           checkpoints (\@writeckpt / \@setckpt). This is the mechanical proof of the one-run lag.
status   : SOURCED
```
```
query    : file_read base/ltmiscen.dtx
examined : 1 file (full, 1900 lines)
outcome  : Primary source for the rerun warning. \enddocument closes the aux, rebinds
           \@newl@bel to \@testdef, re-inputs the aux, and \@enddocument@kernel@warnings emits
           "Label(s) may have changed. Rerun to get cross-references right". Also found the
           second rerun warning "Temporary extra page added at the end. Rerun to get it removed",
           and the kernel comment explaining that the warning is deliberately SUPPRESSED when
           labels are multiply defined.
status   : SOURCED
```

### CTAN mirror — `rerunfilecheck`
```
query    : http://mirrors.ctan.org/macros/latex/contrib/rerunfilecheck/rerunfilecheck.dtx
examined : 1 file (26763 bytes), Documentation section read in full
outcome  : Explicit primary statement that base LaTeX's rerun warning does not cover the table of
           contents or other auxiliary files, and that this package instead uses MD5 checksums.
status   : SOURCED
```
```
query    : https://mirror.ctan.org/macros/latex/contrib/oberdiek/rerunfilecheck.dtx
examined : 1
outcome  : HTTP 404. Package is no longer under the oberdiek/ path; use contrib/rerunfilecheck/.
status   : SOURCED (negative path note)
```

### TUGboat contents indexes (https://tug.org/TUGboat/Contents/)
```
query    : listkeyword.html + listtitle.html, fetched in full (2.26 MB), regex-scanned for
           /rerun|latexmk|convergen|multi-?pass|multiple run|dependenc|incremental|auxiliary|
           cross-?refer|\.aux|build|Makefile|pagination|page break|float|fixpoint|fixed point|
           semantics|Turing|automat/i  and separately for /paginat|output routine|galley/i
examined : 169 + 12 matching index lines out of ~3000 title groups
outcome  : Located, with exact issue/author/PDF for each: Gaspar "Does not suffice to run latex a
           finite number of times to get cross-references right" (35:1); Asakura llmk (41:2);
           Cereda arara (39:2); Thurnherr "An introduction to the LaTeX cross-referencing system"
           (38:1); Mittelbach "Formatting documents with floats" (21:3); Mittelbach
           "fewerfloatpages" (41:1) and "How to influence the position of float environments"
           (35:3); Venkatesan "TeX as a three-stage rocket" (36:2); Stamerjohanns "Texmlbus"
           (42:2); Schrod/Rowley/Detig "A taxonomy of automated typesetting systems" (27:0);
           Rowley & Mittelbach "The floating world" (15:3); Fine "Line breaking and page
           breaking" (21:3) and "Galleys, space, and automata" (14:3); Mailhot "Implementing
           dynamic cross-referencing and PDF with PreTeX" (20:3).
status   : SOURCED
```
```
query    : listtitle.html scanned for /TeXpresso|presso/i ; listauthor.html scanned for /Bour,/
examined : full index
outcome  : NOTHING RELEVANT. No TUGboat article named TeXpresso and no author "Bour" in the
           TUGboat author index. See the UNVERIFIED entry below — a TUG 2026 preprint cites
           "TUGboat 44(2):185-192, 2023, tb44-2/tb138bour-texpresso.pdf" and that URL 404s.
status   : SOURCED (negative)
```

### arXiv API (`export.arxiv.org/api/query`)
```
query    : all:"LaTeX compilation"                    -> 23 results examined
outcome  : One relevant hit: arXiv:2603.02873 "LaTeX Compilation: Challenges in the Era of LLMs".
           Also arXiv:2005.12660 "A Makefile for Developing Containerized LaTeX Technical
           Documents" (tooling note, not analysis). Everything else was false positives from
           physics/maths papers whose text mentions LaTeX.
status   : SOURCED
```
```
query    : all:"incremental typesetting"              -> 0 results
query    : abs:"typesetting" AND abs:"convergence"    -> 0 results
query    : all:"TeX" AND all:"formal semantics"       -> 0 results
query    : all:"pagination" AND all:"NP-complete"     -> 1 result, unrelated (bin packing)
query    : abs:"cross-reference" AND abs:"document" AND abs:"dependency" -> 6 results, all
           LLM/retrieval papers, none about document compilation
outcome  : NOTHING RELEVANT. arXiv contains no work on incremental typesetting, typesetting
           convergence, or formal semantics of TeX.
status   : SOURCED (negative)
```

### DBLP publication API
```
query    : "Automatic float placement multi-column documents"
outcome  : Marriott, Moulder, Hurst, DocEng 2007, pp. 125-134, doi:10.1145/1284420.1284455.
           (Note: Venkatesan's TUGboat reference list gives the same pages; the DOI suffix is
           ...1284455, not ...1284453.)
status   : SOURCED
```
```
query    : "Breaking paragraphs into lines"
outcome  : Knuth & Plass, Softw. Pract. Exp. 11, pp. 1119-1184, 1981, doi:10.1002/SPE.4380111102.
status   : SOURCED (metadata)
```
```
query    : "Incremental document formatting"
outcome  : Pehong Chen, Michael A. Harrison, Ikuo Minakata, DOCPROCS 1988, pp. 93-100,
           doi:10.1145/62506.62523.
status   : SOURCED (metadata)
```
```
query    : "i-LaTeX transitional representations"
outcome  : Gobert & Beaudouin-Lafon, CHI 2022, pp. 554:1-554:16, doi:10.1145/3491102.3517494.
status   : SOURCED (metadata)
```
```
query    : "TeXpresso live rendering LaTeX"
outcome  : NOTHING. Not indexed in DBLP.
status   : SOURCED (negative)
```
```
query    : "Pagination reconsidered"
outcome  : NOTHING. Electronic Publishing: Origination, Dissemination and Design is not indexed
           in DBLP for this item. Metadata had to be obtained from the paper itself.
status   : SOURCED (negative)
```
```
query    : "Optimal pagination techniques automatic typesetting"
outcome  : DBLP JSON endpoint returned unparseable body; retry not attempted. Metadata obtained
           instead from the Stanford SearchWorks catalogue record and from the paper's own
           title page.
status   : REPORTED
```

### TeX FAQ (texfaq.org)
```
query    : https://texfaq.org/FAQ-multiruns
examined : 1
outcome  : HTTP 404. No such slug. The FAQ index was then fetched in full and regex-scanned for
           entries matching /rerun|run|refer|label|aux|multip|cross/i.
status   : SOURCED (negative path note)
```
```
query    : https://texfaq.org/ index scan, then FAQ-rerun and FAQ-crossref
examined : 19 candidate entries, 2 read in full
outcome  : FAQ-rerun "Rerun messages won't go away" contains a primary statement of
           non-termination via roman-numeral page-number oscillation. FAQ-crossref documents the
           \label-before-\caption class of wrong-reference bug (a source-level diagnosis class,
           not a convergence question).
status   : SOURCED
```

### Web search — pagination complexity
```
query    : Plass "Optimal pagination techniques for automatic typesetting systems" Stanford 1981
           STAN-CS-81-870 pdf
outcome  : Thesis PDF located at http://tug.tug.org/docs/plass/plass-thesis.pdf (redirects to
           tug.org/docs/plass/plass-thesis.pdf). Also surfaced Mittelbach's Computational
           Intelligence 2019 pagination paper and "Knuth-Plass Revisited" (DocEng 2015).
status   : SOURCED
```
```
query    : "Pagination reconsidered" Brüggemann-Klein Klein Wohlfeil "Electronic Publishing" 1995
outcome  : Full text located at
           https://mirror.gutenberg-asso.fr/tex.loria.fr/typographie/brueggemann1995pagination2.pdf
status   : SOURCED
```
```
query    : Mittelbach "A general framework for globally optimized pagination" preprint
           latex-project pdf
outcome  : No open preprint found. Wiley landing page blocks non-cookie clients
           (onlinelibrary.wiley.com/action/cookieAbsent). Metadata only.
status   : REPORTED
```

### Web search — the two acceptance questions
```
query    : "static analysis" predict "number of runs" OR "number of passes" LaTeX document
           compilation determine statically
sub-queries actually issued by the tool:
           - static analysis LaTeX compilation runs passes predict
           - LaTeX document compilation iterations static analysis determine
           - "LaTeX" "static analysis" "compilation passes" predict
examined : 31 sources
outcome  : NOTHING RELEVANT. No paper, thesis, or tool that statically derives a run count. The
           only substantive academic hit was arXiv:2603.02873, which argues the OPPOSITE — that
           tools "cannot reliably construct an Abstract Syntax Tree (AST) or structural model".
           Remaining hits were unrelated US patents on compiler pass pipelines and generic
           tutorials.
status   : SOURCED (negative)
```
```
query    : "how many times" OR "number of compilation passes" derive statically document markup
           "dependency graph" cross-references research paper
sub-queries actually issued by the tool:
           - static derivation dependency graph compilation passes document markup
           - number compilation passes needed dependency graph cross-references
           - LaTeX multiple passes cross-references resolution research
examined : 39 sources
outcome  : No static derivation found. Two genuinely relevant discoveries: (a) Scribble's
           documented four-pass model with a fixed-point traverse pass; (b) a publicly listed
           non-academic tool "xreferences" (https://github.com/thiagomael/xreferences) described
           in the search result as building "a dependency graph from cross-references in LaTeX
           documents" and emitting Graphviz/TikZ output. The tool was NOT inspected (out of
           scope) and is recorded as REPORTED. Also surfaced arXiv:2601.15294 "KnowTeX:
           Visualizing Mathematical Dependencies" — deferred to Area A/tools, which is already
           on it.
status   : SOURCED (negative on the main question)
```

### Delegated discovery (2 read-only scouts), all candidates re-verified by me
```
query    : formal semantics of TeX; TeX Turing-completeness proof; operational semantics TeX
           macro expansion arxiv; decidability TeX macros halting problem paper; formal grammar
           LaTeX parsing research paper; static analysis type system LaTeX macros research;
           TeX tokenizer catcode formal grammar academic; DocEng proceedings LaTeX formal model
           cross-reference aux file  (full verbatim list in the scout transcript)
examined : ~21 queries
outcome  : NOTHING RELEVANT. No peer-reviewed operational or denotational semantics of TeX; no
           academic Turing-completeness proof; no paper formalising the .aux round trip or LaTeX
           counters; no type system for TeX macros. Strongest primary evidence for the negative
           is Knuth's own disclaimer in TUGboat 35:3 (verified by me below).
status   : SOURCED (negative)
```
```
query    : Laurenz Maedje master's thesis Typst TU Berlin; Typst documentation iterative layout
           fixed point counters page numbers convergence; memoize LaTeX package CTAN; incremental
           typesetting recompilation research paper; "instant preview" TeX research paper;
           Overleaf cloud LaTeX compilation architecture technical report peer reviewed; thesis
           "LaTeX" build system dependency graph scheduling; "document compilation" "build
           system" dataflow ACM DocEng; Haug "Fast typesetting with incremental compilation"
examined : ~11 queries + fetch attempts
outcome  : Mädje thesis, Typst docs, memoize, Chen/Harrison/Minakata 1988, i-LaTeX CHI 2022 all
           located and subsequently verified by me. NEGATIVE: no peer-reviewed Overleaf
           architecture paper; no MSc/PhD thesis specifically about LaTeX build automation or
           LaTeX dependency analysis; "incremental typesetting" as a research keyword is
           essentially empty between 1988 and 2022.
status   : SOURCED (negative) / REPORTED (candidates, then re-verified individually)
```

### Direct primary-source fetches I performed to verify scout candidates
```
query    : https://typst.app/docs/reference/context/
outcome  : "Compiler iterations" section read in full. Documented five-attempt cap and the
           warning string "document did not converge within five attempts".
status   : SOURCED
```
```
query    : https://laurmaedje.github.io/programmable-markup-language-for-typesetting.pdf
examined : 1.12 MB PDF, converted with pdftotext -layout, §6.3 read in full (pp. 48-51)
outcome  : The undecidability argument. See the entry below. Title page confirms: TU Berlin,
           Faculty IV, Master's thesis, Computer Science, 8 September 2022, examiners Kao and
           Glesner, advisor Stawinoga.
status   : SOURCED
```
```
query    : https://docs.racket-lang.org/scribble/core.html
outcome  : Scribble §6.3 "Structures And Processing": four passes, traverse pass iterates to a
           fixed point.
status   : SOURCED
```
```
query    : https://ctan.org/pkg/memoize
outcome  : Package page read. v1.4.1, 2024-12-02, Sašo Živanović. Caching of compilation results,
           keyed on code plus user-adjustable context.
status   : SOURCED
```
```
query    : https://tug.org/TUGboat/tb35-3/tb111knut-20.pdf
outcome  : Knuth's own disclaimer of any interest in a formal correctness notion for TeX,
           answer 12 (to Udi Manber), p. 239.
status   : SOURCED
```
```
query    : HEAD/GET on https://tug.org/TUGboat/tb44-2/tb138bour-texpresso.pdf and
           https://tug.org/TUGboat/tb44-3/tb138bour-texpresso.pdf
outcome  : Both HTTP 404. TUGboat 44:2 uses the tb137* filename sequence and 44:3 uses tb138*;
           neither issue's file list contains a texpresso item. The citation is unverified and
           the given URL is wrong.
status   : SOURCED (negative)
```
```
query    : http://tug.tug.org/docs/plass/plass-thesis.pdf
outcome  : Fetched. 80 pages of SCANNED PAGE IMAGES with no text layer. Contribution cannot be
           quoted from the primary source; it is quoted below from Brüggemann-Klein et al. 1995
           instead and labelled accordingly.
status   : SOURCED (metadata) / REPORTED (content)
```

---

## Verified sources

### B1. LaTeX kernel — cross-referencing (`ltxref.dtx`)

- **Citation** — Johannes Braams, David Carlisle, Alan Jeffrey, Leslie Lamport, Frank Mittelbach,
  Chris Rowley, Rainer Schöpf. *ltxref.dtx — LaTeX Kernel (Cross Referencing)*, file version
  `[2026/01/07 v1.1w]`, part of the LaTeX base distribution.
- **DOI / URL** — https://github.com/latex3/latex2e/blob/develop/base/ltxref.dtx
- **Access** — full source, read in full.
- **Verbatim quote** (documentation block, "Cross Referencing"):
  > "The command `\label{FOO}` then writes the following on file `\@auxout`:
  > `\newlabel{FOO}{{eval(\@currentlabel)}{eval(\thepage)}{eval(\@currentlabelname)}{eval(\@currentHref)}{eval(\@kernel@reserved@label@data)}}`"

  and, on `\newlabel` itself:
  > "This command will be written to the `.aux` file to pass label information from one run to another."

  and the implementation of `\@setref`:
  > `\def\@setref#1#2#3{% \ifx#1\relax \protect\G@refundefinedtrue \nfss@text{\reset@font\bfseries ??}% \@latex@warning{Reference `#3' on page \thepage \space undefined}% \else \expandafter#2#1\@empty\@empty\@empty\null \fi}`
- **Exact contribution** — Defines the fact-level protocol. Each `\label` emits exactly one
  `\newlabel` record carrying, per label key, the current counter representation, the current page
  number, the current label name, the hyperref target and a reserved kernel slot. Each `\ref` /
  `\pageref` reads the *macro* `\r@<key>` and selects the first or second component; if `\r@<key>`
  is undefined it typesets `??` and warns.
- **What it does NOT do** — There is no graph, no ordering analysis, no pass numbering, and no
  notion of when a value will become available. `\ref` cannot see anything written in the current
  run; it only sees what `\r@<key>` was set to when the `.aux` was read.
- **Relevance to AuxFlow** — This is the ground truth for AuxFlow's *fact instance* node type and
  for the claim that `\pageref` and `\ref` read distinct components of one record. It supports
  AuxFlow's instance-level granularity: the kernel genuinely stores five distinct values per label,
  so "this label's page number" is a real, separately-addressable datum, not an AuxFlow invention.
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B2. LaTeX kernel — file handling and the `.aux` round trip (`ltfiles.dtx`)

- **Citation** — Same authors. *ltfiles.dtx — LaTeX Kernel (File Handling)*, file version
  `[2026-06-01 v1.2w]`, part of the LaTeX base distribution.
- **DOI / URL** — https://github.com/latex3/latex2e/blob/develop/base/ltfiles.dtx
- **Access** — full source, read in full (1843 lines).
- **Verbatim quote** — the documentation header for `\document`:
  > "`\document` (ie `\begin{document}`) — Reads in the .AUX files and `\catcode`'s `@` to 12."

  and the implementation, in order:
  > `\begingroup\@floatplacement\@dblfloatplacement \makeatletter\let\@writefile\@gobbletwo \global \let \@multiplelabels \relax \@input{\jobname.aux}% \endgroup \if@filesw \immediate\openout\@mainaux\jobname.aux \immediate\write\@mainaux{\relax}% \fi`

  and for `\include`:
  > `\immediate\write\@mainaux{\string\@input{#1.aux}}` … `\@writeckpt{#1}`
  > `\def\@wckptelt#1{\immediate\write\@partaux{\string\setcounter{#1}{\the\@nameuse{c@#1}}}}`
- **Exact contribution** — Establishes the mechanics of the round trip with pass semantics. The
  previous run's `.aux` is `\@input` **before** `\jobname.aux` is reopened for writing, so the
  in-memory `\r@…` values for run *p* are exactly the records written during run *p−1*. `\include`
  splits the aux into per-part files stitched by `\@input`, and writes counter checkpoints so a
  later `\includeonly` run can restore counter state without processing the omitted part.
  Note also `\let\@writefile\@gobbletwo` during the aux read: `\@writefile` records (`.toc`,
  `.lof`, `.lot`) are *discarded* at read time, unlike `\newlabel`.
- **What it does NOT do** — No dependency tracking whatsoever; no analysis of which facts changed;
  no ordering guarantee beyond "read then write". Nothing computes how many runs are needed.
- **Relevance to AuxFlow** — This is the primary source for AuxFlow's "pass lag" edge weight of
  exactly 1 for `.aux`-mediated facts. It also gives AuxFlow a real, sourced asymmetry it must
  model: `\newlabel` facts survive into the next run's memory, whereas `\@writefile` facts are
  gobbled on read and only reach the document via `\@starttoc` reading the `.toc` file. Those are
  two different channels with different observability, which matters for any claim about which
  facts the kernel can and cannot compare.
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B3. LaTeX kernel — the rerun warning and `\@testdef` (`ltmiscen.dtx`)

- **Citation** — Same authors. *ltmiscen.dtx — LaTeX Kernel (Misc. Environments)*, file version
  `[2025/04/28 v1.2h]`, part of the LaTeX base distribution.
- **DOI / URL** — https://github.com/latex3/latex2e/blob/develop/base/ltmiscen.dtx
- **Access** — full source, read in full (1900 lines).
- **Verbatim quote** — `\enddocument`:
  > `\immediate\closeout\@mainaux \let\@setckpt\@gobbletwo \let\@newl@bel\@testdef \let\new@label@record\@kernel@new@label@record@testdef` … `\@tempswafalse \global\advance\c@page\@ne \makeatletter \@@input\jobname.aux`

  `\@testdef` itself:
  > `\def\@testdef #1#2#3{% \def\reserved@a{#3}\expandafter \ifx \csname #1@#2\endcsname \reserved@a \else \@tempswatrue \fi}`

  the warning, in `\@enddocument@kernel@warnings`:
  > `\if@filesw \ifx \@multiplelabels \relax \if@tempswa \@latex@warning@no@line{Label(s) may have changed. Rerun to get cross-references right}% \fi \else \@multiplelabels \fi \ifx \@extra@page@added \relax \@latex@warning@no@line{Temporary extra page added at the end. Rerun to get it removed}% \fi \fi`

  and, critically, the kernel's own comment on the suppression rule:
  > "If a label is defined more than once, `\@tempswa` will always be true and thus produce a
  > ``Label(s) may …'' warning. But since a rerun will not solve that problem (unless one uses a
  > package like `varioref` that generates labels on the fly), we suppress this message."
- **Exact contribution** — The engine's own convergence oracle, in full. At `\end{document}` the
  freshly written `.aux` is re-read with `\newlabel` rebound to `\@testdef`, which compares each
  new record against the value currently held in `\r@<key>` (i.e. the *previous* run's value) and
  raises a single global boolean on any difference. That boolean drives the rerun warning. There
  are two such warnings, the second concerning a temporary extra page.
- **What it does NOT do** —
  1. It is a single global boolean. It never names which label changed, so it cannot diagnose.
  2. It only covers records that go through `\@newl@bel` (labels and `\bibcite`). Table of contents
     and other `\@writefile` data are not compared at all (see B4).
  3. It is deliberately **disabled** when any label is multiply defined — precisely the case where a
     naive reader would most expect a warning.
  4. It says nothing about how many further runs are needed, and cannot distinguish "one more run
     will fix this" from "this will never converge".
- **Relevance to AuxFlow** — Direct support for the project's established correction (3): the
  runtime warning is not a reliable convergence oracle, and the reason is now sourced from the
  kernel rather than asserted. Also gives AuxFlow a concrete diagnostic gap to claim: the kernel
  loses the identity of the changed fact, which is exactly what AuxFlow's instance-level graph
  retains. That is a modest but real and defensible delta.
- **Anticipation verdict** — INFORMS ONLY (it is the baseline AuxFlow must beat, not prior art for
  what AuxFlow does).
- **Evidence label** — SOURCED.

### B4. `rerunfilecheck` — checksum-based rerun detection for auxiliary files

- **Citation** — Heiko Oberdiek and the Oberdiek Package Support Group. *rerunfilecheck — Rerun
  checks for auxiliary files*, version `2025-06-21 v1.11`. CTAN,
  `macros/latex/contrib/rerunfilecheck`.
- **DOI / URL** — http://mirrors.ctan.org/macros/latex/contrib/rerunfilecheck/rerunfilecheck.dtx
  (source `.dtx`, documentation section read directly)
- **Access** — full source read; Documentation section read in full.
- **Verbatim quote** (§ Documentation, opening paragraph):
  > "LaTeX informs the user, when to run LaTeX again, if the references have changed. It has the
  > old references from the first reading of the `aux` files already in memory, thus it compares
  > them with the new version of the `aux` file at the end of the document. **However this rerun
  > warnings are not given for the table of contents and other data stored in the `aux` files or
  > other auxiliary files.** Usually many of these data as the table of contents is not keep in
  > memory. If someone wants to detect changes, he has either to keep the data in memory. This does
  > not scale well with huge documents. Or he copies the file before they are changed. Slow I/O
  > operations cost time."

  and on the mechanism:
  > "Since version 1.30.0 pdfTeX provides `\pdfmdfivesum` and `\pdffilesize`. … Thus this package
  > `rerunfilecheck` uses these features to detect file changes. This saves the packages from
  > keeping the whole files in memory or in file copies. The drawback are different files with the
  > same size and the same MD5 checksum (seldom, hopefully)."

  and on the interface:
  > "If the file has changed, `\RerunFileCheck` informs the user with a warning that the file has
  > changed and says the magic word ``Rerun''."
- **Exact contribution** — Extends rerun detection from the label set to arbitrary auxiliary files
  (`.toc`, `.lof`, `.idx`, `.glo`, per-part `.aux`) by recording an MD5 checksum plus file size
  before the file is opened for writing and re-checking it at `enddocument/info`. Options
  `mainaux`, `partaux`, `starttoc`, `index`, `glossary`, `aux`.
- **What it does NOT do** — Purely dynamic, purely per-file. No graph, no per-fact granularity
  (a checksum change tells you the `.toc` changed, not which entry), no pass-count prediction, and
  no distinction between a converging oscillation and a divergence. Emits a false negative on MD5
  collision, as the author notes.
- **Relevance to AuxFlow** — Two things. First, it is a *published, primary, quotable admission*
  that base LaTeX's rerun warning is insufficient — exactly what the task asked to establish.
  Second, it is the strongest form of the practical baseline AuxFlow is measured against
  (established correction 4): checksum-based dynamic convergence detection. AuxFlow must not claim
  novelty for detecting that a file changed between runs.
- **Anticipation verdict** — PARTIAL OVERLAP (on convergence detection; none on static analysis).
- **Evidence label** — SOURCED.

### B5. Mädje — *Typst: A Programmable Markup Language for Typesetting* (MSc thesis) ← MOST DANGEROUS

- **Citation** — Laurenz Mädje. *Typst — A Programmable Markup Language for Typesetting.* Master's
  thesis, Computer Science, Technical University of Berlin, Faculty IV – Electrical Engineering and
  Computer Science, 8 September 2022. First examiner Prof. Dr. Odej Kao; second examiner Prof. Dr.
  Sabine Glesner; advisor Dr. Nicolai Stawinoga.
- **DOI / URL** — https://laurmaedje.github.io/programmable-markup-language-for-typesetting.pdf
- **Access** — full text (1.12 MB PDF, text layer present); §6.3 "Introspection", pp. 48–51, read
  in full; title page and Chapter 7 opening also read.
- **Verbatim quotes** (§6.3, pp. 48–51):
  > "Intra-document dependencies are cyclic in nature. For instance, a heading might originally
  > have been on page 5, but once added to the table of contents, the table of contents breaks
  > across two pages and the heading is suddenly on page 6. These dependencies pose problems for
  > typesetting software. Microsoft Word and TEX show different symptoms of the same problem: In
  > Word, users have to manually update their table of contents through a click of a button.
  > Meanwhile in TEX, they need to compile multiple times for changed headings to propagate to the
  > table of contents." (p. 48)

  > "Resolving introspections is an iterative process. … If the positions after the second round
  > differ from the ones after the first round, a third round of layout becomes necessary. This
  > process repeats until a fixpoint on the positions is reached." (p. 50)

  > "A change to the positions does not always necessitate a relayout though. The significant
  > question is whether the change is observable. If all locate queries made on the old positions
  > yield the same result on the new ones, the observed part of the input stays unchanged. As Typst
  > is deterministic, a relayout would produce the same output and is thus unnecessary." (p. 50)

  > "Some introspections are fundamentally unstable. In the example on the next page, we locate all
  > headings, determine the page number 𝑝 of the first heading, and then insert 𝑝 page breaks
  > before that heading. … On each relayout, the document grows by one page. The result never
  > stabilizes." (p. 50)

  > "Even worse, in general, Typst cannot know whether an introspection will stabilize. Consider
  > the generalized case of a single element and a single locate call. … Mathematically speaking,
  > the position of the heading is defined through a recurrence relation 𝑎 where 𝑎₁ ≔ 1 and
  > 𝑎ₙ ≔ 𝑓(𝑎ₙ₋₁). Here, 𝑓 : ℕ → ℕ is defined through the code in the function passed to locate.
  > The introspection is stable if and only if 𝑎 converges to a fixed value. Thus, to decide
  > whether an introspection is stable, Typst would need to be able to prove that 𝑎 converges for
  > an arbitrary computable function 𝑓. This is a non-trivial behavioural property of 𝑓: It holds
  > true for 𝑓(𝑛) = 1 but not for 𝑓(𝑛) = 𝑛 + 1. Thus, due to Rice's theorem, it is undecidable
  > for an arbitrary 𝑓. Typst cannot analyze whether an arbitrary introspection stabilizes.
  > Luckily, typical introspections stabilize within two to three passes. Thus, a Typst compiler
  > can simply stop compiling after a small constant number of tries, producing a user-facing error
  > message at the guilty locate call." (p. 51)
- **Exact contribution** — Designs a typesetting language whose cross-reference / counter /
  table-of-contents mechanism is a first-class `locate` primitive, and analyses its convergence
  properly. Specifically it (i) names intra-document dependencies as *cyclic*, (ii) gives the
  benign case (TOC shifts a heading's page) and the amplifying case (page reference bounds page
  generation) as worked examples, (iii) formalises stability as convergence of a recurrence
  relation over positions, (iv) proves via Rice's theorem that stability is undecidable for
  arbitrary code, (v) proposes an observability-based relayout test at the granularity of
  individual `locate` queries rather than whole-document state, and (vi) prescribes the practical
  remedy: a small constant iteration cap plus a user-facing error pointing at the guilty `locate`
  call.
- **What it does NOT do** — Nothing is static. There is no dependency graph built from source, no
  SCC computation, no pass-number propagation, no taint analysis, no classification of cycles into
  benign vs amplifying as a *decision procedure*, and no restricted subset on which convergence is
  decided soundly. The observability test and the guilty-call diagnostic are both computed at
  runtime, during and after layout. The target language is Typst, not LaTeX, and the thesis
  explicitly notes that `locate` was not yet implemented in the compiler at the time of writing.
- **Relevance to AuxFlow** — This anticipates a substantial share of AuxFlow's *framing*:
  - AuxFlow's "instance-level dependency graph whose nodes are auxiliary fact instances" —
    anticipated in spirit by per-`locate`-query observability comparison.
  - AuxFlow's "monotone fixpoint over pass numbers" — the fixpoint-on-positions framing is
    anticipated; the *static* propagation is not.
  - AuxFlow's BENIGN_CYCLIC vs AMPLIFYING distinction — anticipated **by example** (the TOC case
    and the growing-document case are exactly AuxFlow's two exemplars), but NOT as a formal
    classification or an analysis. AuxFlow's taint analysis (does a fact influence how much content
    is generated) is a genuine formalisation of a distinction Mädje only illustrates.
  - AuxFlow's source-level diagnosis naming the offending facts — partially anticipated by "a
    user-facing error message at the guilty locate call", though dynamically.
  - AuxFlow MUST NOT claim that document-convergence-as-fixpoint is a new framing, nor that the
    undecidability of the general problem is its own observation. It must cite this thesis for
    both, and position itself as the conservative-subset static counterpart.
- **Anticipation verdict** — PARTIAL OVERLAP, heavy. The strongest overlap found anywhere in
  Area B.
- **Evidence label** — SOURCED.

### B6. Typst documentation — "Compiler iterations"

- **Citation** — Typst documentation, *Context* reference page, section "Compiler iterations".
  Accessed 2026-08-27.
- **DOI / URL** — https://typst.app/docs/reference/context/
- **Access** — full page read.
- **Verbatim quote**:
  > "To resolve contextual interactions, the Typst compiler processes your document multiple times.
  > For instance, to resolve a `locate` call, Typst first provides a placeholder position, layouts
  > your document and then recompiles with the known position from the finished layout. The same
  > approach is taken to resolve counters, states, and queries. In certain cases, Typst may even
  > need more than two iterations to resolve everything. While that's sometimes a necessity, it may
  > also be a sign of misuse of contextual functions (e.g. of state). If Typst cannot resolve
  > everything within five attempts, it will stop and output the warning ``document did not
  > converge within five attempts.''"
- **Exact contribution** — Documents the shipped behaviour of a production typesetting system that
  (a) iterates the whole compilation to resolve document-level introspection, (b) caps iterations
  at five, and (c) emits an explicit non-convergence verdict.
- **What it does NOT do** — Does not predict the iteration count, does not analyse the source, and
  does not name the offending fact in the warning text (it only hints that misuse of `state` may be
  the cause). It also does not distinguish "needs a sixth iteration" from "will never converge".
- **Relevance to AuxFlow** — This is the strongest *deployed* competitor to AuxFlow's output
  contract. It already produces something close to AuxFlow's AMPLIFYING / UNKNOWN verdict, purely
  dynamically. AuxFlow's remaining differentiators against it are: static (no engine run), a
  predicted pass number rather than a cap, and a named offending fact.
- **Anticipation verdict** — PARTIAL OVERLAP (on the verdict; none on the analysis).
- **Evidence label** — SOURCED.

### B7. Scribble — four-pass document processing with a fixed-point traverse pass

- **Citation** — *Scribble: The Racket Documentation Tool*, §6.3 "Structures And Processing"
  (`scribble/core`), Racket 9.3 documentation. Accessed 2026-08-27.
- **DOI / URL** — https://docs.racket-lang.org/scribble/core.html
- **Access** — full page read.
- **Verbatim quote**:
  > "A document is processed in four passes:
  > – The traverse pass traverses the document content in document order so that information from
  > one part of a document can be communicated to other parts of the same document. The information
  > is transmitted through a symbol-keyed mapping that can be inspected and extended by
  > `traverse-element`s and `traverse-block`s in the document. The traverse pass iterates the
  > traversal until it obtains a fixed point (i.e., the mapping from one iteration is unchanged
  > from the previous iteration).
  > – The collect pass globally collects information in the document that can span documents that
  > are built at separate times, such as targets for hyperlinking.
  > – The resolve pass matches hyperlink references with targets and expands delayed elements
  > (where the expansion should not contribute new hyperlink targets).
  > – The render pass generates the result document."
- **Exact contribution** — A documented, deployed document-processing architecture with a
  *statically fixed* pass count (four) for the structural work, one of which is itself a
  fixed-point iteration over a document-level information mapping, plus an explicit design
  constraint that delayed-element expansion must not create new link targets — i.e. a language-level
  restriction imposed precisely to keep the pass structure sound.
- **What it does NOT do** — The four passes are fixed by design, not derived from the document. The
  traverse fixpoint is dynamic and uncapped. There is no analysis of the document's dependency
  structure, no per-fact graph, no SCC classification, and no diagnosis.
- **Relevance to AuxFlow** — Two points that matter. First, "how many passes does a document need"
  has been answered in the literature by *designing the answer into the language* (four, one of
  which loops) rather than by analysing documents. AuxFlow should acknowledge this as the
  language-design alternative. Second, the resolve-pass restriction ("expansion should not
  contribute new hyperlink targets") is a real precedent for a declared-subset restriction that
  bounds feedback — conceptually adjacent to AuxFlow's amplification restriction, arrived at by
  design rather than by analysis.
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B8. Gaspar — non-termination of the LaTeX cross-reference loop

- **Citation** — Jaime Gaspar. "Does not suffice to run latex a finite number of times to get
  cross-references right." *TUGboat* 35(1), 2014, "Letters" section. (The TUGboat title index
  capitalises the title as "…run LaTeX a finite number of times…"; the article itself prints
  lowercase "latex". A page number was not present in my extracted text; a sibling audit records
  it as p. 16.)
- **DOI / URL** — https://tug.org/TUGboat/tb35-1/tb109gaspar.pdf
- **Access** — full text (it is one page).
- **Verbatim quote**:
  > "Abstract. We present a LATEX file such that a cross-reference is wrong no matter how many
  > times we run latex."

  > "It is well-known that we need to run latex several times to get cross-references right. This
  > raises a natural question for mathematicians: for any LATEX file, does it suffice to run latex
  > a finite number of times? We show that the answer is negative, by a counterexample."

  > "This file uses a little diabolical trick: a label `l` is created in the last page (line 7) and
  > there are created (resorting to a for loop) `\pageref{l}` many new pages (lines 5 and 6),
  > causing the document to have `\pageref{l}` + 1 pages, so the cross-reference `\pageref{l}` to
  > the last page is wrong."
- **Exact contribution** — A published, minimal, reproducible counterexample (six lines, using
  `forloop` and `\pageref`) proving that no finite run count suffices for all LaTeX documents.
  The mechanism is exactly the one AuxFlow labels AMPLIFYING: an auxiliary page-number fact bounds
  a loop that generates pages.
- **What it does NOT do** — No analysis, no detection, no classification, no tool. It is a
  one-page letter establishing an existence result.
- **Relevance to AuxFlow** — Confirms established correction (5) with a primary source, and
  independently confirms that AuxFlow's AMPLIFYING category is a real, previously-published
  phenomenon with a canonical witness. AuxFlow should use this document as a test case and must not
  present the phenomenon as newly identified.
- **Anticipation verdict** — INFORMS ONLY (establishes the problem; does not attempt the analysis).
- **Evidence label** — SOURCED.
- **Note on modes** — Gaspar's example *diverges* (page count strictly increases by one per run;
  the equation p = p + 1 has no solution). The TeX FAQ case in B9 *oscillates* with period two.
  These are distinct non-convergence modes and a static analyser detects them by different means;
  they should not be conflated. Taxonomy of the modes is covered in the non-convergence area file,
  not here.

### B9. TeX FAQ — "Rerun messages won't go away"

- **Citation** — *The TeX FAQ*, entry "Rerun messages won't go away", FAQ ID `Q-rerun`
  (category: Usage). Maintained community FAQ, texfaq.org. Accessed 2026-08-27.
- **DOI / URL** — https://texfaq.org/FAQ-rerun
- **Access** — full entry.
- **Verbatim quote**:
  > "The LaTeX message ``Rerun to get crossreferences right'' is supposed to warn the user that the
  > job needs to be processed again, since labels seem to have changed since the previous run.
  > (LaTeX compares the labels it has created this time round with what it found from the previous
  > run when it started; it does this comparison at `\end{document}`.)"

  > "However, there *is* a rare occasion when this error can happen as a result of pathological
  > structure of the document itself. Suppose you have pages numbered in roman, and you add a
  > reference to a label on page ``ix'' (9). The presence of the reference pushes the thing
  > referred to onto page ``x'' (10), but since that's a shorter reference the label moves back to
  > page ``ix'' at the next run. Such a sequence can obviously not terminate."

  > "The only solution to this problem is to make a small change to your document (something as
  > small as adding or deleting a comma will often be enough)."
- **Exact contribution** — Documents (a) the exact semantics of the rerun comparison, matching the
  kernel source in B3, (b) that a broken package is the common cause, and (c) a period-two
  oscillation caused by a page reference whose *typeset width* changes the page it points at, which
  "can obviously not terminate".
- **What it does NOT do** — No formalisation, no detection, no tool. Explicitly offers only the
  human workaround of perturbing the source.
- **Relevance to AuxFlow** — A second independent primary source for non-convergence, and a
  significant *warning* for AuxFlow's model. The roman-numeral case oscillates because the *width*
  of the typeset reference changes the layout — a coupling through glyph metrics, not through
  content-generation count. AuxFlow's taint analysis, as described, separates facts by whether they
  influence *how much content the document generates*. This example generates no extra content; it
  changes the width of one reference. If AuxFlow's taint criterion is content quantity only, this
  document would be classified BENIGN_CYCLIC and AuxFlow would be wrong about it. That is a real
  soundness hazard, sourced, and it should be recorded as a required test case and possibly a
  reason to widen the taint criterion to "influences any layout-determining measurement".
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B10. TeX FAQ — "LaTeX gets cross-references wrong"

- **Citation** — *The TeX FAQ*, entry "LaTeX gets cross-references wrong", FAQ ID `Q-crossref`
  (category: Errors). Accessed 2026-08-27.
- **DOI / URL** — https://texfaq.org/FAQ-crossref
- **Access** — full entry.
- **Verbatim quote**:
  > "Sometimes, however many times you run LaTeX, the cross-references are just wrong. A likely
  > reason is that you have placed the label before the data for the label was set; if the label is
  > recording a `\caption` command, the `\label` command must appear *after* the `\caption`
  > command, or be part of it."

  > "In summary, the `\label` must be *after* the command that defines it (e.g., `\caption`), and
  > if the `\caption` is inside an environment, the `\label` must be in there too."
- **Exact contribution** — Documents the dominant *intra-run* ordering bug in the cross-reference
  system: `\label` captures whatever `\@currentlabel` happens to hold, so misplacement silently
  yields a wrong-but-stable reference.
- **What it does NOT do** — Nothing about convergence or pass counting. This class of bug converges
  perfectly and is still wrong.
- **Relevance to AuxFlow** — Sharpens AuxFlow's claim boundary. A CERTIFIED verdict from AuxFlow
  must not be read as "the references are correct"; it can at most mean "the fact values reach a
  fixpoint in N runs". This is an intra-run dataflow error (`\refstepcounter` → `\@currentlabel` →
  `\label`) that a fact-instance graph *could* also detect, and doing so would be a genuinely
  separate, arguably more valuable, contribution — but it is a different analysis from convergence
  and should be claimed separately if at all.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — SOURCED.

### B11. Asakura — the design concept for `llmk` (Light LaTeX Make)

- **Citation** — Takuto Asakura. "The design concept for `llmk` — Light LaTeX Make." *TUGboat*
  41(2), 2020, pp. 185–187, "Software & Tools".
- **DOI / URL** — https://tug.org/TUGboat/tb41-2/tb128asakura-llmk.pdf
- **Access** — full text.
- **Verbatim quote**:
  > "`max_repeat` (integer) sets the maximum number of repetitions. For various reasons, such as
  > solving cross-references, `llmk` has a feature to repeat command executions. This key exists to
  > prevent potential infinite loops. The default value is 5."

  and on the design contrast with latexmk and rubber:
  > "Their goals are to provide easy ways to process LaTeX documents; they guess how to process a
  > document by analyzing the log files, for instance, and implicitly determine the process. In
  > other words, they try hard to `hide' the specific workflow from users as much as possible."

  > "On the other hand, `llmk` takes a different approach: it requires users to explicitly show the
  > workflow to process a document either in an external configuration file (`llmk.toml`) or in a
  > `*.tex` file."
- **Exact contribution** — A published design rationale for LaTeX build automation as a subject in
  its own right: workflow reproducibility over inference. Its convergence handling is a
  user-settable repetition cap defaulting to 5, explicitly there "to prevent potential infinite
  loops".
- **What it does NOT do** — No static analysis, no dependency graph, no prediction. The pass count
  is a cap, and the author's own framing is that latexmk-class tools *infer* the workflow from logs
  while llmk deliberately does not infer at all.
- **Relevance to AuxFlow** — This is the published state of the art for the pass count in the LaTeX
  build-tool literature: a constant cap. AuxFlow's predicted pass number is a genuine functional
  difference. It is also a useful sourced data point that the published community view treats
  infinite loops as a real risk to be guarded with a magic number. (latexmk's own documented
  iteration cap and checksum mechanism is covered in the LaTeX-tools area file, not here.)
- **Anticipation verdict** — PARTIAL OVERLAP (occupies the same slot in the workflow; solves it by
  a cap, not analysis).
- **Evidence label** — SOURCED.

### B12. Brüggemann-Klein, Klein, Wohlfeil — "Pagination Reconsidered"

- **Citation** — Anne Brüggemann-Klein, Rolf Klein, Stefan Wohlfeil. "Pagination Reconsidered."
  *Electronic Publishing: Origination, Dissemination and Design* 8(2/3), 1995, pp. 139–152.
- **DOI / URL** — https://mirror.gutenberg-asso.fr/tex.loria.fr/typographie/brueggemann1995pagination2.pdf
  (author-format copy; also deposited at https://ub-deposit.fernuni-hagen.de/receive/mir_mods_00001036)
- **Access** — full text (author-format PDF; the volume/page metadata is not printed on this copy
  and is taken from the Bonn "Pagination of Complex Documents" project bibliography and from
  Venkatesan's TUGboat reference list, which agree).
- **Verbatim quote** (§1 Introduction):
  > "Whereas today's formatting systems provide acceptable or even excellent line breaking quality,
  > the quality of their page breaking leaves much to be desired."

  > "LaTEX maintains the correct order, but for positioning the floating objects a simple first-fit
  > strategy is employed. It places a floating object, once it has been cited, on the first page
  > where it fits."

  (§3 Measuring paginations):
  > "Currently, automated pagination routines use a first-fit approach, placing a figure on the next
  > page after its citation that has room for it. This greedy strategy is in conflict with the
  > other goal of good pagination, to always fill each page according to the design specification."

  (§1, on complexity):
  > "But expectations are dampened by the theoretical results by Plass [Pla81]; he proved that
  > optimal page breaking is in general NP-hard, hence computationally intractable."

  > "Plass has shown that this problem is NP-complete, but he has used a different framework: In
  > his model, figure references may cross and figures may also be placed on pages before their
  > citations."

  > "On the other hand, if one uses the sum of the page distances themselves, instead of their
  > squares, the optimization problem becomes computationally tractable, as Plass has also proved."
- **Exact contribution** — A dynamic-programming pagination algorithm minimising page turns, in
  O(mn) for constant page height, with a formal page model (text stream, figure stream, reference
  function R mapping each figure to its first citing line, page fullness bounds, sidedness). It
  also states precisely which pagination objective is NP-hard and which is tractable.
- **What it does NOT do** — This is entirely *within a single run*. Nothing about the `.aux` round
  trip, nothing about how many engine runs are needed, nothing about cross-reference convergence.
  Its "reference function" is figure-to-citing-line, not label-to-value.
- **Relevance to AuxFlow** — Three things:
  1. Sourced confirmation that LaTeX's float placement within a run is greedy first-fit, which is
     the mechanism by which a small fact change (a page number width) can shift a float and hence
     shift other facts. AuxFlow's dependency model needs this to be right.
  2. Sourced statement of Plass's complexity results, which AuxFlow should cite when discussing why
     pagination is not re-optimised globally.
  3. A caution: the pagination literature has *already* formalised document layout as an
     optimisation problem with a reference function. AuxFlow must be clear that its graph is over
     *auxiliary fact instances across runs*, not over layout objects within a run, or a reviewer
     will conflate the two.
- **Anticipation verdict** — ORTHOGONAL (within-run layout optimisation vs cross-run fact
  convergence), INFORMS ONLY on mechanism.
- **Evidence label** — SOURCED (for everything quoted); the Plass NP-hardness/NP-completeness claim
  itself is REPORTED, second-hand through this paper — see B13.

### B13. Plass — *Optimal Pagination Techniques for Automatic Typesetting Systems*

- **Citation** — Michael F. Plass. *Optimal Pagination Techniques for Automatic Typesetting
  Systems.* PhD thesis, Stanford University, 1981. Also Stanford Computer Science Department
  technical report STAN-CS-81-870. Primary advisor: Donald E. Knuth.
- **DOI / URL** — https://tug.org/docs/plass/plass-thesis.pdf ;
  catalogue record https://searchworks.stanford.edu/view/1013335
- **Access** — **METADATA ONLY.** The TUG-hosted PDF was fetched successfully but consists of 80
  scanned page images with no text layer; no text could be extracted or quoted. The Stanford
  SearchWorks record confirms "Thesis Ph. D. Stanford University 1981" and "Knuth, Donald Ervin,
  1938- primary advisor".
- **Verbatim quote** — NONE AVAILABLE from the primary source. The contribution is quoted
  second-hand from B12 and B18.
- **Exact contribution** (REPORTED) — First algorithmic treatment of optimal pagination with
  floating figures. Proved the quadratic-objective variant NP-complete and the linear-objective
  variant tractable.
- **What it does NOT do** — Single-run layout only. Nothing about multi-run document compilation.
- **Relevance to AuxFlow** — Only as the origin of the "pagination is hard" result. AuxFlow does
  not attempt pagination optimisation and should cite this only for context.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — SOURCED (bibliographic metadata) / REPORTED (content). **Do not quote this
  thesis in the AuxFlow write-up without obtaining a text-bearing copy.**

### B14. Knuth & Plass — "Breaking Paragraphs into Lines"

- **Citation** — Donald E. Knuth, Michael F. Plass. "Breaking Paragraphs into Lines." *Software:
  Practice and Experience* 11(11), 1981, pp. 1119–1184.
- **DOI / URL** — https://doi.org/10.1002/spe.4380111102 (DBLP records the DOI as
  `10.1002/SPE.4380111102`)
- **Access** — **METADATA ONLY**, DBLP-verified. Full text not retrieved (Wiley); the article is
  also reprinted in Knuth's *Digital Typography*.
- **Verbatim quote** — NONE. Not read.
- **Exact contribution** (REPORTED) — TeX's optimal line-breaking algorithm: total-fit dynamic
  programming over a paragraph with badness, penalties and demerits.
- **What it does NOT do** — Line breaking only; not page breaking, not multi-run compilation.
- **Relevance to AuxFlow** — Only as background for the asymmetry AuxFlow's framing leans on: line
  breaking is globally optimised per paragraph, page breaking is not. AuxFlow should NOT cite this
  paper for the single-pass page-breaking claim, because I could not verify a statement to that
  effect in it. Use B12, B15 and B18 instead, which are sourced.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — REPORTED.

### B15. Mittelbach — "Formatting documents with floats: A new algorithm for LaTeX2e"

- **Citation** — Frank Mittelbach. "Formatting documents with floats: A new algorithm for
  LaTeX2ε." *TUGboat* 21(3), September 2000 (Proceedings of the 2000 Annual Meeting), pp. 278–290.
- **DOI / URL** — https://tug.org/TUGboat/tb21-3/tb68mittel.pdf
- **Access** — full text; first 300 of 684 extracted lines read closely, remainder skimmed.
- **Verbatim quote**:
  > "One problem with formatting documents containing floats is the number of potential formatting
  > solutions that need to be checked out. The number of trials grows combinatorially in the number
  > of floats and areas which can receive them."

  > "For example, if we have 8 floats waiting to be distributed among 12 areas … then we have to
  > check 125970 possible distributions; if two additional floats appear we end up with 646646
  > trials."

  > "Thus it is important to find algorithms with complexity that is at worst linear in both the
  > number of floats on the trial list and the number of possible float areas, even if this means
  > that in a few cases a relatively good layout will not be found."

  > "The algorithm proceeds by taking the first float from the trial list and trying to place it
  > into the first float area from the area list. … A trial that does not fail means that this
  > distribution of floats becomes the best solution so far and all further trials will be based on
  > adding to this solution (**no backtracking**)."

  > "The document formatting is achieved using a minimal but customizable lookahead (typically the
  > considered galley material is the equivalent of one page/spread of textual material ignoring
  > the additional size taken up by embedded float objects)."

  (on footnote/float conflicts) > "However, checking for this would mean potentially large
  backtracking so the algorithm uses a conservative approach and simply considers a trial as
  failed if footnotes and bottom areas collide."
- **Exact contribution** — Specifies a replacement float-placement algorithm for LaTeX with an
  explicit design constraint of linear complexity and **no backtracking**, with bounded lookahead
  of roughly one page/spread, a formal area-naming scheme, float sequence classes, flush points, and
  grid alignment. The paper is itself typeset with a prototype of the algorithm.
- **What it does NOT do** — Entirely within-run. No `.aux`, no cross-run analysis, no pass counting.
- **Relevance to AuxFlow** — The best-sourced statement available of *why* LaTeX's page/float
  assembly is effectively a single forward pass with local lookahead and no backtracking. That is
  the mechanical substrate of AuxFlow's claim that a fact written late in run p can only be acted
  on in run p+1: within a run, the output routine cannot revisit an earlier decision. AuxFlow
  should cite this rather than gesturing at "TeX is single-pass".
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B16. Marriott, Moulder, Hurst — "Automatic float placement in multi-column documents"

- **Citation** — Kim Marriott, Peter Moulder, Nathan Hurst. "Automatic float placement in
  multi-column documents." *Proceedings of the 2007 ACM Symposium on Document Engineering
  (DocEng '07)*, pp. 125–134.
- **DOI / URL** — https://doi.org/10.1145/1284420.1284455 (DBLP-verified)
- **Access** — **METADATA ONLY**, DBLP-verified. Full text not retrieved (ACM).
- **Verbatim quote** — NONE. Not read.
- **Exact contribution** (REPORTED, via B18's citation) — Studies globally optimised float
  placement for multi-column layout using dynamic programming.
- **What it does NOT do** — Single-run layout.
- **Relevance to AuxFlow** — Context only. Confirms that the within-run layout optimisation problem
  has a mature academic literature that AuxFlow is *not* competing with.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — REPORTED (content), SOURCED (metadata).

### B17. Mittelbach — "A general framework for globally optimized pagination"

- **Citation** — Frank Mittelbach. "A general framework for globally optimized pagination."
  *Computational Intelligence* 35(2), 2019, pp. 242–284. Earlier version: "A General Framework for
  Globally Optimized Pagination", *Proceedings of the 2016 ACM Symposium on Document Engineering
  (DocEng '16)*.
- **DOI / URL** — https://doi.org/10.1111/coin.12165
- **Access** — **METADATA ONLY.** Wiley redirects non-cookie clients to
  `onlinelibrary.wiley.com/action/cookieAbsent`; no abstract obtainable. Volume/issue/pages come
  from a citation block on the Wiley landing page reachable via search
  ("Computational Intelligence 10.1111/coin.12165 35:2(242-284)"), i.e. publisher-sourced but not
  read by me on the article page itself.
- **Verbatim quote** — NONE. Not read.
- **Exact contribution** (REPORTED) — A framework for globally optimised pagination, extended in a
  later paper to automatic float placement.
- **What it does NOT do** — Single-run layout.
- **Relevance to AuxFlow** — Context only. Same caution as B12/B16: do not let a reviewer conflate
  within-run global pagination optimisation with cross-run fact convergence.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — REPORTED.

### B18. Venkatesan — "TeX as a three-stage rocket: Cookie-cutter page breaking"

- **Citation** — S. K. Venkatesan. "TeX as a three-stage rocket: Cookie-cutter page breaking."
  *TUGboat* 36(2), 2015, "Software & Tools". (Page numbers 145–148 appear in the extracted text;
  the article's opening page number was not captured, so the range is 144/145–148.)
- **DOI / URL** — https://tug.org/TUGboat/tb36-2/tb113venkatesan.pdf
- **Access** — full text.
- **Verbatim quote**:
  > "In a simple streaming-down process it is now possible to automatically decide the page breaks
  > and move the floats one-by-one as we paginate. … We call this simple methodology the
  > cookie-cutter algorithm and have applied for a patent, which is pending approval at the Indian
  > patent office [4]."

  > "After the fundamental work on automatic pagination by Plass [5], which showed that the optimal
  > solution to the float placement problem is NP-complete, this problem has been reconsidered in a
  > different light by Bruggemann-Klein et al. [6]. Mittelbach [7] implemented a new algorithm in
  > LATEX2ε and Marriott et al. [8] studied the problem for multicolumn layout."

  > "However, all these methods are quite complex and involve solving complex optimization problems
  > using a dynamic programming approach. Here, our cookie-cutter method [4] is not trying to solve
  > for a global optimum but instead implements a simple one-pass float placement algorithm that
  > seems to produce reasonable results for a large number of documents."
- **Exact contribution** — Proposes restructuring TeX as three stages: paragraph generation, one
  very long scroll page, then pagination by a "one-pass" cookie-cutter sweep. Provides a compact,
  reliable bibliography of the pagination-complexity literature.
- **What it does NOT do** — Nothing about cross-references, the `.aux` round trip, or run counts.
- **Relevance to AuxFlow** — (a) A second sourced statement that one-pass float placement is the
  practical approach; (b) the reference chain that let me verify B12/B13/B16; (c) a *patent flag* —
  the authors state they filed Indian patent application 3348/CHE/2015 covering
  "Transformation Of Marked-up Content To A Reversible File Format For Automated Browser Based
  Pagination". That is pagination, not pass counting, so almost certainly not blocking, but the
  patents area should be told it exists.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — SOURCED.

### B19. Liu, Li, Liu, Wu, Li — "LaTeX Compilation: Challenges in the Era of LLMs"

- **Citation** — Tianyou Liu, Ziqiang Li, Xurui Liu, Yu Wu, Yansong Li. "LaTeX Compilation:
  Challenges in the Era of LLMs." arXiv:2603.02873 [cs.CL], submitted 2026-03-03 (v4 read).
- **DOI / URL** — https://arxiv.org/abs/2603.02873 ; HTML full text
  https://arxiv.org/html/2603.02873v4
- **Access** — full text (HTML), read via targeted extraction of §2, §3.1, §3.3.1.
- **Verbatim quote** (§3.3.1, whose heading is "Multi-pass Compilation: A Fragile Stopgap"):
  > "In LATEX, the accurate generation of cross-references, tables of contents, and bibliographies
  > relies on multiple compilation passes to make up for the absence of internal state. The typical
  > workflow involves a first pass that generates auxiliary files (like .aux and .toc) to record
  > state, followed by subsequent passes that read these files to populate cross-references, page
  > numbers, or chapter titles."

  (§2):
  > "During the second pass, LATEX reads the .aux and .toc files generated previously, obtaining
  > complete numbering and directory information to typeset them correctly into the document. Thus,
  > the cross-references appear correctly, and the TOC is populated. This process demonstrates that
  > the LATEX typesetting process is essentially an iterative workflow that relies on intermediate
  > results to converge. Any feature involving global information or forward/backward dependencies
  > almost inevitably requires multiple compilation passes to produce the final correct output."

  (§3.1.2):
  > "Whether the structural node ``Appendix'' exists depends entirely on the truth value of a
  > condition at the moment of macro expansion. In other words, the document's logical structure is
  > not a stable, enumerable abstract tree, but a result dynamically generated during execution. Any
  > tool attempting to analyze the document structure without running TeX must completely simulate
  > macro expansion and conditional logic, which is virtually unfeasible in practice."

  > "First, static analysis tools find it difficult to intervene. Due to the lack of clear semantic
  > boundaries, tools cannot reliably construct an Abstract Syntax Tree (AST) or structural model,
  > making advanced features like code refactoring, semantic checking, and consistency verification
  > arduous to implement."
- **Exact contribution** — A critique of TeX's compilation architecture (batch model,
  unidirectional processing, coupling of expansion and semantics, lagged error localisation,
  multi-pass compilation as a "fragile stopgap") used to motivate an alternative WYSIWYG structured
  editor. Also reports compilation/rendering-time and LLM fine-tuning experiments.
- **What it does NOT do** — No analysis, no tool, no formalism. Multi-pass compilation is described
  and criticised, never modelled. It is a position paper with experiments about a different system.
- **Relevance to AuxFlow** — Two-edged and important:
  1. *Supports* AuxFlow's motivation: a 2026 published paper says in as many words that LaTeX
     compilation is "essentially an iterative workflow that relies on intermediate results to
     converge" and that multi-pass compilation is a fragile stopgap. That is a citable framing.
  2. *Attacks* AuxFlow's feasibility: it states that static analysis of LaTeX structure without
     running TeX is "virtually unfeasible in practice" because conditional expansion makes the
     structure dynamic. AuxFlow's declared-subset restriction is the answer to this, and AuxFlow
     must state that answer explicitly, in these terms, rather than ignoring the objection. It also
     means AuxFlow cannot claim to analyse arbitrary LaTeX; the subset restriction is load-bearing,
     not cosmetic.
- **Anticipation verdict** — INFORMS ONLY.
- **Evidence label** — SOURCED.

### B20. Knuth — "Twenty Questions for Donald Knuth" (on the absence of a formal semantics for TeX)

- **Citation** — Donald E. Knuth. "Twenty Questions for Donald Knuth, to celebrate the
  ePublication of TAOCP." *TUGboat* 35(3), 2014, pp. 235ff. Reprinted in TUGboat by permission of
  Pearson from informit.com.
- **DOI / URL** — https://tug.org/TUGboat/tb35-3/tb111knut-20.pdf
- **Access** — full text (first 300 of 422 extracted lines read; the relevant answer is #12, p. 239).
- **Verbatim quote** (answer 12, to Udi Manber, p. 239):
  > "Indeed, I myself follow the path of rigor only partway: Rarely do I ever give a formal proof
  > that any of my programs are correct, once I've constructed an informal proof that convinces me.
  > I have no real interest, for example, in defining exactly what it would mean for TEX to be
  > correct, or for verifying formally that my implementation of that 550-page program is free of
  > bugs."

  and, on the state of semantics generally:
  > "Thanks to the work of Floyd, Hoare, and others, we have formal definitions of semantics, and
  > tools by which we can verify that sorting is indeed always achieved."
- **Exact contribution** — Knuth's own on-record statement that he never defined what correctness
  would mean for TeX and had no interest in doing so.
- **What it does NOT do** — Not a research contribution on semantics; an interview answer.
- **Relevance to AuxFlow** — This is the best primary evidence available for the negative result
  that there is no formal semantics of TeX (see [Negative results](#negative-results)). It matters
  for AuxFlow because it means AuxFlow cannot ground its analysis in a published TeX semantics; the
  declared subset must come with its own semantics, defined by AuxFlow, and that definitional work
  is a legitimate and unclaimed contribution.
- **Anticipation verdict** — ORTHOGONAL (but load-bearing for the negative result).
- **Evidence label** — SOURCED.

### B21. Chen, Harrison, Minakata — "Incremental document formatting"

- **Citation** — Pehong Chen, Michael A. Harrison, Ikuo Minakata. "Incremental document
  formatting." *Proceedings of the ACM Conference on Document Processing Systems (DOCPROCS)*, 1988,
  pp. 93–100.
- **DOI / URL** — https://doi.org/10.1145/62506.62523 (DBLP-verified)
- **Access** — **METADATA ONLY**, DBLP-verified. ACM full text returned HTTP 403.
- **Verbatim quote** — NONE. Not read.
- **Exact contribution** (REPORTED) — Applies incremental-computation techniques to document
  formatting; the earliest identified academic treatment of incremental typesetting.
- **What it does NOT do** — Unknown in detail. On the basis of title and venue it concerns
  reformatting after edits, not multi-run convergence.
- **Relevance to AuxFlow** — Establishes that "incremental document formatting" as a research
  subject dates to 1988 and is essentially dormant thereafter (see negatives). Orthogonal to
  AuxFlow, which is about how many full runs are needed, not about reusing work across edits.
- **Anticipation verdict** — ORTHOGONAL (subject to the caveat that it has not been read).
- **Evidence label** — REPORTED.

### B22. Gobert & Beaudouin-Lafon — i-LaTeX

- **Citation** — Camille Gobert, Michel Beaudouin-Lafon. "i-LaTeX: Manipulating Transitional
  Representations between LaTeX Code and Generated Documents." *CHI Conference on Human Factors in
  Computing Systems (CHI '22)*, 2022, article 554, pp. 554:1–554:16.
- **DOI / URL** — https://doi.org/10.1145/3491102.3517494 (DBLP-verified); author copy reported at
  https://www.lri.fr/~gobert/papers/chi2022-ilatex.pdf
- **Access** — **METADATA ONLY**, DBLP-verified. Full text not retrieved.
- **Verbatim quote** — NONE. Not read.
- **Exact contribution** (REPORTED) — An HCI system introducing interactive "transitional"
  representations of LaTeX fragments so authors can manipulate output without a full recompile;
  evaluated with an interview study.
- **What it does NOT do** — Not a convergence or pass-count analysis.
- **Relevance to AuxFlow** — Confirms that "avoid the full recompile" is an active HCI research
  direction distinct from AuxFlow's. Also a possible venue signal: DocEng and CHI are where
  document-tooling work with an evaluation lands.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — REPORTED.

### B23. `memoize` — caching of LaTeX compilation results

- **Citation** — Sašo Živanović. *Memoize — Externalization of graphics and memoization of
  compilation results in general*, version 1.4.1, 2024-12-02. CTAN, `macros/generic/memoize`.
  LPPL 1.3c.
- **DOI / URL** — https://ctan.org/pkg/memoize ; documentation
  https://mirrors.ctan.org/macros/generic/memoize/doc/memoize-doc.pdf
- **Access** — CTAN package page read in full; the 2.9 MB documentation bundle was not opened.
- **Verbatim quote** (CTAN package description):
  > "Memoize is a package for externalization of graphics and memoization of compilation results in
  > general, allowing the author to reuse the results of compilation-intensive code. Memoize (i)
  > induces very little overhead, as all externalized graphics is produced in a single compilation.
  > It features (ii) automatic recompilation upon the change of code or user-adjustable context, and
  > (iii) automatic externalization of TikZ pictures and Forest trees, easily extensible to other
  > commands and environments. Furthermore, Memoize (iv) supports cross-referencing, TikZ overlays
  > and Beamer, (v) works with all major engines and formats, and (vi) is adaptable to any workflow."
- **Exact contribution** — Content-keyed caching of expensive *fragments* within LaTeX
  compilation, with invalidation on change of the fragment's code or a user-declared context.
- **What it does NOT do** — Caches fragments, not runs. Does not reduce or predict the number of
  engine runs; the cache key is code plus declared context, not a derived dependency set. The
  "user-adjustable context" is exactly the manual declaration of dependencies that a dependency
  analysis would automate.
- **Relevance to AuxFlow** — Adjacent but distinct. Notably, the fact that the *context* on which a
  memoised fragment depends has to be declared by hand is a small, concrete piece of evidence that
  automatic per-fragment dependency extraction for LaTeX is not solved practice. That is a supporting
  data point for AuxFlow's dependency-extraction component, though not for its convergence claim.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — SOURCED (package description).

### B24. Build-automation papers in the TUGboat literature (metadata-verified group)

- **Citations**, all verified against the TUGboat title index (issue, author, category, PDF path):
  - Paulo Cereda. "Arara — TeX automation made easy." *TUGboat* 39(2), 2018, "Software & Tools".
    https://tug.org/TUGboat/tb39-2/tb122cereda-arara.pdf
  - Heinrich Stamerjohanns. "Texmlbus, a build system to convert documents to XML and other
    formats." *TUGboat* 42(2), 2021, "Software & Tools".
    https://tug.org/TUGboat/tb42-2/tb131stamerjohanns-texmlbus.pdf
  - Joachim Schrod, Chris Rowley, Christine Detig. "A taxonomy of automated typesetting systems."
    *TUGboat* 27(0), 2006, "Talks". https://tug.org/TUGboat/tb27-0/schrod.pdf
  - Thomas Thurnherr. "An introduction to the LaTeX cross-referencing system." *TUGboat* 38(1),
    2017, "Tutorials". https://tug.org/TUGboat/tb38-1/tb118thurnherr.pdf (URL verified HTTP 200)
  - Paul A. Mailhot. "Implementing dynamic cross-referencing and PDF with PreTeX." *TUGboat*
    20(3), September 1999, "TeX in Publishing". https://tug.org/TUGboat/tb20-3/tb64mail.pdf
  - Chris Rowley, Frank Mittelbach. "The floating world." *TUGboat* 15(3), September 1994,
    "Futures". https://tug.org/TUGboat/tb15-3/tb44rowl.pdf
  - Jonathan Fine. "Line breaking and page breaking." *TUGboat* 21(3), September 2000, "Talks".
    https://tug.org/TUGboat/tb21-3/tb68fine.pdf
  - Jonathan Fine. "Galleys, space, and automata." *TUGboat* 14(3), October 1993, "Macro Writing".
    https://tug.org/TUGboat/tb14-3/tb40fine.pdf
- **Access** — **METADATA ONLY** for all eight (index-verified author/title/issue/PDF path). Only
  Asakura's llmk paper (B11) from this cluster was read in full.
- **Verbatim quote** — NONE for these eight.
- **Exact contribution** (REPORTED, from titles and index categories) — TeX build automation
  (arara, texmlbus), a taxonomy of automated typesetting systems, a tutorial on the
  cross-referencing system, dynamic cross-referencing in a commercial pipeline, and two
  discussions of the float/galley/page-breaking model.
- **What they do NOT do** — None is a convergence analysis or a static pass derivation. arara and
  texmlbus are workflow drivers in the same family as llmk.
- **Relevance to AuxFlow** — Defines the shape of the TUGboat literature AuxFlow sits in: tool
  descriptions and design notes, not analyses. Fine's two papers and Rowley & Mittelbach's "The
  floating world" are the most likely to contain a quotable statement about the galley/page-builder
  model and are worth reading before publication; they were not read here.
- **Anticipation verdict** — INFORMS ONLY (pending reading).
- **Evidence label** — REPORTED (metadata SOURCED from the TUGboat index).

### B25. Unverified and apparently erroneous citation: TeXpresso in TUGboat

- **Citation as reported** — F. Bour. "TeXpresso: Live rendering and error reporting for LaTeX."
  *TUGboat* 44(2):185–192, 2023, `tug.org/TUGboat/tb44-2/tb138bour-texpresso.pdf`. Reported in the
  reference list of a TUG 2026 preprint (Clemens Lode, "Real-Time LuaTeX: Recompiling Large
  Documents in 1ms", https://www.tug.org/tug2026/preprints/lode-realtime.pdf, which itself
  fetched HTTP 200, 388 KB, and was not read by me).
- **Access** — **COULD NOT VERIFY.**
- **Checks performed**:
  - `GET https://tug.org/TUGboat/tb44-2/tb138bour-texpresso.pdf` → HTTP 404.
  - `GET https://tug.org/TUGboat/tb44-3/tb138bour-texpresso.pdf` → HTTP 404.
  - TUGboat title index scanned for `/TeXpresso|presso/i` → no match.
  - TUGboat author index scanned for `Bour,` → no match (nearest entries: Boulanger, Bourgeois).
  - TUGboat 44:2 contents page scanned for "presso" → no match.
  - File-prefix check: TUGboat 44:2 uses the `tb137*` filename series and 44:3 uses `tb138*`;
    neither series contains a texpresso item.
  - DBLP query "TeXpresso live rendering LaTeX" → no hits.
- **Exact contribution** (REPORTED, from the project's own public description, not a paper) —
  Live rendering and immediate error reporting for LaTeX by keeping a checkpointed engine process
  alive, with Emacs and VS Code front ends.
- **Relevance to AuxFlow** — Peripheral (fast preview, not convergence). Recorded here because a
  published-looking TUGboat citation for it appears to be wrong, and the AuxFlow write-up must not
  propagate it. If TeXpresso needs to be cited, cite the project directly, not a TUGboat article.
- **Anticipation verdict** — ORTHOGONAL.
- **Evidence label** — **UNVERIFIED.**

### B26. Unverified: Haug — "Fast Typesetting with Incremental Compilation"

- **Citation as reported** — Martin E. Haug. *Fast Typesetting with Incremental Compilation.*
  Master's thesis, Technical University of Berlin, June 2022. Reported DOI 10.13140/RG.2.2.15606.88642.
- **Access** — **COULD NOT VERIFY.** ResearchGate returned HTTP 403; no institutional repository
  copy located; DBLP unreachable for this query during the session.
- **Exact contribution** (REPORTED) — An incremental parsing algorithm for off-side-rule markup
  syntax and a constrained layout-caching scheme that reuses prior layout elements even when the
  parent container's dimensions changed. Cited as a companion to Mädje's thesis (same institution,
  same year, same project).
- **Relevance to AuxFlow** — Potentially relevant: layout caching keyed on whether a change is
  *observable* is adjacent to Mädje's observability test and hence to AuxFlow's fact-instance
  granularity. Should be obtained and read before publication.
- **Anticipation verdict** — Cannot be assessed without the text.
- **Evidence label** — **REPORTED / UNVERIFIED.**

### B27. Reported only, not inspected: a cross-reference dependency-graph tool for LaTeX

- **Citation as reported** — "xreferences", described in a search result as a tool that "Builds a
  dependency graph from cross-references in LaTeX documents and outputs tikz-wrapped Dot files."
  https://github.com/thiagomael/xreferences
- **Access** — **NOT INSPECTED** (out of scope for this audit). Known only from a search-result
  description.
- **Relevance to AuxFlow** — Directly adjacent to AuxFlow's dependency-extraction component: if it
  does what the description says, then "extract a cross-reference dependency graph from LaTeX
  source" already exists as a non-academic artefact. This does NOT touch pass lag, fixpoint
  propagation, SCC classification, taint, or convergence, so it is not anticipation of the analysis
  — but AuxFlow should not claim that building a cross-reference graph from LaTeX is itself new.
- **Anticipation verdict** — Cannot be assessed without inspection; likely PARTIAL OVERLAP on graph
  extraction only.
- **Evidence label** — **REPORTED.** Must be inspected by whoever owns the tools survey before any
  novelty claim about graph extraction is made.

---

## Negative results

Exact queries that found nothing relevant. All are re-runnable.

**On static derivation of the number of engine runs (the core question):**
```
static analysis LaTeX compilation runs passes predict
LaTeX document compilation iterations static analysis determine
"LaTeX" "static analysis" "compilation passes" predict
static derivation dependency graph compilation passes document markup
number compilation passes needed dependency graph cross-references
LaTeX multiple passes cross-references resolution research
```
70 sources examined across these six. Nothing statically derives a run count for a document.
Every located mechanism is a dynamic loop with a cap: LaTeX's own `\@testdef` boolean (B3),
`rerunfilecheck`'s MD5 comparison (B4), `llmk`'s `max_repeat = 5` (B11), Typst's five-attempt cap
(B6), Scribble's fixed four passes with a dynamic traverse fixpoint (B7).

**On convergence of typesetting as a research subject:**
```
arXiv API: all:"incremental typesetting"                     -> 0 results
arXiv API: abs:"typesetting" AND abs:"convergence"           -> 0 results
arXiv API: all:"pagination" AND all:"NP-complete"            -> 1 result, unrelated (bin packing)
arXiv API: abs:"cross-reference" AND abs:"document" AND abs:"dependency" -> 6 results, all
                                                                LLM/retrieval, none relevant
DBLP: "Pagination reconsidered"                              -> 0 hits (EP-ODD not indexed)
DBLP: "TeXpresso live rendering LaTeX"                       -> 0 hits
```
arXiv contains no work on incremental typesetting or typesetting convergence. The only relevant
arXiv item in the whole area is 2603.02873 (B19), which is a position paper.

**On formal semantics / decidability of TeX:**
```
arXiv API: all:"TeX" AND all:"formal semantics"       -> 0 results
"formal semantics of TeX macro expansion"
"TeX Turing complete proof"
"TeX macro expansion Turing complete primitives proof"
"'formal grammar' LaTeX parsing research paper"
"site:tug.org TUGboat TeX formal semantics"
"DocEng proceedings LaTeX formal model cross-reference aux file"
"DocEng conference proceedings LaTeX template"
"'operational semantics' TeX macro expansion arxiv"
"static analysis type system LaTeX macros research"
"LaTeX macro type checking formal methods"
"TeX LaTeX static analysis verification"
"'decidability' TeX macros halting problem paper"
"'formal model' typesetting system 'multiple passes' document compilation research"
"TeXhackers grammar TeX tokenizer catcode formal model academic paper"
"TeX tokenizer catcode formal grammar academic"
"TeX catcode parsing formal model paper"
```
No peer-reviewed operational or denotational semantics of TeX. No academic Turing-completeness
proof (only blog posts, an Overleaf article, and a GitHub thread). No paper formalising the `.aux`
round trip or LaTeX counters as a formal system. No type system for TeX/LaTeX macros. The one
type-system hit was about the C preprocessor. Knuth's own disclaimer (B20) is the strongest primary
evidence for this negative.

**On incremental / cached / cloud compilation:**
```
Laurenz Maedje master's thesis Typst TU Berlin programmable markup language typesetting
Typst documentation iterative layout fixed point counters page numbers convergence
memoize LaTeX package CTAN documentation cache tikz
incremental typesetting recompilation research paper document formatting
"instant preview" TeX SyncTeX research paper fast preview typesetting
Overleaf cloud LaTeX compilation architecture technical report peer reviewed
i-LaTeX Gobert Beaudouin-Lafon interactive transitional interface paper
thesis "LaTeX" build system dependency graph scheduling PhD OR MSc
"document compilation" "build system" dataflow paper ACM DocEng
"document compilation build system dataflow ACM DocEng paper"
"ACM DocEng document compilation build system paper"
Haug "Fast typesetting with incremental compilation" TU Berlin master thesis pdf
"Incremental document formatting" Chatterjee Notkin DocEng 1988 ACM
```
Findings on the negatives:
- No peer-reviewed paper or technical report authored by Overleaf on their cloud compilation
  architecture. Only third-party mentions.
- **No MSc or PhD thesis specifically about LaTeX build automation, LaTeX dependency analysis, or
  document compilation scheduling exists as far as these queries can establish.** The closest items
  are Mädje's and Haug's theses, which are about designing a replacement typesetting system, and
  the Pluto build-systems paper, which uses LaTeX/BibTeX only as a worked example.
- "Incremental typesetting" as a research keyword is essentially empty between Chen/Harrison/
  Minakata 1988 (B21) and the two 2022 TU Berlin theses.
- The query `"Incremental document formatting" Chatterjee Notkin DocEng 1988 ACM` is recorded as a
  **failed hypothesis**: no such authors exist for that title; the correct authors are Chen,
  Harrison and Minakata.

**Path/fetch failures worth recording so they are not re-attempted blindly:**
```
https://texfaq.org/FAQ-multiruns                                          -> 404 (no such slug)
https://mirror.ctan.org/macros/latex/contrib/oberdiek/rerunfilecheck.dtx  -> 404 (moved)
http://i.stanford.edu/pub/cstr/reports/cs/tr/81/870/CS-TR-81-870.pdf      -> 404
http://infolab.stanford.edu/pub/cstr/reports/cs/tr/81/870/CS-TR-81-870.pdf-> 404
http://cajun.cs.nott.ac.uk/compsci/epo/papers/volume8/issue2/2point9.pdf  -> unreachable (timeout)
https://onlinelibrary.wiley.com/doi/10.1111/coin.12165                    -> cookie wall
https://dl.acm.org/doi/10.1145/62506.62523                                -> 403
https://www.researchgate.net/publication/364622490_...                    -> 403
http://tug.tug.org/docs/plass/plass-thesis.pdf                            -> 200 but scanned
                                                                             images, no text layer
```

**Adjacent items deliberately not pursued here** (owned by sibling audit areas, flagged to avoid
duplicate work): latexmk's documented iteration cap and checksum mechanism; Mittelbach's
"impossible document" answer and the TeX.SE oscillation examples; arXiv:2601.15294 "KnowTeX:
Visualizing Mathematical Dependencies"; Erdweg/Lichter/Weiel's Pluto (OOPSLA 2015), which
reportedly analyses the LaTeX/BibTeX aux-file cycle as a build-scheduling problem; Mokhov/Mitchell/
Peyton Jones "Build Systems à la Carte"; the Indian patent application 3348/CHE/2015 noted in B18.

---

## Summary for the audit

- **The `.aux` round trip and the rerun warning are now established from primary source, not
  memory.** `ltxref.dtx` gives the record format written by `\label`; `ltfiles.dtx` shows
  `\begin{document}` reading the previous run's aux *before* reopening it for writing (the
  mechanical proof of AuxFlow's pass lag of 1); `ltmiscen.dtx` gives `\@testdef`, the single global
  `\@tempswa` boolean, both rerun warning strings, and the kernel's own comment that the warning is
  deliberately suppressed when labels are multiply defined.

- **`rerunfilecheck` is a quotable, primary admission that base LaTeX's warning is insufficient:**
  "this rerun warnings are not given for the table of contents and other data stored in the aux
  files or other auxiliary files." Its answer is MD5 checksums per file — the practical baseline.
  Established corrections 3 and 4 are now fully sourced.

- **The single most dangerous piece of prior art in Area B is Mädje's MSc thesis (TU Berlin, 2022),
  §6.3, pp. 48–51.** It names intra-document dependencies as cyclic, gives AuxFlow's benign
  (TOC-shifts-heading) and amplifying (page-count-grows) exemplars as worked examples, formalises
  stability as convergence of a recurrence relation, **proves via Rice's theorem that it is
  undecidable for arbitrary code**, proposes a per-query *observability* test instead of
  whole-state comparison, and prescribes a constant iteration cap plus "a user-facing error message
  at the guilty locate call". AuxFlow must cite this and must not claim the fixpoint framing, the
  undecidability observation, the benign/amplifying examples, or the idea of naming the guilty
  construct.

- **What survives of AuxFlow's novelty after Mädje, in this area:** doing it *statically*, on LaTeX
  rather than a purpose-built language, over a *declared subset* on which the analysis is sound;
  turning the benign/amplifying distinction from two illustrative examples into a decision
  procedure via taint on content generation; emitting a *predicted pass count* rather than a cap;
  and naming the offending fact instances without running the engine. That is a narrower but real
  and defensible claim. Nothing broader will survive review.

- **Typst's shipped behaviour is the closest deployed competitor to AuxFlow's output contract:**
  documented five-attempt cap and the warning "document did not converge within five attempts".
  AuxFlow's AMPLIFYING/UNKNOWN verdicts are not a new *kind* of output; only the way they are
  derived is new.

- **Non-convergence of LaTeX is published twice over, in two distinct modes.** Gaspar (TUGboat
  35:1, 2014) gives a six-line `forloop` + `\pageref` counterexample that *diverges*; the TeX FAQ
  entry `Q-rerun` gives a roman-numeral page-number case that *oscillates* with period two and
  states that "such a sequence can obviously not terminate". Established correction 5 is sourced.

- **The FAQ oscillation case is a soundness hazard for AuxFlow's taint criterion as currently
  described.** It generates no extra content; it changes the *typeset width* of one reference, which
  moves a page break. A taint criterion restricted to "influences how much content the document
  generates" would misclassify it BENIGN_CYCLIC. Either widen the criterion to any
  layout-determining measurement, or state the limitation explicitly and add this document as a
  known-limitation test case.

- **The published state of the art for the pass count in the LaTeX build-tool literature is a
  constant.** `llmk` (TUGboat 41:2, 2020): "`max_repeat` … exists to prevent potential infinite
  loops. The default value is 5." Typst: five. Scribble: four fixed passes, one of which loops.
  Nobody derives the number.

- **Scribble is the language-design alternative AuxFlow should acknowledge.** Racket's
  documentation tool declares four passes by construction, runs the traverse pass to a fixed point,
  and imposes a language-level restriction that resolve-pass expansion must not create new
  hyperlink targets — a real precedent for restricting feedback by design rather than analysing it.

- **There is no formal semantics of TeX, and Knuth said so himself** (TUGboat 35:3, p. 239: "I have
  no real interest … in defining exactly what it would mean for TEX to be correct"). AuxFlow
  therefore cannot lean on an existing semantics; defining one for its declared subset is
  unclaimed, necessary work and is a legitimate contribution in its own right.

- **A 2026 arXiv position paper both helps and attacks AuxFlow.** It supplies the citable framing
  that "the LaTeX typesetting process is essentially an iterative workflow that relies on
  intermediate results to converge" and heads its section "Multi-pass Compilation: A Fragile
  Stopgap". It also asserts that analysing LaTeX structure without running TeX is "virtually
  unfeasible in practice" because conditional expansion makes the structure dynamic. AuxFlow's
  declared-subset restriction is the only answer to that objection and must be stated as such.

- **The pagination literature is orthogonal but must be cited carefully.** Plass (Stanford PhD,
  1981) on NP-hardness; Brüggemann-Klein/Klein/Wohlfeil (EP-ODD 8(2/3), 1995) on LaTeX's first-fit
  greedy placement and the exact complexity split; Mittelbach (TUGboat 21:3, 2000) on "no
  backtracking" and bounded lookahead; Venkatesan (TUGboat 36:2, 2015) on "a simple one-pass float
  placement algorithm"; Marriott et al. (DocEng '07) and Mittelbach (Comp. Intelligence 35(2),
  2019) on global optimisation. All of it is *within a single run*. It gives AuxFlow its sourced
  basis for "a fact written late in run p can only be acted on in run p+1", and it is the most
  likely thing a reviewer will confuse AuxFlow with. Say the difference explicitly.

- **Two bibliographic warnings.** (1) The Plass thesis PDF at tug.org is scanned images with no
  text layer — do not quote it; the NP-completeness claim in this file is REPORTED via
  Brüggemann-Klein et al. (2) A TUG 2026 preprint cites "Bour, TeXpresso, TUGboat 44(2):185–192,
  2023" at a URL that 404s, and no such article exists in the TUGboat title index, author index, or
  either candidate issue's file list. Do not propagate that citation.

- **Genuine gap in the literature, worth stating as such in the paper:** no MSc/PhD thesis and no
  peer-reviewed paper on LaTeX build automation, LaTeX dependency analysis, or document compilation
  scheduling was located. "Incremental typesetting" as a research keyword is empty between 1988 and
  2022. The subject AuxFlow is entering is, in the academic record, close to unoccupied — which is
  itself a reason to be suspicious and to have checked the adjacent fields (attribute grammars,
  build systems) as hard as this audit checked this one.
