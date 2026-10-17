"""Generator for Review 2 presentation deck matching Review 1 visual identity.

Theme: Dark Navy (#0D1B2A), Card (#152A3E), Border (#1B3A57), Accent Cyan (#38BDF8),
Text Light (#E6EDF3), Muted (#9BAFC6).
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
    # Tracker / category
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

    # Main Slide Title
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT

    # Page number pill
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


def build_review2_deck() -> pptx.Presentation:
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
    p.text = "COMPILER DESIGN LAB   ·   REVIEW 2"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    p = tf1.add_paragraph()
    p.space_before = Pt(12)
    p.text = "AuxFlow: Front-End, Semantics, & IR"
    p.font.name = FONT_HEADING
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT

    p = tf1.add_paragraph()
    p.space_before = Pt(10)
    p.text = "Lexer Catcodes, Recursive Descent, Multi-File Symbol Tables, and the Auxiliary Reference Graph"
    p.font.name = FONT_BODY
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_MUTED

    p = tf1.add_paragraph()
    p.space_before = Pt(40)
    p.text = "Student: Upayan Mazumder (24BDS0367)\nCourse: Compiler Design Lab\nMilestone: Review 2 — Phases 1 to 7 Implementation Complete"
    p.font.name = FONT_BODY
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 2: Review 1 to Review 2 Progress ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "REVIEW 2 MILESTONE", "From Proposed Architecture to Working Front-End & IR", 2)

    # 3 Summary Cards
    c_w = 3.64
    c_h = 5.2
    c_top = 1.6

    # Card A: Front End
    add_card(s2, 0.8, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASES 1–4: FRONT-END"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_a = [
        ("TeX Catcode Lexer", "Single-pass scanner supporting all 16 TeX category codes with full source fidelity."),
        ("Recursive Descent Parser", "Hand-written, 1-token lookahead over declared macro signature table."),
        ("Fault-Tolerant AST", "Missing braces or unterminated groups record diagnostics without crashing."),
        ("Multi-File Forest", "Resolves \\input/\\include chains and detects circular inclusions via DFS."),
    ]
    for b_title, b_desc in bullets_a:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(12)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # Card B: Semantics
    add_card(s2, 0.8 + c_w + 0.4, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(0.8 + c_w + 0.6), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASES 5–6: SEMANTICS"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_b = [
        ("6 Symbol Tables", "LabelTable, RefTable, CiteTable, PackageTable, FileTable, CounterTable."),
        ("Two-Pass Resolution", "Declare pass defines all symbols; Resolve pass binds cross-file references."),
        ("Zero-Engine Check", "auxflow check surfaces undefined refs, duplicate labels, and missing assets in milliseconds."),
        ("Opacity Boundary", "Unmodelled packages flagged immediately under strict default-deny policy."),
    ]
    for b_title, b_desc in bullets_b:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(12)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # Card C: IR Generation
    add_card(s2, 0.8 + (c_w + 0.4) * 2, c_top, c_w, c_h)
    tb = s2.shapes.add_textbox(Inches(0.8 + (c_w + 0.4) * 2 + 0.2), Inches(c_top + 0.2), Inches(c_w - 0.4), Inches(c_h - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PHASE 7: INTERMEDIATE REP."
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    bullets_c = [
        ("Instance-Level ARG", "Auxiliary Reference Graph nodes are fact instances, not generic types."),
        ("Typed Lagged Edges", "Edges carry pass-lag (0 or 1) and dependency type (AUX_ROUNDTRIP, TOOL, LAYOUT)."),
        ("Exists / Value Split", "List entries split into structure (exists) vs page (value) to keep standard docs acyclic."),
        ("Graphviz DOT Export", "auxflow graph serializes the complete IR with visual component coloring."),
    ]
    for b_title, b_desc in bullets_c:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(12)
        p1.text = f"• {b_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"  {b_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    # ==================== SLIDE 3: Lexer Architecture ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "COMPILER PHASE 2", "Lexical Analysis: TeX Category Codes & Scanners", 3)

    add_card(s3, 0.8, 1.6, 5.6, 5.2)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE TEX CATCODE SCANNER"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    body_l3 = [
        "16 Category Codes: Characters are classified by dynamic catcode table (escape '\\', group '{ }', comment '%', math '$').",
        "Single-Pass Linear Scan: O(N) table-driven state machine without backtracking.",
        "Comment Semantics: '%' consumes through the newline and all leading whitespace on the following line.",
        "Delimiter-Driven Verbatim: \\verb|...| dynamically reads its delimiter character and bypasses tokenization.",
        "Precise Span Attribution: Every token retains exact (line, col, offset, length) in the input file.",
    ]
    for item in body_l3:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        p.text = f"• {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    # Code / demonstration card
    add_card(s3, 6.8, 1.6, 5.733, 5.2)
    tb = s3.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CLI OUTPUT: auxflow tokens"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    sample_tokens = (
        "$ auxflow tokens snippet.tex\n"
        "1:1  CONTROL_SEQUENCE '\\section'\n"
        "1:9  BEGIN_GROUP      '{'\n"
        "1:10 LETTER           'I'\n"
        "1:11 LETTER           'n'\n"
        "1:12 LETTER           't'\n"
        "1:13 LETTER           'r'\n"
        "1:14 LETTER           'o'\n"
        "1:15 END_GROUP        '}'\n"
        "2:1  CONTROL_SEQUENCE '\\label'\n"
        "2:7  BEGIN_GROUP      '{'\n"
        "2:8  LETTER           's'\n"
        "2:9  LETTER           'e'\n"
        "2:10 LETTER           'c'\n"
        "2:11 OTHER            ':'\n"
        "2:12 LETTER           '1'\n"
        "2:13 END_GROUP        '}'\n\n"
        "Property: round_trip(tokens) == source bytes"
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = sample_tokens
    p.font.name = FONT_CODE
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 4: Parser & AST ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "COMPILER PHASES 3–4", "Recursive Descent Parsing & Multi-File AST Forest", 4)

    add_card(s4, 0.8, 1.6, 5.6, 5.2)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SYNTACTIC RECONSTRUCTION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    items_s4 = [
        "Declared Subset: Focuses on structure-bearing macros (\\section, \\label, \\pageref, \\cite, \\begin{...}).",
        "Signature-Driven: Command arguments (mandatory {}, optional []) parsed by signature table.",
        "Error Recovery: Unterminated groups or missing arguments log a Diagnostic and close gracefully at EOF.",
        "Inclusion Graph: \\input and \\include nodes connect file ASTs; 3-color DFS flags circular inclusion immediately.",
        "AST Nodes (16): Frozen immutable dataclasses, each with mandatory Span(file_id, start, end).",
    ]
    for item in items_s4:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        p.text = f"• {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s4, 6.8, 1.6, 5.733, 5.2)
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CLI OUTPUT: auxflow ast"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    sample_ast = (
        "$ auxflow ast main.tex\n"
        "=== main.tex ===\n"
        "Document [main.tex:0-142]\n"
        "  Preamble [main.tex:0-48]\n"
        "    MacroCall(\\documentclass) [main.tex:0-23]\n"
        "      Text('article') [main.tex:15-22]\n"
        "    MacroCall(\\usepackage) [main.tex:24-43]\n"
        "      Text('varioref') [main.tex:36-42]\n"
        "  Sectioning(section) [main.tex:49-68]\n"
        "    Text('Introduction') [main.tex:58-67]\n"
        "  MacroCall(\\label) [main.tex:69-85]\n"
        "    Text('sec:intro') [main.tex:76-84]\n"
        "  Include(include) [main.tex:86-112]\n"
        "    Text('chapters/methods')\n"
        "=== chapters/methods.tex ===\n"
        "Document [chapters/methods.tex:0-320]\n"
        "  Sectioning(chapter) ...\n"
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = sample_ast
    p.font.name = FONT_CODE
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 5: Symbol Tables & Semantics ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "COMPILER PHASES 5–6", "Symbol Tables & Zero-Engine Semantic Analysis", 5)

    add_card(s5, 0.8, 1.6, 5.6, 5.2)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TWO-PASS CROSS-MODULE RESOLUTION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    items_s5 = [
        "Pass 1: Declare: Walks all ASTs in the forest. Populates LabelTable definitions, PackageTable declarations, FileTable reachability, and CounterTable ops.",
        "Pass 2: Resolve: Binds RefTable use sites to defining labels across file boundaries; matches citations to bibliography entries.",
        "Multi-File Forward References: Reference in intro.tex to label in appendix.tex resolves cleanly without ordering hazards.",
        "Diagnostics Engine: auxflow check surfaces errors before running any engine pass: undefined refs, duplicate labels, missing graphic files, inclusion loops.",
    ]
    for item in items_s5:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        p.text = f"• {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s5, 6.8, 1.6, 5.733, 5.2)
    tb = s5.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CLI OUTPUT: auxflow symbols & check"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    sample_sym = (
        "$ auxflow symbols main.tex\n"
        "labels:\n"
        "  sec:intro -> main.tex:2:1 (counter: section)\n"
        "  ch:methods -> chapters/methods.tex:1:1\n"
        "refs:\n"
        "  sec:intro -> bound to main.tex:2:1 (ref)\n"
        "  ch:methods -> bound to methods.tex:1:1 (pageref)\n"
        "cites:\n"
        "  knuth1984 -> present in refs.bib (1 use)\n"
        "packages:\n"
        "  varioref -> modelled (narrow syntax)\n"
        "  tikz -> unmodelled (OPAQUE)\n\n"
        "$ auxflow check broken.tex\n"
        "error: undefined reference 'fig:missing' (broken.tex:14:22)\n"
        "error: duplicate label 'sec:intro' (broken.tex:45:1)\n"
        "[Exit status: 1]"
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = sample_sym
    p.font.name = FONT_CODE
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 6: The Auxiliary Reference Graph (IR) ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "COMPILER PHASE 7", "The Auxiliary Reference Graph (ARG) Intermediate Representation", 6)

    add_card(s6, 0.8, 1.6, 5.6, 5.2)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "IR FORMAL SPECIFICATION"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    items_s6 = [
        "Instance Facts: ARG vertices are specific fact instances in code, not coarse categories. Nodes carry exact source spans.",
        "Component Tagging: Every fact is tagged either exists (structural presence) or value (typeset content / number / page).",
        "Edge Semantics: Edges E = (u, v, lag, type, reason).\n  - AUX_ROUNDTRIP (lag 1): read from prior .aux pass.\n  - TOOL (lag 1): consumed by external tool (BibTeX).\n  - LAYOUT (lag 0 or 1): pagination and list extents.",
        "Acyclic Normal Case: Ordinary TOC documents remain strictly acyclic in the ARG, matching the fixed-point convergence of standard LaTeX.",
    ]
    for item in items_s6:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        p.text = f"• {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s6, 6.8, 1.6, 5.733, 5.2)
    tb = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE CRITICAL EXISTS / VALUE SPLIT"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    split_expl = (
        "THE PROBLEM IN NAIVE MODELING:\n"
        "A Section produces a TOC entry on page P.\n"
        "The TOC entry shifts document pagination.\n"
        "Pagination alters page P.\n"
        "-> Forms a cyclic graph for EVERY document!\n\n"
        "AUXFLOW'S ARCHITECTURAL SOLUTION:\n"
        "Split TOC_ENTRY into two nodes:\n"
        "1. TOC_ENTRY [exists] (depends only on structure)\n"
        "   --> feeds LIST_EXTENT\n"
        "   --> feeds CONTENT_VOLUME\n"
        "2. TOC_ENTRY [value] (the rendered page number)\n"
        "   <-- fed by CONTENT_VOLUME\n\n"
        "Result: Edges flow in ONE direction.\n"
        "Ordinary documents are provably acyclic."
    )
    p = tf.add_paragraph()
    p.space_before = Pt(10)
    p.text = split_expl
    p.font.name = FONT_CODE
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT

    # ==================== SLIDE 7: End-to-End Walkthrough ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "VERIFICATION & WALKTHROUGH", "Tracing a Forward Reference: Code to IR Graph", 7)

    # 4 horizontal progression boxes
    b_w = 2.65
    b_h = 5.2
    steps = [
        ("1. SOURCE SNIPPET", FONT_CODE, Pt(11), COLOR_TEXT,
         "\\section{Intro}\n\\label{s:intro}\n...\nSee page \\pageref{s:intro}\n\\newpage"),
        ("2. AST & SYMBOLS", FONT_BODY, Pt(11), COLOR_MUTED,
         "• AST Node: MacroCall(\\label)\n• LabelTable: 's:intro'\n  counter: 'section'\n• RefTable: 's:intro'\n  kind: 'pageref'\n• Bound across files: True"),
        ("3. LOWERED IR FACTS", FONT_CODE, Pt(10), COLOR_TEXT,
         "f0: CONTENT_VOLUME\n    [value]\nf1: LABEL_NUMBER(s:intro)\n    [value]\nf2: LABEL_PAGE(s:intro)\n    [value]\nf3: PAGEREF_USE(s:intro)\n    [value]"),
        ("4. ARG EDGES", FONT_BODY, Pt(11), COLOR_MUTED,
         "• f0 -> f2: LAYOUT (lag 0)\n  'pagination sets page'\n• f2 -> f3: AUX_ROUNDTRIP\n  (lag 1)\n  'pageref reads label'\n\nResult: 2-run chain\nAcyclic DAG (Pass 1 -> 2)"),
    ]
    for idx, (stitle, font, fsize, fcolor, content) in enumerate(steps):
        left = 0.8 + idx * (b_w + 0.38)
        add_card(s7, left, 1.6, b_w, b_h)
        tb = s7.shapes.add_textbox(Inches(left + 0.15), Inches(1.8), Inches(b_w - 0.3), Inches(b_h - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.name = FONT_HEADING
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = content
        p.font.name = font
        p.font.size = fsize
        p.font.color.rgb = fcolor

    # ==================== SLIDE 8: Status & Review 3 Bridge ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "SUMMARY & NEXT STAGES", "Review 2 Deliverables Complete; Ready for Review 3", 8)

    add_card(s8, 0.8, 1.6, 5.6, 5.2)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "REVIEW 2 DELIVERABLES ACHIEVED"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    achievements = [
        "Phase 1–7 Implementation Complete: Lexer, Parser, AST Forest, Symbol Tables, Semantics, and ARG IR fully functional.",
        "Zero-Engine Operation: All front-end analysis runs in Python without requiring TeX Live installed.",
        "Robust Test Suite: 100+ unit tests covering token round-trips, error recovery, forward references, and graph lowering.",
        "Type Safety: strict mypy enabled across 40+ source modules with zero type errors.",
    ]
    for item in achievements:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        p.text = f"✓ {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT

    add_card(s8, 6.8, 1.6, 5.733, 5.2)
    tb = s8.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "REVIEW 3 ROADMAP (PHASES 8–16)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    next_steps = [
        ("Phase 8–9: SCC & Taint Analysis", "Iterative Tarjan algorithm detects cycles; taint analysis identifies content amplification risks."),
        ("Phase 10–11: Fixpoint & Classification", "Compute stable pass P; classify into CERTIFIED, BENIGN_CYCLIC, AMPLIFYING, UNKNOWN."),
        ("Phase 12–13: Planner & Verifier", "Emit safe execution plans with dead-code elimination; verify canonical auxiliary state."),
        ("Phase 14–16: 15-Member Benchmark Corpus", "Execute 1050 containerized runs across 7 baselines; prove Gates 1 and 2."),
    ]
    for n_title, n_desc in next_steps:
        p1 = tf.add_paragraph()
        p1.space_before = Pt(10)
        p1.text = f"→ {n_title}"
        p1.font.bold = True
        p1.font.size = Pt(12)
        p1.font.color.rgb = COLOR_TEXT
        p2 = tf.add_paragraph()
        p2.text = f"   {n_desc}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED

    prs.save("presentation/review2-auxflow.pptx")
    print("Saved presentation/review2-auxflow.pptx successfully!")


if __name__ == "__main__":
    build_review2_deck()
