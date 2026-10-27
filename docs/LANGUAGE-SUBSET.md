# Language subset

AuxFlow analyses a **declared subset of LaTeX**. It does not implement TeX and does not attempt
to.

Two constraints shape the subset:

1. Every corpus document must compile under a stock engine, so that dynamic baselines can be
   measured on exactly the same input.
2. The subset must be expressive enough to construct forward dependencies, backward
   dependencies, dependency chains, generated-state dependencies, cycles, converging cases and
   non-converging cases — otherwise the research question cannot be tested.

Anything outside the subset has **defined behaviour**: it becomes opaque, and the analysis
degrades conservatively. It is never guessed at.

## Required

| Construct | Why it is required |
|---|---|
| `\documentclass{...}` | Establishes counters and sectioning; identifies class-provided facts |
| `\usepackage{...}[opts]` | Package identity determines which fact kinds can exist |
| `\input{f}` | File inclusion without a page break; builds the inclusion graph |
| `\include{f}` | File inclusion with an implicit page break |
| `\label{k}` | Produces the primary fact |
| `\ref{k}` | Consumes the number component; both directions |
| `\pageref{k}` | Consumes the page component; the origin of page feedback |
| `\vref{k}` with `varioref` | Reads a label page; its dynamic text extent is not modelled |
| `\cite{k}` and variants | Produces a citation fact; drives the external tool edge |
| `\bibliography{f}`, `\bibliographystyle{s}` | Produces bibliography state through an external tool |
| `\tableofcontents` | Generated state whose page footprint shifts pagination |
| `\listoffigures`, `\listoftables` | The same mechanism with distinct fact kinds; tests generality |
| `\chapter`, `\section`, `\subsection` | Produce list entries; advance counters |
| `figure`, `table` environments, `\caption` | Produce list entries; carry labels |
| `\includegraphics{f}` | A file dependency with no auxiliary fact |
| `%` comments, `\%` | Lexer correctness; a classic source of silent mis-parsing |
| `\verb`, `verbatim` | Must be *recognised in order to be skipped*, or the lexer mis-tokenises |
| `\newcommand`, `\renewcommand` | Recorded, never expanded (see below) |
| `\newcounter`, `\setcounter`, `\value` | Required to express the amplifying-cycle class |
| `\forloop`, `\whiledo` | The content-generating control constructs |
| `\newpage`, `\clearpage` | Content-quantity primitives; targets of the taint analysis |

The last three rows exist for one reason: **without a construct whose repetition count can
depend on a fact value, the non-convergence class cannot be written down, and the project's
central claim cannot be tested.** They are part of the subset because the research requires
them, not because documents commonly use them.

### Macro definitions

`\newcommand` and `\renewcommand` are **recorded in the symbol table and never expanded**. The
body is stored as a token list. If the body contains any modelled construct, the macro is marked
opaque and every call site inherits that opacity.

This is a deliberate under-approximation. Expanding macros correctly requires a TeX interpreter;
expanding them incorrectly would produce an unsound analysis while looking like a feature.
Recording without expanding is honest and its consequences are visible in the classification.

## Optional

Implemented only if the schedule allows. Each adds a distinct mechanism rather than more of the
same.

| Construct | What it adds |
|---|---|
| `\includeonly{...}` | Selective compilation; prerequisite for incremental invalidation |
| `\pageref{LastPage}` | A well-known boundary case between benign and amplifying feedback |
| `\index`, `makeindex` | A second external tool edge, confirming the tool-lag model generalises |
| `longtable` | Width feedback — a convergence mechanism unrelated to pagination |

## Unsupported

| Construct | Behaviour | Why |
|---|---|---|
| Category-code redefinition | opaque | Would require a TeX interpreter; invalidates the lexer's own assumptions |
| `\csname` / `\expandafter` | opaque | Control-sequence names not statically determinable |
| Conditional expansion altering reference structure | opaque | Requires evaluation |
| `\write18` / shell escape | opaque, and disabled at execution | Out of scope |
| Arbitrary package internals | opaque | Unbounded surface |
| TikZ externalisation | opaque | Communicates through auxiliary side-channels the model does not track |
| Anything else not listed above | opaque | Default-deny |

The list is default-deny: a construct is supported only if it appears in the Required or
Optional table.

## Fallback rule

Non-negotiable, and implemented before any parser code.

When the parser meets a construct outside the subset it emits `Opaque(span, reason)`. From
there:

1. An opacity marker in file *f* makes every fact originating in *f* carry `opaque = true` with
   value unknown. **Facts are never silently dropped** — dropping a fact would remove edges and
   could shorten the derived plan, which is the one failure mode that can corrupt a document.
2. Any unknown value reaching the ARG removes the document from the certified state; it becomes
   `UNKNOWN`.
3. `UNKNOWN` emits the conservative default plan and relies entirely on runtime verification.
4. **AuxFlow never emits a plan shorter than the conservative default for a document that is not
   certified.**

Rule 4 is what makes "AuxFlow cannot cause a wrong document" true rather than aspirational. It
is enforced by a property test over randomly generated classifications, not merely by review.

