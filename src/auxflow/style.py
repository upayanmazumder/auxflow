"""Terminal styling for human-facing CLI output.

Machine-readable output (JSON, DOT, tokens, AST) is never styled. Colour is on
only when the stream is a terminal, `NO_COLOR` is unset, and `TERM` is not
`dumb`. `--color always|never` and `FORCE_COLOR` override that check.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Literal, TextIO

ColorMode = Literal["auto", "always", "never"]

_RESET = "\033[0m"
_CODES = {
    "bold": "1",
    "dim": "2",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "cyan": "36",
}
_STATE_STYLE = {
    "CERTIFIED": ("bold", "green"),
    "BENIGN_CYCLIC": ("bold", "cyan"),
    "AMPLIFYING": ("bold", "red"),
    "UNKNOWN": ("bold", "yellow"),
}
_STATE_WORDS = re.compile(r"\b(CERTIFIED|BENIGN_CYCLIC|AMPLIFYING|UNKNOWN)\b")
_SEVERITY_WORDS = re.compile(r"\b(error|warning):")

_mode: ColorMode = "auto"


def configure(mode: ColorMode) -> None:
    """Set the colour mode for the rest of the process."""
    global _mode
    _mode = mode


def enabled(stream: TextIO | None = None) -> bool:
    """Whether output written to `stream` (default stdout) should carry colour."""
    if _mode == "always":
        return True
    if _mode == "never":
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    target = stream if stream is not None else sys.stdout
    return target.isatty() and os.environ.get("TERM", "") != "dumb"


def paint(text: str, *styles: str, stream: TextIO | None = None) -> str:
    """Wrap `text` in ANSI codes for `styles`, or return it unchanged."""
    if not styles or not enabled(stream):
        return text
    prefix = "".join(f"\033[{_CODES[name]}m" for name in styles)
    return f"{prefix}{text}{_RESET}"


def style_report(text: str, stream: TextIO | None = None) -> str:
    """Colour state names and severity labels in a rendered human report."""
    if not enabled(stream):
        return text

    def state(match: re.Match[str]) -> str:
        return paint(match.group(1), *_STATE_STYLE[match.group(1)], stream=stream)

    def severity(match: re.Match[str]) -> str:
        colour = "red" if match.group(1) == "error" else "yellow"
        return paint(match.group(0), "bold", colour, stream=stream)

    return _SEVERITY_WORDS.sub(severity, _STATE_WORDS.sub(state, text))
