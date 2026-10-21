"""Generate the Review 2 document for AuxFlow.

Review 2 covers compiler Phases 1-7 (lexer through IR generation) and reports
progress on all 16 implementation phases.

Run from the repository root:
    python scripts/generate_review2_document.py
Output: docs/review2-document.docx
"""

from __future__ import annotations

from review_docx import (
    GUIDE,
    PROGRAMME,
    PROJECT_TITLE,
    REGISTER_NUMBER,
    STUDENT,
    add_bullet,
    add_details_table,
    add_figure,
    add_grid,
    add_heading,
    add_label,
    add_para,
    add_title,
    new_document,
)

OUTPUT = "docs/review2-document.docx"


def build_document() -> None:
    doc = new_document()
    add_title(doc, "PROJECT REVIEW 2", PROJECT_TITLE)

    # 1. Project details
    add_heading(doc, "1. Project Details")
    add_details_table(
        doc,
        [
            ("Project Title", PROJECT_TITLE),
            ("Student Name(s)", STUDENT),
            ("Register Number(s)", REGISTER_NUMBER),
            ("Programme / Branch", PROGRAMME),
            ("Project Guide", GUIDE),
            ("Review Date", "28 October 2026"),
        ],
    )

    # 2. Project overview
    add_heading(doc, "2. Project Overview")
    add_label(doc, "Introduction")
    add_para(
        doc,
        "AuxFlow is a static analysis tool for LaTeX documents that need more than one "
        "compilation pass. It has its own compiler front end (lexer, parser, AST, symbol "
        "tables) and an intermediate representation called the Auxiliary Reference Graph "
        "(ARG). Graph analysis over the ARG classifies the cross-reference dependency "
        "structure of a document before the LaTeX engine runs.",
    )

    add_label(doc, "Problem")
    add_para(
        doc,
        "Cross-references, tables of contents, and bibliographies make LaTeX write auxiliary "
        "files that the next pass reads. A document is stable only when these files stop "
        "changing. Build tools find the pass count by trial: they run the engine until the "
        "files stop changing, or they run a fixed schedule such as three passes. A fixed "
        "schedule wastes runs on simple documents and stops too early on documents that need "
        "more. A small number of documents never stabilise because a page number controls "
        "how much content is generated. No tool we surveyed (latexmk, latexrun, Tectonic) "
        "analyses this dependency structure before it runs the engine.",
    )

    add_label(doc, "Objectives")
    for objective in [
        "Build a compiler front end (lexer, parser, AST, symbol tables, semantic checks) for "
        "a declared subset of LaTeX.",
        "Lower the resolved AST into the Auxiliary Reference Graph, an instance-level "
        "intermediate representation with typed, lagged dependency edges.",
        "Classify each document into one of four convergence states (CERTIFIED, "
        "BENIGN_CYCLIC, AMPLIFYING, UNKNOWN) with strongly connected components and taint "
        "analysis.",
        "Derive a safe build plan with a predicted engine run count, and check that "
        "prediction at runtime.",
        "Measure the approach on a benchmark corpus against seven baselines and against "
        "latexmk, latexrun, Tectonic, and Typst.",
    ]:
        add_bullet(doc, objective)

    add_label(doc, "Approach")
    add_para(
        doc,
        "AuxFlow treats pass-count selection as a compiler problem. It parses the source "
        "once, builds a graph of every construct that reads or writes auxiliary state, and "
        "decides from that graph whether the auxiliary state settles and after how many "
        "runs. For a certified document the tool predicts the run count in under 10 ms with "
        "no engine execution. For constructs outside the declared subset it reports UNKNOWN "
        "and uses a conservative schedule.",
    )

    # 3. Implementation progress
    add_heading(doc, "3. Implementation Progress")
    add_para(
        doc,
        "Progress: 16 of 16 implementation phases complete (100% of the implementation "
        "plan). This document covers the front end and the intermediate representation "
        "(Phases 1 to 7).",
    )
    add_grid(
        doc,
        ["Phases", "Scope", "Status"],
        [
            ["1", "Project setup and test infrastructure", "Complete"],
            ["2 to 7", "Lexer, parser, AST, symbol tables, semantic checks, IR", "Complete"],
            [
                "8 to 11",
                "SCC analysis, taint analysis, stable-pass fixpoint, classifier",
                "Complete",
            ],
            ["12 to 13", "Build planner, runtime verification", "Complete"],
            ["14 to 16", "Benchmark corpus, harness, evaluation report", "Complete"],
        ],
    )
    add_label(doc, "System architecture")
    add_figure(
        doc,
        "docs/figures/architecture.png",
        "Figure 1. AuxFlow compiler pipeline. Phases 1 to 7 are the subject of this document.",
    )
    add_figure(
        doc,
        "docs/figures/arg-b08.png",
        "Figure 2. Auxiliary Reference Graph of b08_cycle (auxflow graph). Taint analysis "
        "adds the dashed STRUCTURAL edges. The thick one closes the AMPLIFYING cycle.",
        width_cm=15.5,
    )

    add_label(doc, "Implemented modules (Phases 1 to 7)")
    for name, desc in [
        (
            "Lexer (auxflow.lexer)",
            "Single-pass, table-driven scanner for the sixteen TeX category codes. It "
            "recognises comments, control words and symbols, and \\verb verbatim regions. A "
            "property test checks that the tokens reproduce the exact source bytes.",
        ),
        (
            "Parser (auxflow.parser)",
            "Hand-written recursive-descent parser with one token of lookahead. A "
            "macro-signature table drives mandatory and optional argument parsing. The parser "
            "produces one AST per file over sixteen node kinds, and every node has a source "
            "span. Malformed input, such as an unterminated group, becomes a diagnostic and "
            "does not raise an exception.",
        ),
        (
            "AST and inclusion resolution (auxflow.ast)",
            "Joins the per-file ASTs into a multi-file forest and builds the inclusion graph "
            "from \\input and \\include. Depth-first search detects circular inclusion and "
            "files that the entry file cannot reach.",
        ),
        (
            "Symbol tables (auxflow.semantic)",
            "Six tables (LabelTable, RefTable, CiteTable, PackageTable, FileTable, "
            "CounterTable). A declare pass records every definition, then a resolve pass binds "
            "the uses, so forward and cross-file references resolve.",
        ),
        (
            "Semantic analysis (auxflow.semantic)",
            "Checks that need no engine run: undefined references and citations, duplicate "
            "labels, missing included files, missing graphics files, inclusion cycles, and "
            "unmodelled packages.",
        ),
        (
            "Intermediate representation (auxflow.ir)",
            "The ARG has one fact per modelled construct (label, reference, contents entry, "
            "citation, counter read) with a source span. Typed edges (AUX_ROUNDTRIP, TOOL, "
            "LAYOUT, STRUCTURAL) carry a pass lag. Each list entry is split into an exists "
            "fact and a value fact, so a document with only a table of contents stays "
            "acyclic. The graph serialises to JSON and Graphviz DOT.",
        ),
        (
            "Command-line interface (auxflow.cli)",
            "auxflow tokens, ast, symbols, check, and graph expose Phases 2 to 7. The same "
            "CLI also has classify, plan, and run for the Review 3 phases.",
        ),
    ]:
        add_bullet(doc, desc, bold_lead=f"{name}: ")

    add_label(doc, "Technologies")
    for item in [
        "Python 3.12 or later. CI tests 3.12 and 3.13, and the suite also passes on 3.14.",
        "No third-party runtime dependencies. The lexer, parser, symbol tables, IR, and the "
        "Tarjan SCC algorithm are written by hand.",
        "pytest and Hypothesis for unit, property, golden, and end-to-end tests.",
        "mypy in strict mode for type checking, and ruff for linting and formatting.",
        "Docker for the benchmark: a pinned image with TeX Live, latexmk, latexrun, "
        "Tectonic, and Typst.",
        "Input language: a documented subset of LaTeX2e.",
    ]:
        add_bullet(doc, item)

    add_label(doc, "Screenshots")
    add_para(
        doc,
        "Each image shows a real auxflow command and its output on small test documents.",
    )
    for filename, caption in [
        ("01-tokens.png", "Phase 2, lexical analysis: auxflow tokens"),
        ("02-ast.png", "Phases 3 and 4, parsing and AST: auxflow ast"),
        ("03-symbols.png", "Phase 5, symbol tables: auxflow symbols"),
        ("04-check.png", "Phase 6, semantic analysis: auxflow check on a clean and a broken file"),
        ("05-graph.png", "Phase 7, intermediate representation: auxflow graph (Graphviz DOT)"),
        ("06-classify-certified.png", "Phase 11 classifier on the same IR: a CERTIFIED document"),
        ("07-classify-amplifying.png", "Phase 11 classifier: an AMPLIFYING document"),
        ("08-verification.png", "Test suite, strict type check, and lint"),
    ]:
        add_figure(doc, f"docs/screenshots/{filename}", caption)

    add_label(doc, "Results")
    for result in [
        "All 16 phases are implemented: about 3,930 lines of implementation code in 41 "
        "modules, and about 4,080 lines of test code in 46 files. The Review 2 modules "
        "(lexer, parser, AST, semantic analysis, IR) are about 2,290 of those lines.",
        "245 tests pass and 1 is skipped. mypy --strict reports no issues in 41 source "
        "files, and ruff reports no lint issues in src, tests, and bench.",
        "The parser recovers from unterminated groups and missing arguments without an "
        "exception. Dedicated recovery tests cover these cases.",
        "The exists/value split keeps the table-of-contents benchmark (b05_toc) acyclic: "
        "it classifies CERTIFIED.",
        "On the 15-document corpus, every document classified as predicted before "
        "implementation, and both evaluation gates passed.",
    ]:
        add_bullet(doc, result)

    add_label(doc, "Remaining work")
    add_bullet(
        doc,
        "Write the research paper. The paper/ directory has the section structure, and the "
        "evaluation results it needs are available.",
    )

    # 4. Novelty
    add_heading(doc, "4. Novelty")
    add_label(doc, "Contribution")
    add_para(
        doc,
        "AuxFlow applies standard compiler construction (lexing, parsing, symbol tables, an "
        "intermediate representation, and graph dataflow analysis) to multi-pass LaTeX "
        "compilation. Existing tools handle that problem only by running the engine again. "
        "The central design choice is an instance-level dependency graph in which each list "
        "entry is split into an exists fact and a value fact, so ordinary documents stay "
        "acyclic.",
    )

    add_label(doc, "Comparison with existing tools")
    add_para(
        doc,
        "latexmk, latexrun, and Tectonic decide after each engine run whether another run is "
        "needed. They read rerun warnings or compare auxiliary-file checksums. AuxFlow makes "
        "this decision from the source before the first run. It classifies the document, "
        "predicts the run count when the document is certified, and names the facts and "
        "source locations that form a risky cycle.",
    )

    add_label(doc, "Specific techniques")
    for item in [
        "A declared LaTeX subset with a default-deny rule: an unsupported construct makes "
        "the document UNKNOWN, and the tool does not assume it is safe.",
        "The exists/value split in the IR, which stops a table of contents from appearing as "
        "a false cycle.",
        "Four classification states. Value-only cycles (BENIGN_CYCLIC) are kept separate "
        "from cycles in which a value controls how much content is generated (AMPLIFYING).",
        "Static prediction paired with runtime verification. The verifier records a "
        "prediction miss when the real run count exceeds the prediction.",
    ]:
        add_bullet(doc, item)

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
