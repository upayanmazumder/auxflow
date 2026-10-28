"""Generate the Review 2 document for AuxFlow matching the Assessment 9 format.

Assessment 9 - 10 Marks format:
1. Project Details
2. Project Overview
3. Implementation / Prototype Progress (75/100%) - 5 Marks
4. Novelty - 2 Marks
5. Presentation and Q&A - 3 Marks
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

OUTPUT_DOCS = "docs/review2-document.docx"
OUTPUT_DOWNLOADS = "docs/reviews/downloads/review2-document.docx"


def build_document() -> None:
    doc = new_document()
    add_title(doc, "PROJECT REVIEW 2", "Assessment 9 \u2013 10 Marks")

    # 1. Project Details
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

    # 2. Project Overview
    add_heading(doc, "2. Project Overview")
    add_label(doc, "Brief introduction to the project")
    add_para(
        doc,
        "AuxFlow is a static analysis tool and compiler front end for multi-pass LaTeX builds. "
        "It parses source files without running TeX, constructs an Auxiliary Reference "
        "Graph (ARG), and analyzes cross-reference dependencies before typesetting.",
    )

    add_label(doc, "Problem statement and the need for the project")
    add_para(
        doc,
        "LaTeX resolves references, citations, and tables of contents through auxiliary "
        "files across successive runs. Existing build tools (such as latexmk, latexrun, and "
        "Tectonic) repeat compilation until auxiliary files stabilize or hit arbitrary caps. "
        "Pathological documents with cyclic dependencies can diverge or oscillate indefinitely, "
        "which tools detect only after wasting multiple runs. A static decision procedure is "
        "needed to predict convergence and determine required pass bounds directly from source.",
    )

    add_label(doc, "Objectives of the project")
    for objective in [
        "Construct a robust compiler front end (lexer, recursive descent parser, AST forest, "
        "symbol tables, and semantic analyzer) for a declared subset of LaTeX.",
        "Lower resolved syntax trees into an Auxiliary Reference Graph (ARG) with instance-level "
        "nodes, typed dependencies, and temporal pass lags.",
        "Formulate dataflow taint analysis and strongly connected component algorithms to classify "
        "documents into CERTIFIED, BENIGN_CYCLIC, AMPLIFYING, or UNKNOWN states.",
        "Synthesize safe, minimal build plans and verify auxiliary file convergence at runtime.",
        "Benchmark classification accuracy, latency, and execution economy across an empirical "
        "corpus of 15 documents isolating nine non-convergence mechanisms.",
    ]:
        add_bullet(doc, objective)

    add_label(doc, "Proposed solution and its expected outcome")
    add_para(
        doc,
        "AuxFlow treats pass-count prediction as a compiler dependency analysis problem. By "
        "evaluating dataflow reachability from resolved reference values to content-generating "
        "control structures, AuxFlow identifies amplifying feedback cycles prior to execution. "
        "For certified documents, it produces an exact pass bound in under 10 ms with zero "
        "engine overhead. The expected outcome is a dependable compilation plan that prevents "
        "non-terminating builds and eliminates redundant typesetting passes.",
    )

    # 3. Implementation / Prototype Progress (75/100%) - 5 Marks
    add_heading(doc, "3. Implementation / Prototype Progress (75/100%) \u2013 5 Marks")
    add_label(doc, "Overall implementation status")
    add_para(
        doc,
        "Implementation status: 100% of the 16 implementation phases are complete and verified. "
        "Review 2 focuses on the completed compiler front end and intermediate representation "
        "(Phases 1 to 7), while all downstream analysis and planning modules are also fully "
        "functional.",
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

    add_label(doc, "Modules completed and their functionalities")
    for name, desc in [
        (
            "Lexer (auxflow.lexer)",
            "Table-driven scanner implementing all sixteen TeX category codes. It recognizes "
            "comments, control sequences, and verbatim environments with exact character-roundtrip "
            "preservation.",
        ),
        (
            "Parser (auxflow.parser)",
            "Fault-tolerant recursive-descent parser with one token lookahead. Uses macro argument "
            "signatures, attaches source spans to all nodes, and recovers gracefully from syntax "
            "errors.",
        ),
        (
            "AST Forest & Inclusion (auxflow.ast)",
            "Assembles per-file ASTs into a forest, resolving \\input and \\include dependencies "
            "while detecting recursive inclusion cycles and isolating unreachable files via DFS.",
        ),
        (
            "Symbol Tables (auxflow.semantic)",
            "Maintains six symbol tables (LabelTable, RefTable, CiteTable, PackageTable, "
            "FileTable, CounterTable) using two-pass declare/resolve traversal to handle forward "
            "cross-file references.",
        ),
        (
            "Semantic Analysis (auxflow.semantic)",
            "Performs static validation without running TeX: identifies undefined references, "
            "missing citations, duplicate labels, missing files, and warns on unmodeled packages.",
        ),
        (
            "Intermediate Representation (auxflow.ir)",
            "Lowers facts into the Auxiliary Reference Graph (ARG). Implements the exists/value "
            "split on list entries to prevent spurious cycles, assigning pass lags and typed "
            "dependency edges.",
        ),
        (
            "Command-Line Interface (auxflow.cli)",
            "Provides developer inspectability via auxflow tokens, ast, symbols, check, and "
            "graph commands.",
        ),
    ]:
        add_bullet(doc, desc, bold_lead=f"{name}: ")

    add_label(doc, "Technologies, tools, programming languages, and platforms used")
    for item in [
        "Programming Language: Python 3.12+ (tested across Python 3.12, 3.13, and 3.14).",
        "Architecture: Zero third-party runtime dependencies at the core for strict portability.",
        "Verification Tools: pytest for unit/regression tests, Hypothesis for property-based "
        "testing.",
        "Quality Assurance: mypy in strict mode (zero type issues), ruff for high-performance "
        "linting.",
        "Benchmark Environment: Pinned Docker container with TeX Live, latexmk, latexrun, "
        "Tectonic, and Typst.",
        "Input Specification: Formal declared subset of standard LaTeX2e markup.",
    ]:
        add_bullet(doc, item)

    add_label(doc, "System architecture / block diagram / workflow")
    add_para(
        doc,
        "The diagram below outlines the overall compiler architecture, showing the progression "
        "from raw source characters through lexical tokens, syntax trees, symbol tables, and "
        "the ARG intermediate representation.",
    )
    add_figure(
        doc,
        "docs/figures/architecture.png",
        "Figure 1. AuxFlow compiler pipeline and dataflow architecture.",
    )
    add_figure(
        doc,
        "docs/figures/arg-b08.png",
        "Figure 2. Instance-level Auxiliary Reference Graph generated for corpus case b08_cycle.",
        width_cm=15.5,
    )

    add_label(doc, "Screenshots of the implemented modules or prototype")
    add_para(
        doc,
        "The following screenshots demonstrate the working CLI commands corresponding to the "
        "completed modules.",
    )
    for filename, caption in [
        ("01-tokens.png", "Figure 3. Lexical analysis via auxflow tokens showing category codes"),
        ("02-ast.png", "Figure 4. AST generation via auxflow ast with source span annotations"),
        ("03-symbols.png", "Figure 5. Two-pass symbol table inspection via auxflow symbols"),
        ("04-check.png", "Figure 6. Semantic analysis and error reporting via auxflow check"),
        ("05-graph.png", "Figure 7. Graphviz DOT export of the ARG via auxflow graph"),
        ("06-classify-certified.png", "Figure 8. Static classification of a certified document"),
        ("07-classify-amplifying.png", "Figure 9. Detection of an amplifying feedback cycle"),
        (
            "08-verification.png",
            "Figure 10. Test suite execution, strict mypy verification, and ruff linting",
        ),
    ]:
        add_figure(doc, f"docs/screenshots/{filename}", caption)

    add_label(doc, "Results obtained so far")
    for result in [
        "Front-End and IR: Complete implementation of all 7 front-end modules (over 2,290 lines "
        "of core code) with zero external runtime dependencies.",
        "Quality Verification: Over 400 test cases passing cleanly with strict type annotations "
        "across all files.",
        "Fault Tolerance: Demonstrated syntax recovery on broken documents without uncaught "
        "exceptions.",
        "Spurious Cycle Prevention: Proved that the exists/value fact split correctly preserves "
        "acyclicity on table-of-contents documents (b05_toc).",
        "Corpus Validation: Confirmed predicted convergence classification across all 15 "
        "benchmark corpus members.",
    ]:
        add_bullet(doc, result)

    add_label(doc, "Remaining work required to complete the project")
    for remaining in [
        "Finalize and format the comprehensive research paper draft in paper/main.tex.",
        "Package release distribution artifacts on PyPI and GitHub Releases.",
        "Finalize viva presentation defense slides and demonstration assets.",
    ]:
        add_bullet(doc, remaining)

    # 4. Novelty - 2 Marks
    add_heading(doc, "4. Novelty \u2013 2 Marks")
    add_label(doc, "What is new or different about the proposed project?")
    add_para(
        doc,
        "AuxFlow is the first system to treat multi-pass document build scheduling as a classical "
        "compiler static analysis problem rather than an empirical trial-and-error execution loop. "
        "Instead of repeatedly invoking the engine to observe whether auxiliary files change, "
        "AuxFlow builds a formal instance-level dependency graph and computes pass bounds "
        "analytically before execution.",
    )

    add_label(doc, "How does the project differ from existing solutions?")
    add_para(
        doc,
        "Existing build tools (latexmk, latexrun, Tectonic, ConTeXt, Typst) are purely "
        "dynamic: they execute compilation iterations up to hard-coded caps (typically 5 to "
        "9 passes) and compare checksums between runs. They provide no diagnostic explanation "
        "when a document diverges. AuxFlow differs fundamentally by performing ahead-of-time "
        "dependency analysis, isolating the exact source locations responsible for "
        "amplifying feedback, and certifying convergence prior to running the engine.",
    )

    add_label(doc, "What specific improvement, feature, or approach does it introduce?")
    for item in [
        "Declared Subset with Default-Deny: Formalizes supported LaTeX constructs and safely flags "
        "unsupported features as UNKNOWN rather than assuming sound convergence.",
        "Exists/Value Fact Split: A novel intermediate representation design that decouples "
        "entry existence from typeset page values, preventing standard tables of contents from "
        "producing false cyclic dependencies.",
        "Monotone Taint Propagation: Distinguishes benign value cycles from content-amplifying "
        "loops, providing a domain-specific sufficient check for the classical finite-height "
        "convergence condition.",
        "Integrated Ahead-of-Time Planning and Verification: Derives a proven pass bound for "
        "certified documents and couples it with runtime auxiliary verification to catch "
        "unexpected state divergence.",
    ]:
        add_bullet(doc, item)

    # 5. Presentation and Q&A - 3 Marks
    add_heading(doc, "5. Presentation and Q&A \u2013 3 Marks")
    add_label(doc, "Clear explanation of the problem, methodology, and implementation")
    add_para(
        doc,
        "The presentation clearly articulates why multi-pass document compilation requires static "
        "analysis: auxiliary file feedback can cause monotonic divergence or oscillation that "
        "heuristic iteration caps fail to handle safely. The methodology demonstrates how source "
        "text is transformed through a catcode-aware lexer, signature-driven parser, and AST "
        "forest into the Auxiliary Reference Graph. The implementation highlights robust, "
        "zero-dependency Python engineering, strict type safety, extensive property and golden "
        "testing, and clear CLI inspection commands.",
    )

    add_label(doc, "Explanation of individual contributions")
    for contrib in [
        "Sole Developer & Researcher: Conceived, formulated, and implemented the entire AuxFlow "
        "compiler pipeline, from the 16-catcode lexer through the ARG intermediate representation "
        "and analysis engine.",
        "Test & Benchmark Design: Authored the full test suite (400+ unit, property, and golden "
        "tests) and built the containerized benchmarking harness evaluating 15 corpus documents "
        "against 7 baselines.",
        "Theoretical Framing & Documentation: Formulated the exists/value split, mapped "
        "finite-height convergence criteria to taint propagation, and authored all project "
        "documentation, reports, and research paper drafts.",
    ]:
        add_bullet(doc, contrib)

    doc.save(OUTPUT_DOCS)
    doc.save(OUTPUT_DOWNLOADS)
    print(f"Saved {OUTPUT_DOCS} and {OUTPUT_DOWNLOADS}")


if __name__ == "__main__":
    build_document()
