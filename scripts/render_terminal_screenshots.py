"""Render real captured CLI output as terminal-style screenshot images, for
embedding in docs/review2-document.docx. Every string below is copied
verbatim from an actual `auxflow` run (see commit message / session log),
not invented.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BG = (13, 20, 30)
BAR = (28, 38, 51)
BORDER = (45, 58, 75)
TEXT = (219, 226, 235)
GREEN = (80, 220, 140)
RED = (240, 100, 100)
AMBER = (240, 190, 90)
DOT_RED = (237, 106, 94)
DOT_AMBER = (245, 191, 79)
DOT_GREEN = (97, 194, 83)

FONT_PATH_CANDIDATES = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_BOLD_CANDIDATES + FONT_PATH_CANDIDATES if bold else FONT_PATH_CANDIDATES
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_terminal(filename: str, title: str, lines: list[tuple[str, tuple[int, int, int]]]) -> None:
    font = _font(15)
    font_bold = _font(15, bold=True)
    pad_x, pad_y = 24, 18
    line_h = 22
    bar_h = 34
    width = 980
    height = bar_h + pad_y * 2 + line_h * len(lines)

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, width, bar_h], fill=BAR)
    for i, color in enumerate((DOT_RED, DOT_AMBER, DOT_GREEN)):
        draw.ellipse([16 + i * 22, bar_h // 2 - 6, 16 + i * 22 + 12, bar_h // 2 + 6], fill=color)
    draw.text((width // 2, bar_h // 2), title, font=font_bold, fill=(180, 190, 200), anchor="mm")
    draw.rectangle([0, 0, width - 1, height - 1], outline=BORDER, width=2)

    y = bar_h + pad_y
    for text, color in lines:
        f = font_bold if text.startswith("$ ") else font
        draw.text((pad_x, y), text, font=f, fill=color)
        y += line_h

    img.save(OUT_DIR / filename)
    print(f"Saved {OUT_DIR / filename}")


def main() -> None:
    render_terminal(
        "01-tokens.png",
        "auxflow tokens: Phase 2: Lexical Analysis",
        [
            ("$ auxflow tokens main.tex", TEXT),
            ("1:1  CONTROL_SEQUENCE  '\\\\documentclass'", TEXT),
            ("1:15 BEGIN_GROUP        '{'", TEXT),
            ("1:16 LETTER             'a'", TEXT),
            ("1:17 LETTER             'r'", TEXT),
            ("1:18 LETTER             't'", TEXT),
            ("1:19 LETTER             'i'", TEXT),
            ("1:20 LETTER             'c'", TEXT),
            ("1:21 LETTER             'l'", TEXT),
            ("1:22 LETTER             'e'", TEXT),
            ("1:23 END_GROUP          '}'", TEXT),
            ("1:24 END_OF_LINE        '\\\\n'", TEXT),
            ("2:1  CONTROL_SEQUENCE   '\\\\begin'", TEXT),
        ],
    )

    render_terminal(
        "02-ast.png",
        "auxflow ast: Phase 3-4: Parsing & AST",
        [
            ("$ auxflow ast main.tex", TEXT),
            ("=== /tmp/demo/main.tex ===", (150, 160, 175)),
            ("Document [/tmp/demo/main.tex:0-335]", TEXT),
            ("  Preamble [/tmp/demo/main.tex:0-24]", TEXT),
            ("    MacroCall(\\\\documentclass) [/tmp/demo/main.tex:0-23]", TEXT),
            ("      Text('article') [/tmp/demo/main.tex:15-22]", TEXT),
            ("    Text('\\\\n') [/tmp/demo/main.tex:23-24]", TEXT),
            ("  Environment(document) [/tmp/demo/main.tex:24-334]", TEXT),
            ("    Text('\\\\n') [/tmp/demo/main.tex:40-41]", TEXT),
            ("    Sectioning(section) [/tmp/demo/main.tex:41-74]", TEXT),
            ("      Text('The initial observation') [...50-73]", TEXT),
            ("    MacroCall(\\\\label) [/tmp/demo/main.tex:74-97]", TEXT),
            ("      Text('sec:observation') [...81-96]", TEXT),
        ],
    )

    render_terminal(
        "03-symbols.png",
        "auxflow symbols: Phase 5: Symbol Tables",
        [
            ("$ auxflow symbols main.tex", TEXT),
            ("LabelTable:", AMBER),
            ("  sec:observation: /tmp/demo/main.tex:74-97", TEXT),
            ("    counter=section duplicate=False", TEXT),
            ("RefTable:", AMBER),
            ("  sec:observation: ref /tmp/demo/main.tex:236-257", TEXT),
            ("    -> /tmp/demo/main.tex:74-97", TEXT),
            ("CiteTable:", AMBER),
            ("PackageTable:", AMBER),
            ("FileTable:", AMBER),
            ("  /tmp/demo/main.tex: path=/tmp/demo/main.tex", TEXT),
            ("    includer=- reachable=True opaque=False", TEXT),
            ("CounterTable:", AMBER),
        ],
    )

    render_terminal(
        "04-check.png",
        "auxflow check: Phase 6: Semantic Analysis",
        [
            ("$ auxflow check main.tex", TEXT),
            ("(no diagnostics)", GREEN),
            ("$ echo $?", TEXT),
            ("0", GREEN),
            ("", TEXT),
            ("$ auxflow check broken.tex", TEXT),
            ("broken.tex:45-62: error: undefined reference: 'fig:missing'", RED),
            ("broken.tex:100-123: error: duplicate label: 'sec:observation'", RED),
            ("$ echo $?", TEXT),
            ("1", RED),
        ],
    )

    render_terminal(
        "05-graph.png",
        "auxflow graph: Phase 7: Intermediate Representation",
        [
            ("$ auxflow graph main.tex", TEXT),
            ("digraph arg {", TEXT),
            ("  rankdir=LR;", TEXT),
            ('  f0 [label="LABEL_NUMBER\\\\nsec:observation\\\\n[value]"];', TEXT),
            ('  f1 [label="LABEL_PAGE\\\\nsec:observation\\\\n[value]"];', TEXT),
            ('  f2 [label="REF_USE\\\\nsec:observation\\\\n[value]"];', TEXT),
            ('  f0 -> f2 [label="AUX_ROUNDTRIP lag 1"];', TEXT),
            ("}", TEXT),
        ],
    )

    render_terminal(
        "06-classify-certified.png",
        "auxflow classify: CERTIFIED (acyclic)",
        [
            ("$ auxflow classify main.tex", TEXT),
            ("auxflow: CERTIFIED -- 2 runs", GREEN),
            ("", TEXT),
            ("  longest dependency chain (stable_pass 1):", TEXT),
            ("    LABEL_NUMBER(sec:observation)  main.tex:3:34  -> 1", TEXT),
            ("    LABEL_PAGE(sec:observation)    main.tex:3:34  -> 1", TEXT),
            ("    REF_USE(sec:observation)       main.tex:7:39  run 2", TEXT),
            ("", TEXT),
            ("  The facts above require all 2 runs to stabilise.", TEXT),
        ],
    )

    render_terminal(
        "07-classify-amplifying.png",
        "auxflow classify: AMPLIFYING (unmodelled risk, refused)",
        [
            ("$ auxflow classify cycle.tex", TEXT),
            ("auxflow: AMPLIFYING CYCLE -- this document may not converge.", RED),
            ("", TEXT),
            ("  cycle (3 facts):", TEXT),
            ("    PAGEREF_USE(end:generated)  cycle.tex:5:32", TEXT),
            ("      -> CONTENT_VOLUME  cycle.tex:8:3  STRUCTURAL", TEXT),
            ("      -> LABEL_PAGE(end:generated)  cycle.tex:10:29", TEXT),
            ("      -> PAGEREF_USE(end:generated)", TEXT),
            ("", TEXT),
            ("  No build plan emitted. Use --force to execute under a cap of 6 runs.", AMBER),
            ("$ echo $?", TEXT),
            ("1", RED),
        ],
    )

    render_terminal(
        "08-verification.png",
        "Quality gates: pytest, mypy, ruff",
        [
            ("$ python -m pytest", TEXT),
            ("245 passed, 1 skipped, 8 warnings in 2.16s", GREEN),
            ("", TEXT),
            ("$ mypy", TEXT),
            ("Success: no issues found in 41 source files", GREEN),
            ("", TEXT),
            ("$ ruff check src tests", TEXT),
            ("All checks passed!", GREEN),
        ],
    )


if __name__ == "__main__":
    main()
