"""Generator for Review 3 presentation deck matching AuxFlow visual identity.

Theme: Dark Navy (#0D1B2A), Card (#152A3E), Border (#1B3A57), Accent Cyan (#38BDF8),
Text Light (#E6EDF3), Muted (#9BAFC6), Green (#34D399), Amber (#FBBF24).
Widescreen 16:9 (13.333" x 7.5").
"""

from __future__ import annotations

import pptx
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

COLOR_BG = RGBColor(0x0D, 0x1B, 0x2A)
COLOR_CARD = RGBColor(0x15, 0x2A, 0x3E)
COLOR_BORDER = RGBColor(0x1B, 0x3A, 0x57)
COLOR_ACCENT = RGBColor(0x38, 0xBD, 0xF8)
COLOR_TEXT = RGBColor(0xE6, 0xED, 0xF3)
COLOR_MUTED = RGBColor(0x9B, 0xAF, 0xC6)
COLOR_GREEN = RGBColor(0x34, 0xD3, 0x99)
COLOR_AMBER = RGBColor(0xFB, 0xBF, 0x24)
COLOR_RED = RGBColor(0xF8, 0x71, 0x71)

FONT_HEADING = "Trebuchet MS"
FONT_BODY = "Calibri"
FONT_CODE = "Consolas"


def set_bg(slide: pptx.slide.Slide) -> None:
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG


def add_header(
    slide: pptx.slide.Slide, tracker: str, title: str, slide_num: int, total_slides: int = 8
) -> None:
    txbox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.0), Inches(0.4))
    tf = txbox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = tracker.upper()
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT

    num_box = slide.shapes.add_textbox(Inches(11.0), Inches(0.4), Inches(1.5), Inches(0.4))
    ntf = num_box.text_frame
    ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
    np = ntf.paragraphs[0]
    np.alignment = PP_ALIGN.RIGHT
    np.text = f"{slide_num:02d} / {total_slides:02d}"
    np.font.name = FONT_HEADING
    np.font.size = Pt(13)
    np.font.bold = True
    np.font.color.rgb = COLOR_MUTED


def add_card(
    slide: pptx.slide.Slide,
    left: float,
    top: float,
    width: float,
    height: float,
    bg_color: RGBColor = COLOR_CARD,
    border_color: RGBColor = COLOR_BORDER,
) -> pptx.shapes.autoshape.Shape:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape


