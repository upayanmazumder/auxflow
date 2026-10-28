"""Generate the Review 3 report for AuxFlow.

The report follows the required nine-section format: title page, abstract,
introduction, literature review, methodology, implementation, results and
discussion, conclusion and future work, references.

The benchmark numbers come from bench/results/2026-10-28/ (see
paper/make_results.py). Code counts describe the current source tree.

Run from the repository root:
    python scripts/generate_review3_document.py
Output: docs/reviews/downloads/review3-document.docx
"""

from __future__ import annotations

from docx.enum.text import WD_BREAK
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

OUTPUT = "docs/reviews/downloads/review3-document.docx"
RESULTS = "bench/results/2026-10-28"


def build_document() -> None:
    doc = new_document()

    # 1. Title page ---------------------------------------------------------------------
    add_title(doc, "PROJECT REVIEW 3", PROJECT_TITLE)
    add_heading(doc, "1. Title Page")
    add_details_table(
        doc,
        [
            ("Project title", PROJECT_TITLE),
            ("Student name", STUDENT),
            ("Register number", REGISTER_NUMBER),
            ("Programme", PROGRAMME),
            ("Department", "School of Computer Science and Engineering (SCOPE)"),
            ("College", "Vellore Institute of Technology, Vellore, Tamil Nadu, India"),
            ("Academic year", "2026-2027"),
            ("Project guide", GUIDE),
        ],
    )
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # 2. Abstract -----------------------------------------------------------------------
    add_heading(doc, "2. Abstract")
    add_para(
        doc,
        "Cross-references, contents pages, and bibliographies can require more than one LaTeX "
        "run. Each run reads auxiliary files from the preceding run. Build tools usually "
        "repeat the engine until those files appear stable or a run limit is reached. "
        "A document with feedback between page references and layout may not settle.",
    )
    add_para(
        doc,
        "AuxFlow is a static analysis tool and compiler front end for a declared subset of "
        "LaTeX. The parser identifies references and generated lists, then the Auxiliary "
        "Reference Graph (ARG) records individual facts and their dependencies. Taint "
        "analysis checks whether a reference value controls the amount of content. AuxFlow "
        "reports CERTIFIED, BENIGN_CYCLIC, AMPLIFYING, or UNKNOWN before compilation. The "
        "planner selects engine runs, and the runtime verifier compares the resulting "
        "auxiliary files.",
    )
    add_para(
        doc,
        "The evaluation used 15 documents and 7 baselines, with 10 repetitions per "
        "document and baseline (1,050 trials, not 1,050 engine runs). Over an "
        "eight-pass ground-truth horizon, the predicted bound met or exceeded "
        "the measured requirement for all 7 currently certified documents. "
        "Two unstable documents were AMPLIFYING and four were UNKNOWN. UNKNOWN "
        "does not establish non-convergence. Analysis took 1.3 ms at the median "
        "and 10.4 ms at most in this corpus. Guards added after the first "
        "measurements changed three declared false negatives from CERTIFIED to UNKNOWN.",
    )

    # 3. Introduction -------------------------------------------------------------------
    add_heading(doc, "3. Introduction")
    add_label(doc, "Background")
    add_para(
        doc,
        "LaTeX writes labels to an auxiliary file during one run. A reference can read "
        "those labels on the next run. Contents pages and bibliographies add further "
        "dependencies. The tools examined here use different stopping tests: latexmk "
        "limits itself to 5 runs, Tectonic to 6, ConTeXt to 9, and Typst to 5 "
        "iterations. latexrun documents no limit.",
    )
    add_label(doc, "Problem statement")
    add_para(
        doc,
        "The stopping tests examined in this report do not derive a pass bound from the "
        "document's source. A fixed schedule can end before references settle. An engine "
        "warning can miss changes to a generated list. Reference text can also change "
        "line breaks and page numbers, so a document may alter the dependencies that "
        "the analysis tries to describe. Static pass numbering assumes a fixed graph. "
        "AuxFlow therefore verifies its predicted plan against an engine run.",
    )
    add_label(doc, "Objectives")
    for item in [
        "Classify a document before an engine run and show the source locations of "
        "potentially amplifying cycles.",
        "Calculate a pass bound for certified documents, then compare it with measured run counts.",
        "Build from that classification and compare auxiliary files after each engine run.",
        "Compare a fixed schedule and four dynamic stopping tests with AuxFlow on "
        "a 15-document corpus, including cases that expose limitations.",
    ]:
        add_bullet(doc, item)

    # 4. Literature review --------------------------------------------------------------
    add_heading(doc, "4. Literature Review")
    add_grid(
        doc,
        ["Related work", "Main finding", "Relation to AuxFlow"],
        [
            [
                "Alblas (1981)",
                "Distinguishes simple from pure multi-pass attribute evaluation. "
                "The pure setting considers individual attribute instances.",
                "AuxFlow numbers individual auxiliary facts. It does not claim "
                "to invent instance-level pass numbering.",
            ],
            [
                "Hecht and Ullman (1975)",
                "Relate iterative data-flow rounds to graph depth.",
                "AuxFlow uses a similar propagation bound, followed by a "
                "confirmation run.",
            ],
            [
                "Magnusson and Hedin (2007)",
                "State finite-height and monotonicity conditions for circular "
                "attribute convergence. Their evaluator does not check them.",
                "AuxFlow detects content-generation feedback in its declared "
                "subset, but it does not test every convergence condition.",
            ],
            [
                "Erdweg, Lichter, and Weiel (2015)",
                "Their Pluto build system handles LaTeX dependencies dynamically. "
                "They explain why general static dependency detection is not sound.",
                "AuxFlow restricts the source language and reports UNKNOWN "
                "for unsupported constructs.",
            ],
            [
                "Gaspar (2014)",
                "Shows a LaTeX loop whose page reference causes repeated page growth.",
                "The example informs corpus document b08_cycle, which AuxFlow "
                "reports as AMPLIFYING.",
            ],
        ],
    )
    add_para(
        doc,
        "These five works cover pass scheduling, iteration bounds, cyclic "
        "evaluation, dynamic build dependencies, and a non-convergent LaTeX "
        "example. AuxFlow applies their ideas to a restricted document model.",
    )

    # 5. Methodology --------------------------------------------------------------------
    add_heading(doc, "5. Methodology")
    add_label(doc, "Proposed system and architecture")
    add_para(
        doc,
        "Parsing, graph construction, classification, and planning use only source files. "
        "The auxflow run command executes the plan and checks the files TeX writes.",
    )
    add_figure(doc, "docs/figures/architecture.png", "Figure 1. AuxFlow compiler pipeline")

    add_label(doc, "Data model")
    add_para(
        doc,
        "The Auxiliary Reference Graph (ARG) has a node for each label, reference, or "
        "other fact instance. Each node records its kind, key, component (exists or "
        "value), and source span. Edges record the dependency, pass lag, reason, "
        "and type: AUX_ROUNDTRIP, TOOL, LAYOUT, or STRUCTURAL.",
    )
    add_figure(
        doc,
        "docs/figures/arg-model.png",
        "Figure 2. Entity-relationship model of the ARG",
        width_cm=14.0,
    )

    add_label(doc, "Analysis workflow")
    for item in [
        "Taint analysis begins with values read in loop bounds or conditions. It follows "
        "value edges to find facts that may influence generated content. For each such "
        "fact, it adds a STRUCTURAL edge to content volume. The cost is O(V + E).",
        "Iterative Tarjan analysis finds strongly connected components. An internal "
        "STRUCTURAL edge marks an AMPLIFYING cycle. An opaque fact marks UNKNOWN_CYCLE. "
        "The other cycles are BENIGN within the model.",
        "After cycle analysis, stable-pass numbering follows the longest path between "
        "components. For a fact f, s(f) = 1 when f has no dependencies. Otherwise, "
        "s(f) = 1 + max(s(g) + lag(g to f) - 1) over dependencies g. P is the largest "
        "s(f) for facts stored in auxiliary files. The planned bound is N = P + 1.",
    ]:
        add_bullet(doc, item)
    add_figure(
        doc,
        "docs/figures/arg-b08.png",
        "Figure 3. ARG of b08_cycle. Taint analysis adds the STRUCTURAL edge that closes "
        "the AMPLIFYING cycle.",
        width_cm=11.0,
    )

    add_label(doc, "Classification and planning")
    add_para(
        doc,
        "The classifier selects one of four states from the graph. A CERTIFIED plan "
        "uses the derived count. Every other executable plan starts with at least "
        "three engine runs, as enforced by a planner assertion. AMPLIFYING has no "
        "plan unless the user supplies --force. Forced runs stop at a cap of six. "
        "UNKNOWN has a conservative executable plan by default. The --strict option "
        "refuses UNKNOWN before execution.",
    )
    add_figure(
        doc,
        "docs/figures/classification-flow.png",
        "Figure 4. Four-state classifier and the plan for each state",
    )

    add_label(doc, "Runtime verification")
    add_para(
        doc,
        "After each engine run, the verifier reads auxiliary files and compares "
        "canonical records with the previous run. If they still change after "
        "the planned runs, it repeats the last engine step up to the cap. "
        "It records a prediction miss if verification exceeds a certified bound. "
        "It does not use engine rerun warnings.",
    )
    add_figure(
        doc,
        "docs/figures/runtime-sequence.png",
        "Figure 5. auxflow run: plan execution with runtime verification",
    )

    add_label(doc, "Tools")
    add_para(
        doc,
        "The compiler core uses Python 3.12 without third-party runtime dependencies. "
        "I used pytest and Hypothesis for tests, ruff and mypy --strict for checks, "
        "Docker for the pinned benchmark image, and hatch-vcs for tag-based versions.",
    )

    # 6. Implementation -----------------------------------------------------------------
    add_heading(doc, "6. Implementation")
    add_para(
        doc,
        "Review 2 covered phases 1 to 7, from lexical analysis through ARG construction. "
        "Phases 8 to 16 add graph analysis, planning, runtime checks, and evaluation.",
    )
    add_grid(
        doc,
        ["Phase", "Module", "Function"],
        [
            ["8", "auxflow.analysis.scc", "Iterative Tarjan SCC and cycle labels"],
            ["9", "auxflow.analysis.taint", "Seed and propagate taint, add STRUCTURAL edges"],
            ["10", "auxflow.analysis.stable_pass", "Stable-pass number per fact, N = P + 1"],
            ["11", "auxflow.analysis.classify", "Four-state classifier and diagnostics"],
            ["12", "auxflow.planner", "Build plan with the safety rule and the --force cap"],
            ["13", "auxflow.runtime", "State normalisation, fixpoint check, auxflow run"],
            ["14 to 16", "bench/", "Corpus, 7 baselines, ground truth, evaluation report"],
        ],
    )
    add_label(doc, "Changes after the first measurement")
    for item in [
        "After the first measurements, I added a guard for page references under "
        "roman, Roman, alph, or Alph numbering. These numeral forms can change "
        "width as their values change. The guard also marks \\vref and \\vpageref UNKNOWN.",
        "An explicit list treats certain packages and commands as inert. This lets "
        "ordinary front matter pass without treating an arbitrary package as safe.",
        "The auxflow run command limits each tool call to 600 seconds. It passes "
        "-no-shell-escape and rejects auxiliary files outside the work directory.",
        "The auxflow update command uses pipx when that environment has no pip.",
    ]:
        add_bullet(doc, item)
    add_label(doc, "Code and quality figures")
    for item in [
        "The current tree has 5,657 lines of Python source in 47 modules, excluding "
        "the generated version file. Tests contain 6,021 lines in 58 Python files. "
        "The compiler core has no third-party runtime dependencies. In the local "
        "non-engine test run, 403 tests passed, 1 skipped, and 3 engine or slow "
        "tests were deselected. These counts describe the current tree.",
    ]:
        add_bullet(doc, item)

    # 7. Results and discussion ---------------------------------------------------------
    add_heading(doc, "7. Results and Discussion")
    add_label(doc, "Experimental setup")
    add_para(
        doc,
        "The 15 documents, b01_plain through b15_ibid, include a multi-chapter thesis "
        "and cases for mechanisms M1 to M9. Each of seven baselines used ten "
        "repetitions per document, in separate containers with one CPU and no "
        "network. This produced 1,050 trials, including static-only D trials with "
        "no engine runs. A is a fixed three-run schedule, B uses engine warnings, "
        "C compares outputs, C' compares inputs, and C'' compares files read and "
        "rewritten within a run. D is static AuxFlow analysis. E adds runtime "
        "verification with --strict for UNKNOWN. Ground truth N* uses eight "
        "unconditional engine passes rather than a baseline's stopping decision. "
        "I recorded expected classes before implementing the analyzer.",
    )
    add_figure(
        doc,
        "docs/figures/evaluation-setup.png",
        "Figure 6. Evaluation setup: corpus, baselines, ground truth, and gates",
    )

    add_label(doc, "Screenshots of classification and execution")

    for filename, caption in [
        (
            "06-classify-certified.png",
            "Figure 7. auxflow classify and plan on a CERTIFIED document",
        ),
        ("07-classify-amplifying.png", "Figure 8. auxflow classify on an AMPLIFYING document"),
        ("09-classify-unknown.png", "Figure 9. auxflow classify on an UNKNOWN document"),
        ("10-run-forced.png", "Figure 10. auxflow run --force stops at the cap of six runs"),
    ]:
        add_figure(doc, f"docs/screenshots/{filename}", caption)
    add_label(doc, "Classification and run-count bound")
    add_grid(
        doc,
        ["Document", "N*", "Before the guard", "Current class", "Predicted N"],
        [
            ["b01_plain", "1", "CERTIFIED", "CERTIFIED", "1"],
            ["b02_backref", "2", "CERTIFIED", "CERTIFIED", "2"],
            ["b03_fwdref", "2", "CERTIFIED", "CERTIFIED", "2"],
            ["b04_chain", "2", "CERTIFIED", "CERTIFIED", "3"],
            ["b05_toc", "3", "CERTIFIED", "CERTIFIED", "3"],
            ["b06_bib", "3", "CERTIFIED", "CERTIFIED", "4"],
            ["b07_footnote", "2", "UNKNOWN", "UNKNOWN", "none"],
            ["b08_cycle", "divergent", "AMPLIFYING", "AMPLIFYING", "none"],
            ["b09_thesis", "3", "CERTIFIED", "CERTIFIED", "4"],
            ["b10_random", "divergent", "UNKNOWN", "UNKNOWN", "none"],
            ["b11_width", "oscillating", "CERTIFIED", "UNKNOWN", "none"],
            ["b12_float", "oscillating", "CERTIFIED", "UNKNOWN", "none"],
            ["b13_varioref", "oscillating", "CERTIFIED", "UNKNOWN", "none"],
            ["b14_ifthen", "oscillating", "AMPLIFYING", "AMPLIFYING", "none"],
            ["b15_ibid", "3", "UNKNOWN", "UNKNOWN", "none"],
        ],
    )
    for item in [
        "For the 7 currently certified documents, N >= N* over the measured "
        "eight-pass horizon. The bound is exact for 4 and exceeds ground truth "
        "by one for b04, b06, and b09. This does not prove a universal bound.",
        "The classifier marks b08 AMPLIFYING and b05 CERTIFIED. The former has a "
        "content-generating cycle, while the latter has a generated list without "
        "that cycle.",
        "Among the 6 non-convergent corpus documents, 2 are AMPLIFYING and 4 are "
        "UNKNOWN before execution. UNKNOWN reports insufficient static knowledge, "
        "not proof of non-convergence. Ground truth supplies the latter finding.",
        "The analysis marks b14 AMPLIFYING because it may affect content quantity. "
        "This case changes content size instead. A hand port compiled under Typst "
        "without an error.",
    ]:
        add_bullet(doc, item)

    add_label(doc, "Gate 1 is reported as FAIL")
    add_para(
        doc,
        "The original test specification expected CERTIFIED for b11, b12, and b13, "
        "although it identified them as false negatives. After initial measurements, "
        "the phase 16 syntactic guards changed all three to UNKNOWN. The automated "
        "report therefore marks Gate 1 FAIL against that original specification. "
        "Gate 2 checks N >= N* for certified documents and reports zero violations. "
        "These three cases cannot independently validate a guard designed after "
        "their failures. The guard checks numeral syntax, not font metrics.",
    )

    add_label(doc, "Stopping tests compared")
    add_grid(
        doc,
        ["Outcome", "A", "B", "C", "C'", "C''", "E", "D"],
        [
            ["Correct stop, of 9 convergent documents", "9", "7", "9", "9", "9", "7", "7"],
            ["Premature stop on a convergent document", "0", "2", "0", "0", "0", "0", "0"],
            ["Withheld by static refusal", "0", "0", "0", "0", "0", "2", "2"],
            ["Non-convergence flagged, of 6", "0", "5", "6", "6", "6", "6", "6"],
            ["Non-convergence accepted as converged", "6", "1", "0", "0", "0", "0", "0"],
            ["Engine runs on the 9 convergent documents", "27", "17", "22", "22", "22", "17", "0"],
        ],
        widths_cm=[6.9, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35],
    )
    for item in [
        "The fixed three-run schedule A accepts all 6 non-convergent cases as converged.",
        "The warning test B accepts b10 after one run in every repetition, although "
        "its auxiliary state never settles. B also stops at one run on b05 and "
        "b15, where N* is 3.",
        "C, C', and C'' produced the same outcomes for each document. The expected "
        "one-run difference between output and input comparisons did not appear "
        "in this corpus.",
        "E made 17 engine runs across the 7 convergent documents it executed. "
        "A made 21 on those same documents. The benchmark's strict policy refused "
        "the 6 non-convergent cases and the convergent but opaque b07 and b15 "
        "before execution. Without --strict, UNKNOWN can run with verification.",
        "For b01_plain, N* and the predicted N are both 1, but E runs twice. "
        "pdfTeX writes a page-count record to the .aux file, so the verifier "
        "needs two observed states to confirm equality. It records a prediction "
        "miss in all 10 repetitions because the executed count exceeds N. "
        "That operational miss does not show a pass-bound violation.",
    ]:
        add_bullet(doc, item)
    add_figure(
        doc,
        f"{RESULTS}/executions.png",
        "Figure 11. Engine runs until a verdict, per document and baseline (generated by "
        "bench/harness/report.py)",
    )

    add_label(doc, "External tools")
    add_para(
        doc,
        "latexmk and latexrun did not converge on the 6 non-convergent documents "
        "within their tested limits. latexrun also failed on b15, which latexmk "
        "accepted. Offline Tectonic ran only b01 and b08. It reached its "
        "six-pass limit on b08. Typst rejected a hand port of b08 with "
        "'loop seems to be infinite'.",
    )

    add_label(doc, "Cost")
    add_para(
        doc,
        "The analysis took 1.3 ms at the median and 10.4 ms at most across "
        "the measured corpus. The largest graph, b09_thesis, had 91 facts "
        "and 73 edges and took 7.5 ms. These timings are analysis overhead. "
        "The run counts above do not subtract that time.",
    )

    add_label(doc, "Threats to validity")
    for item in [
        "The corpus contains 15 documents, mostly synthetic, and all benchmark "
        "runs used one machine. This limits how far the findings generalize.",
        "I wrote the corpus, expectations, and analyzer. I recorded the expectations "
        "first, but their author and the implementer were the same person.",
        "The model assumes a resolved reference does not change pagination. "
        "Text width can violate that assumption, so the analysis remains "
        "unsound for extent-driven feedback.",
        "The container uses TeX Live 2022. Other releases may require different "
        "run counts. A leftover .aux file once caused three baselines to stop "
        "early on b05. I removed those records and repeated the runs.",
    ]:
        add_bullet(doc, item)

    # 8. Conclusion and future work -----------------------------------------------------
    add_heading(doc, "8. Conclusion and Future Work")
    add_label(doc, "Outcomes")
    for item in [
        "On the 7 currently certified documents, AuxFlow's predicted count was "
        "never below measured N* within eight passes. Non-certified plans use "
        "at least three runs when execution is allowed.",
        "Static analysis took 1.3 ms at the median in this 15-document corpus. "
        "Diagnostics include source locations.",
        "In this corpus, a fixed three-run schedule accepted all 6 unstable "
        "documents, while the engine-warning test stopped early on b05 and b15. "
        "It also accepted b10 as converged.",
        "The IEEE conference-style research paper is in paper/.",
    ]:
        add_bullet(doc, item)
    add_label(doc, "Limitations")
    for item in [
        "The analysis handles a declared subset. Unsupported constructs make "
        "the result UNKNOWN, which is not a non-convergence finding. The benchmark "
        "refused UNKNOWN under --strict, while normal execution permits it.",
        "The syntactic width guard does not capture every change to text extent. "
        "Extent-driven feedback can still defeat the analysis.",
        "AMPLIFYING covers both divergence and oscillation. The bound for "
        "BENIGN_CYCLIC is heuristic, and this corpus has no benign cyclic case.",
        "Ground truth observes eight passes. A longer run could reveal later changes.",
    ]:
        add_bullet(doc, item)
    add_label(doc, "Improvements")
    for item in [
        "Test more documents from independent, real projects.",
        "Develop a width analysis that does not rely only on numeral syntax.",
        "Distinguish divergent cycles from oscillating cycles where evidence permits.",
        "Model additional package behavior and study whether benign cycles "
        "admit a justified pass bound.",
    ]:
        add_bullet(doc, item)

    # 9. References ---------------------------------------------------------------------
    add_heading(doc, "9. References")
    for ref in [
        "G. V. Bochmann, Semantic evaluation from left to right, Communications of the ACM "
        "19(2):55-62, 1976.",
        "H. Alblas, A characterization of attribute evaluation in passes, Acta Informatica "
        "16(4):427-464, 1981.",
        "K.-J. Raiha and E. Ukkonen, Minimizing the number of evaluation passes for "
        "attribute grammars, SIAM Journal on Computing 10(4):772-786, 1981.",
        "R. Farrow, Automatic generation of fixed-point-finding evaluators for circular, "
        "but well-defined, attribute grammars, SIGPLAN Notices 21(7):85-98, 1986.",
        "L. G. Jones, Efficient evaluation of circular attribute grammars, ACM TOPLAS "
        "12(3):429-462, 1990.",
        "E. Magnusson and G. Hedin, Circular reference attributed grammars: their "
        "evaluation and applications, Science of Computer Programming 68(1):21-37, 2007.",
        "M. S. Hecht and J. D. Ullman, A simple algorithm for global data flow analysis "
        "problems, SIAM Journal on Computing 4(4):519-532, 1975.",
        "J. B. Kam and J. D. Ullman, Global data flow analysis and iterative algorithms, "
        "Journal of the ACM 23(1):158-171, 1976.",
        "A. Mokhov, N. Mitchell, and S. Peyton Jones, Build systems a la carte, "
        "Proceedings of the ACM on Programming Languages 2(ICFP), 2018.",
        "S. Erdweg, M. Lichter, and M. Weiel, A sound and optimal incremental build "
        "system with dynamic dependencies, OOPSLA 2015.",
        "R. Tarjan, Depth-first search and linear graph algorithms, SIAM Journal on "
        "Computing 1(2):146-160, 1972.",
        "Gaspar, Does not suffice to run LaTeX a finite number of times to get "
        "cross-references right, TUGboat 35(1):16, 2014.",
        "L. Madje, A Programmable Markup Language for Typesetting, MSc thesis, "
        "Technische Universitat Berlin, 2022.",
        "J. Collins, latexmk, https://ctan.org/pkg/latexmk (version 4.88).",
        "A. Clements, latexrun, https://github.com/aclements/latexrun.",
        "Tectonic, https://github.com/tectonic-typesetting/tectonic (version 0.15.0).",
        "Typst, https://github.com/typst/typst (version 0.11.0).",
        "AuxFlow source, corpus, harness, and results, "
        "https://github.com/upayanmazumder/auxflow, and PyPI package auxflow.",
        "U. Mazumder and B. R., AuxFlow: A static applicability test for fixpoint "
        "convergence in multi-pass LaTeX builds, 2026, paper/main.pdf in the repository.",
    ]:
        add_bullet(doc, ref)

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
