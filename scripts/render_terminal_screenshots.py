"""Render live `auxflow` output as terminal-style screenshot images.

Every screenshot comes from a real run of the installed `auxflow` command on a
bench/corpus document. Nothing is typed by hand. Run from the repository root,
inside the environment where `auxflow` is installed:

    python scripts/render_terminal_screenshots.py

Output: docs/screenshots/*.png (review documents) and paper/figures/shot-*.png (paper).

For the `auxflow run` screenshot, the pdfTeX transcript is dropped. Only the
lines that AuxFlow itself prints are kept.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "bench" / "corpus"
OUT_DIR = ROOT / "docs" / "screenshots"
WORK_ROOT = Path("/tmp/auxflow-demo")

BG = (13, 20, 30)
BAR = (28, 38, 51)
BORDER = (45, 58, 75)
TEXT = (219, 226, 235)
MUTED = (150, 160, 175)
GREEN = (80, 220, 140)
RED = (240, 100, 100)
AMBER = (240, 190, 90)
DOT_RED = (237, 106, 94)
DOT_AMBER = (245, 191, 79)
DOT_GREEN = (97, 194, 83)

FONT_REGULAR = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]
FONT_BOLD = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]

FONT_SIZE = 15
LINE_HEIGHT = 22
MAX_COLUMNS = 104
SCALE = 2  # render at 2x so the text stays sharp in print


@dataclass(frozen=True)
class Shot:
    """One screenshot: a title, a corpus document, and the commands to run on it."""

    filename: str
    title: str
    document: str
    commands: tuple[str, ...]
    max_lines: int | None = None  # cut long output and mark the cut
    keep: str | None = None  # regex: keep only matching output lines
    columns: int = MAX_COLUMNS  # wrap width, in characters
    out_dir: Path = OUT_DIR


SHOTS = (
    Shot("01-tokens.png", "auxflow tokens", "b02_backref", ("auxflow tokens main.tex",), 14),
    Shot("02-ast.png", "auxflow ast", "b02_backref", ("auxflow ast main.tex",), 16),
    Shot("03-symbols.png", "auxflow symbols", "b02_backref", ("auxflow symbols main.tex",), 18),
    Shot("04-check.png", "auxflow check", "b05_toc", ("auxflow check main.tex",)),
    Shot("05-graph.png", "auxflow graph", "b02_backref", ("auxflow graph main.tex",), 22),
    Shot(
        "06-classify-certified.png",
        "auxflow classify: CERTIFIED",
        "b06_bib",
        ("auxflow classify main.tex", "auxflow plan --explain main.tex"),
    ),
    Shot(
        "07-classify-amplifying.png",
        "auxflow classify: AMPLIFYING",
        "b08_cycle",
        ("auxflow classify main.tex",),
    ),
    Shot(
        "08-verification.png",
        "auxflow run: runtime verification",
        "b05_toc",
        ("auxflow run main.tex",),
        keep=r"^(auxflow:|\{|Done)",
    ),
    Shot(
        "09-classify-unknown.png",
        "auxflow classify: UNKNOWN",
        "b11_width",
        ("auxflow classify main.tex",),
    ),
    Shot(
        "10-run-forced.png",
        "auxflow run --force: capped run",
        "b08_cycle",
        ("auxflow run --force main.tex",),
        keep=r"^(auxflow:|\{|Done|Stopped)",
    ),
)


# Narrow shots for the paper. Each fits one column of a two-column page.
PAPER_DIR = ROOT / "paper" / "figures"
PAPER_COLUMNS = 58
PAPER_SHOTS = (
    Shot(
        "shot-amplifying.png",
        "auxflow classify",
        "b08_cycle",
        ("auxflow classify main.tex",),
        max_lines=21,
        columns=PAPER_COLUMNS,
        out_dir=PAPER_DIR,
    ),
    Shot(
        "shot-plan.png",
        "auxflow plan --explain",
        "b06_bib",
        ("auxflow plan --explain main.tex",),
        columns=PAPER_COLUMNS,
        out_dir=PAPER_DIR,
    ),
    Shot(
        "shot-unknown.png",
        "auxflow classify",
        "b11_width",
        ("auxflow classify main.tex",),
        max_lines=9,
        columns=PAPER_COLUMNS,
        out_dir=PAPER_DIR,
    ),
    Shot(
        "shot-run.png",
        "auxflow run --force",
        "b08_cycle",
        ("auxflow run --force main.tex",),
        keep=r"^(auxflow:|\{|Done|Stopped)",
        columns=PAPER_COLUMNS,
        out_dir=PAPER_DIR,
    ),
)


def _font(candidates: list[str]) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, FONT_SIZE * SCALE)
    return ImageFont.load_default()


def _wrap(line: str, columns: int) -> list[str]:
    if len(line) <= columns:
        return [line]
    indent = len(line) - len(line.lstrip(" "))
    pieces: list[str] = []
    rest = line
    prefix = ""
    while len(rest) + len(prefix) > columns:
        cut = rest.rfind(" ", 0, columns - len(prefix))
        if cut <= indent:
            cut = columns - len(prefix)
        pieces.append(prefix + rest[:cut].rstrip())
        rest = rest[cut:].lstrip()
        prefix = " " * (indent + 2)
    pieces.append(prefix + rest)
    return pieces


def _color(line: str) -> tuple[int, int, int]:
    if line.startswith("$ "):
        return TEXT
    if re.search(r"CERTIFIED|CONVERGED|No problems|Done\.", line):
        return GREEN
    if re.search(r"AMPLIFYING|error|cap_exceeded|tool_error|No build plan", line):
        return RED
    if re.search(r"UNKNOWN|BENIGN_CYCLIC|warning|Next:|cap of", line):
        return AMBER
    if line.startswith(("In plain terms", "...")):
        return MUTED
    return TEXT


def _run(command: str, directory: Path, keep: str | None) -> list[str]:
    env = dict(os.environ, NO_COLOR="1", AUXFLOW_NO_UPDATE_CHECK="1", COLUMNS="100")
    done = subprocess.run(
        command,
        shell=True,
        cwd=directory,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=300,
    )
    lines = done.stdout.splitlines()
    if keep:
        pattern = re.compile(keep)
        lines = [line for line in lines if pattern.match(line)]
    return lines


def _capture(shot: Shot) -> list[tuple[str, tuple[int, int, int]]]:
    rows: list[tuple[str, tuple[int, int, int]]] = []
    # A fixed location keeps the paths that auxflow prints the same on every run.
    shutil.rmtree(WORK_ROOT, ignore_errors=True)
    try:
        directory = WORK_ROOT / "doc"
        shutil.copytree(CORPUS / shot.document, directory)
        shutil.copytree(CORPUS / "shared", WORK_ROOT / "shared")
        for command in shot.commands:
            rows.append((f"$ {command}", TEXT))
            lines = [
                piece
                for line in _run(command, directory, shot.keep)
                for piece in _wrap(line, shot.columns)
            ]
            if shot.max_lines is not None and len(lines) > shot.max_lines:
                lines = [*lines[: shot.max_lines], "..."]
            rows.extend((line, _color(line)) for line in lines)
    finally:
        shutil.rmtree(WORK_ROOT, ignore_errors=True)
    return rows


def render(shot: Shot) -> Path:
    rows = _capture(shot)
    regular = _font(FONT_REGULAR)
    bold = _font(FONT_BOLD)
    pad_x, pad_y, bar_h = 24 * SCALE, 18 * SCALE, 34 * SCALE
    line_h = LINE_HEIGHT * SCALE
    columns = max(len(text) for text, _ in rows)
    char_w = regular.getlength("M")
    width = int(max(360 * SCALE, min(columns, shot.columns) * char_w + pad_x * 2))
    height = bar_h + pad_y * 2 + line_h * len(rows)

    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width, bar_h], fill=BAR)
    for index, color in enumerate((DOT_RED, DOT_AMBER, DOT_GREEN)):
        x = (16 + index * 22) * SCALE
        top, bottom = bar_h // 2 - 6 * SCALE, bar_h // 2 + 6 * SCALE
        draw.ellipse([x, top, x + 12 * SCALE, bottom], fill=color)
    draw.text((width // 2, bar_h // 2), shot.title, font=bold, fill=(180, 190, 200), anchor="mm")
    draw.rectangle([0, 0, width - 1, height - 1], outline=BORDER, width=2 * SCALE)

    y = bar_h + pad_y
    for text, color in rows:
        draw.text((pad_x, y), text, font=bold if text.startswith("$ ") else regular, fill=color)
        y += line_h

    shot.out_dir.mkdir(parents=True, exist_ok=True)
    path = shot.out_dir / shot.filename
    image.save(path)
    return path


def main() -> None:
    if shutil.which("auxflow") is None:
        raise SystemExit("error: auxflow is not on PATH. Install it first (make install).")
    for shot in (*SHOTS, *PAPER_SHOTS):
        print(f"saved {render(shot).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