def build_review3_deck() -> pptx.Presentation:
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ==================== SLIDE 1: Title ====================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    card1 = add_card(s1, 0.8, 0.8, 11.733, 5.9)
    tf1 = card1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.8)
    tf1.margin_right = Inches(0.8)
    tf1.margin_top = Inches(0.7)

    p = tf1.paragraphs[0]
    p.text = "COMPILER DESIGN LAB   ·   REVIEW 3 (FINAL VIVA)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    p = tf1.add_paragraph()
    p.space_before = Pt(12)
    p.text = "AuxFlow: Analysis, Optimization, & Empirical Evaluation"
    p.font.name = FONT_HEADING
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT

    p = tf1.add_paragraph()
    p.space_before = Pt(10)
    p.text = "Cycle Classification, Build Planning, Runtime Verification, and 15-Member Benchmark Corpus Results"
    p.font.name = FONT_BODY
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_MUTED

    p = tf1.add_paragraph()
    p.space_before = Pt(40)
    p.text = "Student: Upayan Mazumder (24BDS0367)\nCourse: Compiler Design Lab\nMilestone: Review 3 — Full 16-Phase Implementation & Evaluation Complete"
    p.font.name = FONT_BODY
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 2: Project Overview & Architecture ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "PROJECT ARCHITECTURE", "End-to-End Compiler Pipeline for Multi-Pass Documents", 2)

    c_w = 3.64
    c_h = 5.2
    c_top = 1.6

    add_card(s2, 0.8, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASES 1–7: FRONT-END"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_p1 = [
        ("Lexer & Catcodes", "16 TeX category codes, single-pass scanner, precise source spans."),
        ("Recursive Descent Parser", "Argument signatures, error recovery, multi-file AST forest."),
        ("Symbol Tables & Checks", "2-pass declaration/resolution, zero-engine diagnostics."),
        ("Auxiliary Reference Graph", "Fact instances with exists/value split and lagged typed edges."),
    ]
    for b_title, b_desc in bullets_p1:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    add_card(s2, 0.8 + c_w + 0.4, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(0.8 + c_w + 0.6), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASES 8–11: ANALYSIS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_p2 = [
        ("Iterative Tarjan SCC", "Condensation DAG computation without interpreter stack limits."),
        ("Taint Analysis", "Worklist reachability from condition reads to CONTENT_VOLUME."),
        ("Stable-Pass Recurrence", "Derives exact pass numbers P for fact stabilization."),
        ("4-State Classification", "CERTIFIED, BENIGN_CYCLIC, AMPLIFYING, UNKNOWN."),
    ]
    for b_title, b_desc in bullets_p2:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    add_card(s2, 0.8 + (c_w + 0.4) * 2, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(0.8 + (c_w + 0.4) * 2 + 0.2), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASES 12–16: EVALUATION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_p3 = [
        ("Build Planner Optimizer", "Dead-file/tool elimination, run-count derivation, safety invariant."),
        ("Runtime Verification", "Canonical normalization of auxiliary records into fixpoint sets."),
        ("15-Member Corpus", "M1–M8 non-convergence mechanisms covering all declared gates."),
        ("7 Baselines Measured", "1050 containerized runs prove Gate 1 and Gate 2 (EC1) empirically."),
    ]
    for b_title, b_desc in bullets_p3:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # ==================== SLIDE 3: Static Analysis & Taint ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "CYCLE & TAINT ANALYSIS", "Detecting Amplifying Feedback Without Full Simulation", 3)

    add_card(s3, 0.8, 1.6, 5.6, 5.2)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE TAINT-SEED MECHANISM"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    taint_points = [
        "Core Question: Can a cross-reference value influence how much content the document generates?",
        "Taint Seeds: Facts whose values are read inside loop conditions or bounds (\\forloop, \\whiledo, \\ifthenelse).",
        "Forward Worklist: Taint propagates monotonically along value-carrying edges (push-at-most-once invariant).",
        "STRUCTURAL Edge Insertion: Each tainted fact gets a STRUCTURAL edge f -> CONTENT_VOLUME with its verbatim source span.",
        "Cycle Decision: If any SCC contains a STRUCTURAL edge, the document is classified AMPLIFYING.",
    ]
    for pt in taint_points:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = f"• {pt}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s3, 6.8, 1.6, 5.733, 5.2)
    tb = s3.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "FOUR-STATE CLASSIFICATION DECISION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    states = [
        ("CERTIFIED (Bound = P + 1 passes)", "Provably acyclic dependency structure. Standard documents settle within derived bound."),
        ("BENIGN_CYCLIC (Value-only cycle)", "Cycles exist in value edges (e.g. section lists) but no content quantity changes."),
        ("AMPLIFYING (Refused by default)", "A cross-reference controls content growth. High divergence risk. Requires --force."),
        ("UNKNOWN (Conservative fallback)", "Contains unmodelled packages/macros. Falls back to default 3-run schedule."),
    ]
    for st_title, st_desc in states:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(12)
        p1.text = f"[{st_title}]"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {st_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # ==================== SLIDE 4: Build Planner & Runtime Verifier ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "PLANNER & VERIFICATION", "Safe Build Optimization & Sound Fixpoint Comparison", 4)

    add_card(s4, 0.8, 1.6, 5.6, 5.2)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "BUILD PLANNER PASSES (PHASE 12)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    planner_points = [
        ("1. Dead-File Elimination", "Scans and spell-checks only files reachable in the inclusion graph. Unused chapters skipped."),
        ("2. Dead-Tool Elimination", "Omits BibTeX unless both citation facts and bibliography commands exist."),
        ("3. Run-Count Derivation", "CERTIFIED plans emit exactly P+1 engine passes; non-certified emit conservative floor (3 runs)."),
        ("4. Safety Invariant", "Asserts non-certified executable plans have at least 3 engine runs before emission."),
    ]
    for pt, desc in planner_points:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"• {pt}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    add_card(s4, 6.8, 1.6, 5.733, 5.2)
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "RUNTIME VERIFIER (PHASE 13)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER
    verifier_points = [
        ("Canonical Normalization", "Parses .aux, .toc, .lof, .lot, .bbl into order-independent record tuples."),
        ("Documented Exclusion List", "Only \\relax is excluded (boiler-plate). Unmodelled commands stay observable."),
        ("Sound Fixpoint vs Warnings", "Compares normalized state Ak == Ak-1 directly, avoiding unsound engine warnings."),
        ("Bounded Extension & Misses", "Extends execution while state changes up to cap; logs PredictionMiss when exceeding certified bound."),
    ]
    for pt, desc in verifier_points:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"• {pt}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # ==================== SLIDE 5: Benchmark Corpus ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "15-MEMBER BENCHMARK CORPUS", "Systematic Coverage of Multi-Pass Convergence Mechanisms", 5)

    card_table = add_card(s5, 0.8, 1.6, 11.733, 5.2)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE 15-MEMBER CORPUS (bench/corpus/b01_plain .. b15_ibid)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    table_data = (
        "ID           MECHANISM / PURPOSE                                       EXPECTED    OBSERVED (D)  STATUS\n"
        "------------------------------------------------------------------------------------------------------\n"
        "b01_plain    Plain prose with no auxiliary state producers/consumers   CERTIFIED   CERTIFIED     PASS\n"
        "b02_backref  Backward cross-reference (label then ref)                 CERTIFIED   CERTIFIED     PASS\n"
        "b03_fwdref   Forward cross-reference (ref then label)                  CERTIFIED   CERTIFIED     PASS\n"
        "b04_chain    Contents extent shifts page before reference              CERTIFIED   CERTIFIED     PASS\n"
        "b05_toc      Contents list without cross-reference uses                CERTIFIED   CERTIFIED     PASS\n"
        "b06_bib      BibTeX tool edge with generated-list cascade              CERTIFIED   CERTIFIED     PASS\n"
        "b07_footnote Footnote placement feedback via resolved ref width        UNKNOWN     UNKNOWN       PASS\n"
        "b08_cycle    M1: Loop bounded by forward page ref (Gaspar 2014)        AMPLIFYING  AMPLIFYING    PASS\n"
        "b09_thesis   Realistic multi-chapter thesis (TOC/LOF/LOT, bib, unreach) CERTIFIED  CERTIFIED     PASS\n"
        "b10_random   M8: Nondeterministic pdfTeX random auxiliary state        UNKNOWN     UNKNOWN       PASS\n"
        "b11_width    M3: Reference width changes line-break (SE 30674)         CERTIFIED*  CERTIFIED     PASS (decl.)\n"
        "b12_float    M4: Top float placement and Roman page number width       CERTIFIED*  CERTIFIED     PASS (decl.)\n"
        "b13_varioref M6: varioref dynamic text moves across page break         CERTIFIED*  CERTIFIED     PASS (decl.)\n"
        "b14_ifthen   M2: ifthenelse conditional font sizing on pageref         AMPLIFYING  AMPLIFYING    PASS\n"
        "b15_ibid     M5: biblatex authoryear-icomp same-page ibid feedback     UNKNOWN     UNKNOWN       PASS\n"
        "------------------------------------------------------------------------------------------------------\n"
        "* Declared false negatives: predicted in advance as limitations of the line-breaking abstraction."
    )
    p = tf.add_paragraph()
    p.space_before = Pt(8)
    p.text = table_data
    p.font.name = FONT_CODE
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 6: Empirical Results & Baselines ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "EMPIRICAL EVALUATION", "1050 Containerized Runs Across 7 Compilation Baselines", 6)

    add_card(s6, 0.8, 1.6, 5.6, 5.2)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ORACLE COMPARISON (EXECUTIONS TO CERTIFY)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    summary_oracle = (
        "BASELINE PERFORMANCE SUMMARY:\n\n"
        "• Baseline A (Fixed Schedule = 3 runs):\n"
        "  Silently wrong on all 6 non-converging docs.\n\n"
        "• Baseline B (Engine Warnings):\n"
        "  Unsound! Declares CONVERGED after 1 run on\n"
        "  b10_random (never warns on random changes),\n"
        "  misses TOC shifts with no ref on b05_toc.\n\n"
        "• Baselines C / C' / C'' (State Checksums):\n"
        "  Sound dynamic fixpoint detection.\n"
        "  C costs N+1 runs; C' and C'' cost N runs.\n\n"
        "• Baseline D (AuxFlow Static Alone):\n"
        "  Zero engine runs! Classifies in <10ms.\n\n"
        "• Baseline E (Static Plan + Verification):\n"
        "  Combines static speed with dynamic safety.\n"
        "  Correctly catches b11-b13 false negatives\n"
        "  at cap=6 instead of failing silently."
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = summary_oracle
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT

    # Right side: The execution chart placeholder / summary
    add_card(s6, 6.8, 1.6, 5.733, 5.2)
    tb = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "GATES & EXTERNAL TOOL CROSS-CHECKS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    cross_checks = (
        "GATE 1 (Classification Separation): PASS\n"
        "• b08 correctly AMPLIFYING with 3 named facts.\n"
        "• b05 correctly CERTIFIED (no false alarm).\n"
        "• b11-b13 matched declared false negatives.\n\n"
        "GATE 2 (Empirical Claim EC1): PASS\n"
        "• Predicted N >= Ground Truth N* for all certified docs.\n"
        "• 0 undeclared bound failures across all 15 members.\n\n"
        "SHIPPING TOOL CROSS-CHECKS (RQ6):\n"
        "• latexmk 4.79: Fails to converge on b08, b10, b11-b14.\n"
        "• latexrun: Fails to converge on b08, b10, b11-b15.\n"
        "  --> Independently confirms b11-b13 non-convergence\n"
        "      is real, not an AuxFlow artifact!\n"
        "• Typst Compiler: Refuses b08_cycle with\n"
        "  'error: loop seems to be infinite'."
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = cross_checks
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 7: Live Demonstration Walkthrough ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "LIVE DEMONSTRATION", "Verifying b08_cycle & b11_width via bench/demo.sh", 7)

    add_card(s7, 0.8, 1.6, 5.6, 5.2)
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "DEMONSTRATION 1: b08_cycle (AMPLIFYING)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    demo1 = (
        "$ auxflow classify bench/corpus/b08_cycle/main.tex\n"
        "auxflow: AMPLIFYING CYCLE -- may not converge.\n"
        "  cycle (3 facts):\n"
        "    PAGEREF_USE(end:generated) (main.tex:5:32)\n"
        "      -> CONTENT_VOLUME (main.tex:8:3)\n"
        "         STRUCTURAL: reaches content construct\n"
        "      -> LABEL_PAGE(end:generated) (main.tex:10:29)\n"
        "      -> PAGEREF_USE(end:generated)\n"
        "  [Refuses to emit plan without --force]\n\n"
        "$ auxflow run --force main.tex\n"
        "  Pass 1 -> 1 page\n"
        "  Pass 2 -> 2 pages\n"
        "  Pass 3 -> 3 pages ... Pass 6 -> 6 pages\n"
        "  Status: cap_exceeded (Monotone divergence!)"
    )
    p = tf.add_paragraph()
    p.space_before = Pt(8)
    p.text = demo1
    p.font.name = FONT_CODE
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT

    add_card(s7, 6.8, 1.6, 5.733, 5.2)
    tb = s7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "DEMONSTRATION 2: b11_width (DECLARED MISCLASSIFICATION)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    demo2 = (
        "$ auxflow classify bench/corpus/b11_width/main.tex\n"
        "auxflow: CERTIFIED -- 2 runs\n"
        "  [Acyclic ARG: no STRUCTURAL edges found]\n\n"
        "THE DECLARED EXPERIMENT:\n"
        "expected.json:\n"
        "  declared_false_negative: true\n"
        "  mechanism: M3 ref width changes line break\n\n"
        "GROUND TRUTH REALITY:\n"
        "Real engine state hashes across 8 runs:\n"
        "  Run 1: add8c2c1 (page 1)\n"
        "  Run 2: 72beb0e4 (page 2)\n"
        "  Run 3: add8c2c1 (page 1)\n"
        "  Run 4: 72beb0e4 (page 2) ... period-2 forever!\n\n"
        "Conclusion: Predicted misclassification is confirmed!"
    )
    p = tf.add_paragraph()
    p.space_before = Pt(8)
    p.text = demo2
    p.font.name = FONT_CODE
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 8: Project Deliverables & Conclusion ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "CONCLUSION & ARTIFACTS", "Summary of Completed Compiler Deliverables", 8)

    add_card(s8, 0.8, 1.6, 5.6, 5.2)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tf_box = tb.text_frame
    tf_box.word_wrap = True
    p = tf_box.paragraphs[0]
    p.text = "PROJECT METRICS & VERIFICATION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    metrics = [
        "16 Implementation Phases Complete: From Lexer to Final Evaluation.",
        "75 GitHub Issues & 7 Milestones Closed: 58/58 sub-issues linked and reconciled.",
        "Quality Gate Scores: 245 unit tests passed, strict mypy type check clean, ruff lint/format clean.",
        "Plan Validation: 0.0 defects, 100% quality score on validate_plan.py.",
        "Fast Performance: Static classification in <10ms, including multi-chapter thesis.",
    ]
    for m in metrics:
        p = tf_box.add_paragraph()
        p.space_before = Pt(10)
        p.text = f"✓ {m}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s8, 6.8, 1.6, 5.733, 5.2)
    tb = s8.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY RESEARCH CONTRIBUTIONS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    contributions = [
        ("Instance-Level Reference IR", "A formal dependency graph (ARG) with an exists/value split that keeps ordinary multi-pass documents acyclic."),
        ("Taint-Based Amplification Analysis", "Detects monotone divergence risks statically before execution, producing source-located diagnostics."),
        ("Empirical Soundness Proof", "Demonstrates that engine warnings are unsound, and that runtime verification rescues static false negatives."),
        ("Transparent Falsification", "Predicts its own limitations (M3, M4, M6) in advance rather than disguising them as unexpected errors."),
    ]
    for c_title, c_desc in contributions:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(8)
        p1.text = f"★ {c_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {c_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    prs.save("presentation/review3-auxflow.pptx")
    print("Saved presentation/review3-auxflow.pptx successfully!")


if __name__ == "__main__":
    build_review3_deck()
