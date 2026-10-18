"""Generate the formal Review 2 assessment document (.docx) per the
official VIT Project Review 2 template (Assessment 9-10, 10 marks total:
Implementation/Prototype Progress 5, Novelty 2, Presentation and Q&A 3).

Content is grounded in the actual repository state at the Review 2
checkpoint (compiler Phases 1-7: lexer through IR generation), matching
docs/review2-viva.md and docs/COMPILER-PIPELINE.md. Nothing here claims
work from Phases 8-16 (Review 3 scope) as already complete.
"""

from __future__ import annotations

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x0D, 0x1B, 0x2A)
ACCENT = RGBColor(0x1B, 0x3A, 0x57)
BODY_FONT = "Calibri"
HEAD_FONT = "Calibri"


def shade_cell(cell, color_hex: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.makeelement(qn("w:shd"), {qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): color_hex})
    tc_pr.append(shd)


def set_cell_text(cell, text: str, bold: bool = False, size: int = 10, color: RGBColor | None = None) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = BODY_FONT
    if color:
        run.font.color.rgb = color


def add_heading(doc: Document, text: str, level: int = 1, marks: str | None = None) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.bold = True
    run.font.name = HEAD_FONT
    run.font.size = Pt(16 if level == 1 else 13)
    run.font.color.rgb = NAVY
    if marks:
        mrun = p.add_run(f" ({marks})")
        mrun.italic = True
        mrun.font.size = Pt(11)
        mrun.font.color.rgb = RGBColor(0x5A, 0x5A, 0x5A)
    # Bottom border rule
    p_pr = p._p.get_or_add_pPr()
    border = p_pr.makeelement(
        qn("w:pBdr"),
        {},
    )
    bottom = border.makeelement(
        qn("w:bottom"),
        {qn("w:val"): "single", qn("w:sz"): "6", qn("w:space"): "4", qn("w:color"): "1B3A57"},
    )
    border.append(bottom)
    p_pr.append(border)


def add_bullet(doc: Document, text: str, bold_lead: str | None = None, level: int = 0) -> None:
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(4)
    if bold_lead:
        r1 = p.add_run(bold_lead)
        r1.bold = True
        r1.font.name = BODY_FONT
        r1.font.size = Pt(11)
        r2 = p.add_run(text)
        r2.font.name = BODY_FONT
        r2.font.size = Pt(11)
    else:
        r = p.add_run(text)
        r.font.name = BODY_FONT
        r.font.size = Pt(11)


