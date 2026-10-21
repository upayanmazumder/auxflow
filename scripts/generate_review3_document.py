"""Generate the Review 3 document for AuxFlow.

Review 3 presents compiler Phases 8-16: analysis, build planning, runtime
verification, and the benchmark evaluation. Every number comes from
docs/EVALUATION-REPORT.md, docs/GATE-REPORT.md, or
bench/results/published/.

Run from the repository root:
    python scripts/generate_review3_document.py
Output: docs/review3-document.docx
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

OUTPUT = "docs/review3-document.docx"


def build_document() -> None:
    doc = new_document()
    add_title(doc, "PROJECT REVIEW 3", PROJECT_TITLE)

    add_heading(doc, "1. Project Details")
    add_details_table(
        doc,
        [
            ("Project Title", PROJECT_TITLE),
            ("Student Name(s)", STUDENT),
            ("Register Number(s)", REGISTER_NUMBER),
            ("Programme / Branch", PROGRAMME),
            ("Project Guide", GUIDE),
            ("Review Date", "31 October 2026"),
        ],
    )

    add_heading(doc, "2. Project Overview")
    add_para(
        doc,
        "AuxFlow is a static analysis tool for LaTeX documents that need more than one "
        "compilation pass. It parses the source, builds the Auxiliary Reference Graph (ARG), "
        "and classifies the document as CERTIFIED, BENIGN_CYCLIC, AMPLIFYING, or UNKNOWN "
        "before the engine runs. For a certified document it predicts the engine run count. "
        "A runtime verifier then checks the prediction against the real engine.",
    )
    add_para(
        doc,
        "Review 2 covered the front end and the IR (Phases 1 to 7). This document covers "
        "Phases 8 to 16: graph analysis, classification, build planning, runtime "
        "verification, and the evaluation.",
    )
    add_figure(
        doc,
        "docs/figures/architecture.png",
        "Figure 1. AuxFlow compiler pipeline. Phases 8 to 16 are the subject of this document.",
    )
    add_heading(doc, "3. Implementation Status")
    add_para(
        doc,
        "Progress: 16 of 16 implementation phases complete (100% of the implementation plan).",
    )
    add_grid(
        doc,
        ["Phase", "Module", "Function"],
        [
            [
                "8",
                "auxflow.analysis.scc",
                "Iterative Tarjan SCC, condensation graph, cycle "
                "classes AMPLIFYING / UNKNOWN_CYCLE / BENIGN",
            ],
            [
                "9",
                "auxflow.analysis.taint",
                "Seeds from values read in loop bounds and "
                "conditions, worklist propagation, STRUCTURAL edges to CONTENT_VOLUME",
            ],
            [
                "10",
                "auxflow.analysis.stable_pass",
                "Stable-pass number P per fact on the condensation, predicted runs P + 1",
            ],
            [
                "11",
                "auxflow.analysis.classify",
                "Four-state classifier and source-located diagnostics, auxflow classify",
            ],
            [
                "12",
                "auxflow.planner",
                "Build plan: reachable files only, bibtex only with "
                "citations and a bibliography, derived run count, refusal of AMPLIFYING",
            ],
            [
                "13",
                "auxflow.runtime",
                "Normalised auxiliary records, fixpoint check, "
                "prediction-miss records, auxflow run",
            ],
            [
                "14 to 16",
                "bench/",
                "15-document corpus, 7 baselines, ground truth, "
                "1,050 containerised runs, evaluation report",
            ],
        ],
    )
    add_label(doc, "Classification")
    add_figure(
        doc,
        "docs/figures/classification-flow.png",
        "Figure 2. Four-state classifier and the build plan for each state",
    )
    add_figure(
        doc,
        "docs/figures/arg-b08.png",
        "Figure 3. ARG of b08_cycle. Taint analysis adds the STRUCTURAL edge that closes the "
        "AMPLIFYING cycle.",
    )

    add_label(doc, "Build planner safety rule")
    add_para(
        doc,
        "Only a CERTIFIED plan uses the derived run count. Every other executable state uses "
        "at least three engine runs, and an assertion in the planner enforces this. An "
        "AMPLIFYING document gets no plan unless the user passes --force, which runs it "
        "under a cap of six runs.",
    )

    add_label(doc, "Runtime verification")
    add_para(
        doc,
        "The verifier normalises each auxiliary file into an order-independent set of "
        "records and compares the state after run k with the state after run k-1. Rerun "
        "warnings miss changes in generated lists, so the verifier does not use them. When "
        "a certified document needs more runs than predicted, the verifier records a "
        "prediction miss.",
    )
    add_figure(
        doc,
        "docs/figures/runtime-sequence.png",
        "Figure 4. auxflow run: plan execution with runtime verification",
    )

    add_label(doc, "Code and quality figures")
    for item in [
        "About 3,930 lines of implementation code in 41 modules, and about 4,080 lines of "
        "test code in 46 files. No third-party runtime dependencies.",
        "245 tests pass and 1 is skipped. mypy --strict reports no issues in 41 source "
        "files. ruff reports no lint issues in src, tests, and bench.",
    ]:
        add_bullet(doc, item)

    for filename, caption in [
        ("06-classify-certified.png", "auxflow classify on a CERTIFIED document"),
        ("07-classify-amplifying.png", "auxflow classify on an AMPLIFYING document: no plan"),
        ("08-verification.png", "Test suite, strict type check, and lint"),
    ]:
        add_figure(doc, f"docs/screenshots/{filename}", caption)

    add_heading(doc, "4. Evaluation and Results")
    add_label(doc, "Setup")
    add_para(
        doc,
        "15 benchmark documents (b01_plain to b15_ibid) cover the non-convergence mechanisms "
        "M1 to M9, including a realistic multi-chapter thesis. Seven baselines were measured: "
        "A (fixed three runs), B (rerun warnings), C (checksum), C' (inputs), C'' "
        "(read/write set), D (AuxFlow static), and E (AuxFlow static plus runtime "
        "verification). Each document and baseline ran ten times in a pinned Docker image "
        "with one CPU and no network: 1,050 runs in total. Ground truth N* comes from eight "
        "unconditional engine passes, independent of every baseline.",
    )
    add_figure(
        doc,
        "docs/figures/evaluation-setup.png",
        "Figure 5. Evaluation pipeline: corpus, baselines, ground truth, and gates",
    )

    add_label(doc, "Gate 1, classification separation: PASS")
    add_grid(
        doc,
        ["Document", "Expected", "Observed"],
        [
            ["b08_cycle", "AMPLIFYING", "AMPLIFYING"],
            ["b05_toc", "not AMPLIFYING", "CERTIFIED"],
            [
                "b11_width, b12_float, b13_varioref",
                "CERTIFIED (declared false negative)",
                "CERTIFIED",
            ],
            ["b07_footnote, b15_ibid", "UNKNOWN", "UNKNOWN"],
        ],
    )
    add_para(
        doc,
        "All 15 documents classified exactly as expected.json predicted before implementation.",
    )

    add_label(doc, "Gate 2, run-count bound (EC1): PASS")
    add_grid(
        doc,
        ["Document", "Predicted N", "Ground truth N*", "N >= N*"],
        [
            ["b01_plain", "1", "1", "yes"],
            ["b02_backref", "2", "2", "yes"],
            ["b03_fwdref", "2", "2", "yes"],
            ["b04_chain", "3", "2", "yes"],
            ["b05_toc", "3", "3", "yes"],
            ["b06_bib", "4", "3", "yes"],
            ["b09_thesis", "4", "3", "yes"],
            ["b11_width", "2", "divergent(8)", "no (declared)"],
            ["b12_float", "2", "divergent(8)", "no (declared)"],
            ["b13_varioref", "2", "divergent(8)", "no (declared)"],
        ],
    )
    add_para(
        doc,
        "The only three violations are the three documents declared as false negatives "
        "before implementation. There are no undeclared violations.",
    )

    add_label(doc, "Findings")
    for item in [
        "Baseline A reports success on all six non-convergent documents (b08, b10, b11 to "
        "b14) and is wrong on each of them.",
        "Baseline B reports CONVERGED after one run on b10_random in all ten repetitions. "
        "Ground truth for b10_random is divergent(8).",
        "On b11_width, b12_float, and b13_varioref, static analysis alone (D) certifies the "
        "document wrongly, as declared. Baseline E keeps running past the prediction and "
        "reports cap_exceeded at six runs in all 30 repetitions.",
        "latexmk and latexrun also fail to converge on b11_width, b12_float, and "
        "b13_varioref. Tectonic stops b08_cycle at its 6-pass limit, and Typst rejects a "
        "port of b08_cycle with 'loop seems to be infinite'.",
        "Static analysis (D) finishes in under 10 ms on every document. The largest case, "
        "b09_thesis with 91 facts and 73 edges, has a median of 9.65 ms.",
        "b01_plain needs two runs under E although N* is 1. pdfTeX writes "
        "\\@abspage@last on every run, so the verifier needs a second run to see two equal "
        "states.",
    ]:
        add_bullet(doc, item)
    add_figure(
        doc,
        "bench/results/published/figures/executions.png",
        "Figure 6. Engine executions to certify, per document and baseline",
    )

    add_label(doc, "Limitations")
    for item in [
        "The corpus has 15 documents, and most are synthetic. All runs used one machine.",
        "The static model does not see line-break width, float placement, or varioref text "
        "feedback. Runtime verification catches these cases.",
        "Tectonic ran fully offline on only b01_plain and b08_cycle. The latexmk and latexrun "
        "cross-check covers all 15 documents.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "5. Novelty")
    for item in [
        "Static classification of multi-pass convergence from source, before any engine "
        "run. latexmk, latexrun, and Tectonic decide only after each run.",
        "The exists/value split in the IR, which keeps ordinary documents acyclic.",
        "Four states that separate value-only cycles from cycles that change how much "
        "content is generated.",
        "A static prediction paired with a runtime verifier that records prediction misses.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "6. Remaining Work and Future Scope")
    for item in [
        "Write the research paper. The paper/ directory has the section structure.",
        "Model more packages, so fewer documents classify UNKNOWN.",
        "Prove a run-count bound for benign cycles.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "7. Reproduction")
    add_para(
        doc,
        "bash bench/demo.sh runs the full pipeline on b08_cycle and b11_width and compares "
        "each verdict with the published measurements. Every number in this document comes "
        "from bench/results/published/ and docs/EVALUATION-REPORT.md.",
    )

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