### Granularity

Currently specified as **whole-document**: any opacity anywhere downgrades the entire document.
Per-file granularity would be more useful and is recorded as open decision D11 in
[PROJECT.md](PROJECT.md). Adopting it requires an argument that opacity cannot leak across an
inclusion boundary, which is not obviously true — an opaque macro defined in one file can be
called in another.

## Dependency structures the subset can express

Each row is a structure the research question requires, together with the constructs that
produce it. This table is the justification for the subset's contents.

| Structure | Constructs | Corpus member |
|---|---|---|
| Backward dependency | `\label` then later `\ref` | b02 |
| Forward dependency | `\ref` then later `\label` | b03 |
| Dependency chain | contents extent to pagination to page reference; citation to bibliography adds tool lag | b04, b06 |
| Generated-state dependency | `\tableofcontents` with sectioning | b05 |
| External tool dependency | `\cite` with `\bibliography` | b06 |
| Multiple interacting lists | `\tableofcontents`, `\listoffigures`, `\listoftables` | b09 |
| Benign cycle | any generated list plus `\pageref` | b05, b09 |
| Amplifying cycle | `\forloop` bounded by `\pageref`, generating `\newpage` | b08 |
| Opaque fallback | unsupported footnote, changing generated state, `biblatex` | b07, b10, b15 |
| Conditional on a reference value | `\ifthenelse` selecting differently sized content on `\pageref` | b14 |
| Extent feedback — **not modelled** | resolved reference width changing a line break | b11 |
| Float placement feedback — **not modelled** | `[!t]` float with roman page numbering | b12 |
| Dynamic textual reference — **not modelled** | `varioref` text shifts a reference across a page break relative to a float | b13 |
| Footnote extent feedback — **not modelled** | page reference in a footnote changes its own page placement | b07 |
| Nondeterministic generated state — **out of model** | fresh auxiliary value each engine run | b10 |
| Same-page citation feedback — **refused, not modelled** | `biblatex` `ibid` across a page break | b15 |

The `b11`–`b13` cases recognise reference syntax but do not model typeset extent.
Modelling that extent requires line breaking, which is out of scope. Treating every rendered value
as pagination-affecting makes the analysis vacuous. `b07` and `b15` instead remain opaque and
are refused under strict mode. These cases state the subset boundary by convergence mechanism.

### Inert packages and commands

Some packages and commands write no auxiliary or cross-reference state. AuxFlow treats them as inert and does not mark a document UNKNOWN for using them. The packages are `inputenc`, `fontenc`, `ae`, `aecompl`, `lmodern`, `xcolor`, `parskip`, `geometry`, `setspace`, `multicol`, and `amsmath`. The commands are listed in `_INERT_COMMANDS` in `src/auxflow/ir/graph.py`. `\eqref` resolves like `\ref`. A local macro is inert only if every command in its body is inert. These constructs can still change pagination. The ARG does not model that, as with all layout.

The allowlist is part of the stated language subset from v0.1.0. Additions are breaking changes to the analysis contract: a package added to the allowlist can cause a document that was previously UNKNOWN to become CERTIFIED. Removals are also breaking: a document that was CERTIFIED may become UNKNOWN. Both directions require a minor version increment.

A page reference under `roman`, `Roman`, `alph`, or `Alph` page numbering makes the document UNKNOWN. The numeral width changes with its value, which can move line breaks and the reference's own target (b11, b12). `\vref` and `\vpageref` also make a document UNKNOWN (b13). References under arabic numbering are not treated this way, so b03 and b09 stay CERTIFIED.

## Diagnosing larger projects

`auxflow check` lists unmodelled packages declared directly in the document and packages
loaded by a local class or local package file. These warnings report declarations only.
They do not prove the package's macros or layout effects are safe.

The classifier reports repeated unsupported constructs by name and occurrence count.
Use `auxflow classify -v FILE` for each source location. A local unmodelled class
makes a document UNKNOWN even when its main `.tex` file uses only supported commands.
An external class that AuxFlow cannot inspect also remains outside the stated model.

The package inventory does not parse installed TeX packages or cache dependency
graphs. A package's presence on a machine does not establish its convergence
behavior. Project graphs depend on local document content and must be rebuilt
when that content changes.
Do not interpret a CERTIFIED result as a guarantee about arbitrary class internals.

Literal commands inside `verbatim` and `lstlisting` do not produce reference facts.
`lstlisting` remains an unmodelled environment, so its document can still be UNKNOWN.
Graphic files can be referenced relative to the entry document or the including file.
`auxflow check` reports a missing graphic only when neither location has the file.

## Non-goals for the subset

- Not a specification of LaTeX, nor a subset anyone else should adopt.
- Not intended to grow toward full coverage. Growth is measured in *mechanisms* modelled, not in
  constructs recognised; adding twenty more macros that all produce label facts would add
  nothing.
- Not a validator. `auxflow check` reports defects it can see, but a document passing it is not
  thereby guaranteed to typeset.