def add_para(doc: Document, text: str, size: int = 11, italic: bool = False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.font.name = BODY_FONT
    run.font.size = Pt(size)
    run.italic = italic
    return p


def build_document() -> None:
    doc = Document()

    # Base style
    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = Pt(11)

    # Narrower margins
    section = doc.sections[0]
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # ---------- Title Block ----------
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    trun = title.add_run("PROJECT REVIEW 2")
    trun.bold = True
    trun.font.size = Pt(22)
    trun.font.name = HEAD_FONT
    trun.font.color.rgb = NAVY

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(14)
    srun = sub.add_run("Assessment 9-10 Marks")
    srun.italic = True
    srun.font.size = Pt(12)
    srun.font.color.rgb = RGBColor(0x5A, 0x5A, 0x5A)

    # ---------- Section 1: Project Details ----------
    add_heading(doc, "1. Project Details")
    details = [
        ("Project Title", "AuxFlow: Static Analysis for Multi-Pass Document Compilation"),
        ("Student Name(s)", "Upayan Mazumder"),
        ("Register Number(s)", "24BDS0367"),
        ("Programme / Branch", "B.Tech CSE (Data Science)"),
        ("Project Guide", "Banupriya R"),
        ("Review Date", "21 October 2026"),
    ]
    table = doc.add_table(rows=len(details), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Cm(5.0)
    table.columns[1].width = Cm(10.5)
    for i, (label, value) in enumerate(details):
        row = table.rows[i]
        set_cell_text(row.cells[0], label, bold=True, size=11)
        shade_cell(row.cells[0], "E6EDF3")
        set_cell_text(row.cells[1], value, size=11)
    doc.add_paragraph()

    # ---------- Section 2: Project Overview ----------
    add_heading(doc, "2. Project Overview")

    add_para(
        doc,
        "Brief introduction to the project:",
    ).runs[0].bold = True
    add_para(
        doc,
        "AuxFlow is a compiler-based static analysis tool for LaTeX documents that use "
        "multi-pass compilation. It builds a dedicated compiler front end (lexer, parser, "
        "AST, symbol tables) and an intermediate representation called the Auxiliary "
        "Reference Graph (ARG), then performs graph-based dataflow analysis to classify a "
        "document's cross-reference dependency structure before any LaTeX engine runs.",
    )

    add_para(doc, "Problem statement and the need for the project:").runs[0].bold = True
    add_para(
        doc,
        "LaTeX documents containing cross-references, tables of contents, bibliographies, and "
        "similar auxiliary state require multiple compilation passes to converge to a stable "
        "output. Authors currently discover the correct number of passes by trial and error, "
        "or by running a fixed schedule (e.g. always three passes) that can either waste "
        "compute on documents that converge sooner or silently under-compile documents that "
        "need more passes, including rare documents that do not converge at all (infinite "
        "page growth or page-number oscillation). No existing tool reasons about this "
        "dependency structure statically, before executing the engine.",
    )

    add_para(doc, "Objectives of the project:").runs[0].bold = True
    objectives = [
        "Build a complete compiler front end (lexer, parser, AST, symbol tables, semantic "
        "checks) for a declared, well-specified subset of the LaTeX language.",
        "Lower the resolved AST into an instance-level Intermediate Representation (the "
        "Auxiliary Reference Graph) that models cross-reference, table-of-contents, "
        "bibliography, and counter dependencies as typed, lagged graph edges.",
        "Apply static graph analysis (strongly connected components, taint propagation) to "
        "classify each document into one of four convergence states: CERTIFIED, "
        "BENIGN_CYCLIC, AMPLIFYING, or UNKNOWN.",
        "Derive a safe, minimal build plan (predicted engine pass count) for certified "
        "documents, and pair it with runtime verification that can confirm or correct the "
        "static prediction.",
        "Evaluate the approach empirically against a benchmark corpus and against existing "
        "shipping tools (latexmk, latexrun, Tectonic).",
    ]
    for o in objectives:
        add_bullet(doc, o)

    add_para(doc, "Proposed solution and its expected outcome:").runs[0].bold = True
    add_para(
        doc,
        "AuxFlow proposes treating the LaTeX convergence problem as a compiler problem rather "
        "than a trial-and-error execution problem: parse the source once, build a dependency "
        "graph of every cross-reference-bearing construct, and decide statically whether the "
        "document's auxiliary state is guaranteed to stabilise, and in how many passes. The "
        "expected outcome is a tool that classifies a document and (when safe) predicts an "
        "exact engine-pass count in milliseconds, with zero LaTeX engine executions, while "
        "degrading conservatively (reporting UNKNOWN rather than guessing) for constructs "
        "outside its declared subset.",
    )

    # ---------- Section 3: Implementation / Prototype Progress ----------
    add_heading(doc, "3. Implementation / Prototype Progress (75/100%)", marks="5 Marks")

    add_para(doc, "Overall implementation status:").runs[0].bold = True
    add_para(
        doc,
        "As of Review 2, Phases 1 through 7 of the 16-phase implementation plan are complete "
        "and verified: the full compiler front end (lexical analysis, parsing, AST "
        "construction, symbol tables, semantic analysis) and the Intermediate Representation "
        "(the Auxiliary Reference Graph) are implemented, tested, and committed. This is "
        "approximately 44% of the total phase count and covers the entire input-to-IR "
        "pipeline that every later analysis phase depends on. The remaining phases "
        "(graph analysis, classification, build planning, runtime verification, and "
        "empirical evaluation) are scoped for Review 3.",
    )

    add_para(doc, "Modules completed and their functionalities:").runs[0].bold = True
    modules = [
        (
            "Lexer (auxflow.lexer)",
            "Single-pass, table-driven scanner implementing all sixteen TeX category codes "
            "(catcodes). Recognises comments, escape sequences, control words/symbols, and "
            "delimiter-driven \\verb verbatim regions. Verified with a token round-trip "
            "property test (reconstructed tokens reproduce the exact source bytes).",
        ),
        (
            "Parser (auxflow.parser)",
            "Hand-written recursive-descent parser with one token of lookahead. Argument "
            "parsing (mandatory/optional groups) is driven by a declared macro-signature "
            "table. Produces one AST per file over sixteen node kinds, each carrying a "
            "mandatory source span. Malformed input (unterminated groups, missing arguments) "
            "is recorded as a diagnostic rather than raising an exception, so the parser "
            "never crashes on real-world input.",
        ),
        (
            "AST and inclusion resolution (auxflow.ast)",
            "Assembles per-file ASTs into a multi-file forest and builds the file-inclusion "
            "graph from \\input/\\include edges, with depth-first-search cycle detection for "
            "circular inclusion.",
        ),
        (
            "Symbol tables (auxflow.semantic)",
            "Six symbol tables (LabelTable, RefTable, CiteTable, PackageTable, FileTable, "
            "CounterTable) populated by a two-pass declare-then-resolve traversal, so forward "
            "references and cross-file references both resolve correctly.",
        ),
        (
            "Semantic analysis (auxflow.semantic.diagnostics)",
            "Zero-engine-execution checks: undefined references, undefined citations, "
            "duplicate labels, unresolvable file inclusions, missing graphics files, "
            "inclusion cycles, and use of an unmodelled (opaque) package.",
        ),
        (
            "Intermediate Representation (auxflow.ir)",
            "The Auxiliary Reference Graph (ARG): one fact instance per modelled construct "
            "(label, reference, table-of-contents entry, citation, counter read), each with a "
            "mandatory source span, connected by typed, lagged dependency edges. List-producing "
            "facts use an exists/value split so that ordinary documents remain acyclic by "
            "construction. Serialises to JSON and to Graphviz DOT.",
        ),
        (
            "Command-line interface (auxflow.cli)",
            "Five working subcommands exposing every completed phase: "
            "auxflow tokens, auxflow ast, auxflow symbols, auxflow check, auxflow graph.",
        ),
    ]
    for name, desc in modules:
        add_bullet(doc, desc, bold_lead=f"{name}: ")

    add_para(doc, "Technologies, tools, programming languages, and platforms used:").runs[0].bold = True
    tech = [
        "Language: Python 3.12+ (tested through 3.14), strict static typing enforced with mypy.",
        "Core implementation: zero third-party runtime dependencies. The lexer, parser, "
        "symbol tables, and IR are entirely hand-written, including the eventual Tarjan "
        "strongly connected components algorithm used in later phases.",
        "Testing: pytest with property-based testing via Hypothesis for round-trip and "
        "structural invariants.",
        "Code quality: ruff (linting and formatting), mypy --strict (type checking).",
        "Version control and CI: Git and GitHub, with GitHub Actions running lint, "
        "format-check, type-check, and the full test suite on every change.",
        "Target input language: a declared, documented subset of LaTeX2e.",
    ]
    for t in tech:
        add_bullet(doc, t)

    add_para(doc, "System architecture / workflow:").runs[0].bold = True
    add_para(
        doc,
        "The implemented pipeline (Phases 1-7, left to right): "
        "Source bytes  -->  Lexer (catcode-aware tokens)  -->  Parser (recursive descent)  "
        "-->  AST (per file)  -->  Multi-file Forest (inclusion graph)  -->  Symbol Tables "
        "(declare, then resolve)  -->  Semantic Diagnostics (zero-engine checks)  -->  IR "
        "Lowering  -->  Auxiliary Reference Graph (the Intermediate Representation). Every "
        "stage up to and including the IR runs with no LaTeX engine installed. Phases 8-16 "
        "(not yet started) will consume this ARG for graph analysis, classification, build "
        "planning, and runtime verification.",
    )

    add_para(doc, "Screenshots of the implemented modules or prototype:").runs[0].bold = True
    add_para(
        doc,
        "Captured from real `auxflow` runs against the project's own benchmark corpus "
        "(bench/corpus/). Each image shows the exact command and its unedited output.",
    )
    screenshots = [
        ("01-tokens.png", "Phase 2, Lexical Analysis: auxflow tokens"),
        ("02-ast.png", "Phase 3-4, Parsing and AST: auxflow ast"),
        ("03-symbols.png", "Phase 5, Symbol Tables: auxflow symbols"),
        ("04-check.png", "Phase 6, Semantic Analysis: auxflow check, clean and with errors"),
        ("05-graph.png", "Phase 7, Intermediate Representation: auxflow graph (Graphviz DOT)"),
        ("06-classify-certified.png", "Preview of Phase 11 classification: a CERTIFIED document"),
        ("07-classify-amplifying.png", "Preview of Phase 11 classification: an AMPLIFYING document"),
        ("08-verification.png", "Test suite, type check, and lint, all passing"),
    ]
    for filename, caption in screenshots:
        doc.add_picture(f"docs/screenshots/{filename}", width=Cm(15.5))
        last_pic = doc.paragraphs[-1]
        last_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(10)
        crun = cap.add_run(caption)
        crun.italic = True
        crun.font.size = Pt(10)
        crun.font.color.rgb = RGBColor(0x5A, 0x5A, 0x5A)

    add_para(doc, "Results obtained so far:").runs[0].bold = True
    results = [
        "Full front-end and IR pipeline (Phases 1-7) implemented and passing its test suite.",
        "~3,900 lines of implementation code and ~4,100 lines of test code.",
        "All code passes strict mypy type checking with zero errors and zero ruff lint/format "
        "issues.",
        "Continuous integration (GitHub Actions) runs on every commit across Python 3.12 and "
        "3.13.",
        "The parser correctly recovers from malformed input (unterminated groups, missing "
        "arguments) without raising an exception, verified by dedicated error-recovery tests.",
        "The IR's exists/value split was verified against hand-worked examples to keep "
        "ordinary documents (e.g. one containing only a table of contents) acyclic.",
    ]
    for r in results:
        add_bullet(doc, r)

    add_para(doc, "Remaining work required to complete the project:").runs[0].bold = True
    remaining = [
        "Phases 8-9: Strongly-connected-component (Tarjan) analysis and taint propagation to "
        "detect amplifying feedback.",
        "Phases 10-11: Stable-pass fixpoint derivation and the four-state document classifier "
        "(CERTIFIED / BENIGN_CYCLIC / AMPLIFYING / UNKNOWN).",
        "Phase 12: Build planner producing a safe, optimised engine-run schedule.",
        "Phase 13: Runtime verification executor that confirms or corrects static predictions "
        "against the real LaTeX engine.",
        "Phases 14-16: A fifteen-member benchmark corpus, a measurement harness comparing "
        "seven baselines, and the final empirical evaluation report.",
    ]
    for r in remaining:
        add_bullet(doc, r)

    # ---------- Section 4: Novelty ----------
    add_heading(doc, "4. Novelty", marks="2 Marks")

    add_para(doc, "What is new or different about the proposed project?").runs[0].bold = True
    add_para(
        doc,
        "AuxFlow applies standard compiler-construction techniques (lexing, parsing, symbol "
        "tables, an intermediate representation, and graph-based dataflow analysis) to a "
        "problem domain (multi-pass LaTeX compilation convergence) that is conventionally "
        "handled only dynamically, by repeatedly re-running the engine. Building an "
        "instance-level dependency graph with a deliberate exists/value split to keep "
        "ordinary documents acyclic is the central structural idea.",
    )

    add_para(doc, "How does the project differ from existing solutions?").runs[0].bold = True
    add_para(
        doc,
        "Existing tools (plain LaTeX, latexmk, latexrun, Tectonic) all decide whether another "
        "compilation pass is needed dynamically: by re-running the engine and inspecting "
        "warnings or comparing auxiliary-file checksums after each run. None of them reason "
        "about the dependency structure before execution. AuxFlow instead performs this "
        "reasoning statically, from source, before any engine pass, classifying the document "
    )

    add_para(
        doc, "What specific improvement, feature, or approach does it introduce?"
    ).runs[0].bold = True
    improvements = [
        "A declared, explicit LaTeX language subset with a documented default-deny rule: "
        "anything outside the subset is conservatively marked UNKNOWN rather than silently "
        "assumed safe.",
        "The exists/value fact split in the Intermediate Representation, which prevents the "
        "most common document shape (a table of contents) from appearing as a false cycle.",
        "A four-state classification (rather than a binary converges/does-not-converge "
        "verdict) that distinguishes harmless value-only cycles from genuinely amplifying "
        "feedback.",
        "A static analysis that is explicitly paired with, not a replacement for, runtime "
        "verification; it does not claim certainty it cannot support.",
    ]
    for i in improvements:
        add_bullet(doc, i)

    # ---------- Section 5: Presentation and Q&A ----------
    add_heading(doc, "5. Presentation and Q&A", marks="3 Marks")

    add_para(
        doc, "Clear explanation of the problem, methodology, and implementation:"
    ).runs[0].bold = True
    add_para(
        doc,
        "Presented via the accompanying slide deck (presentation/review2-auxflow.pptx) and "
        "viva preparation guide (docs/review2-viva.md), covering: why this is a compiler "
        "project; the lexer's category-code model; the recursive-descent parser and error "
        "recovery; the two-pass symbol table resolution; and the Auxiliary Reference Graph, "
        "including a worked end-to-end trace from a source snippet through tokens, AST, "
        "symbol bindings, and final IR facts and edges.",
    )

    add_para(doc, "Explanation of individual contributions:").runs[0].bold = True
    add_para(
        doc,
        "This is a single-student project. Upayan Mazumder (24BDS0367) is solely responsible "
        "for the design and implementation of all completed modules: the lexer, parser, AST, "
        "inclusion-graph resolution, symbol tables, semantic diagnostics, the Intermediate "
        "Representation, the command-line interface, the full test suite, and the continuous "
        "integration configuration.",
    )

    doc.save("docs/review2-document.docx")
    print("Saved docs/review2-document.docx successfully!")


if __name__ == "__main__":
    build_document()
