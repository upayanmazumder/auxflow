r"""Discover literal package requirements in local class and style files.

This is source inventory, not TeX execution: conditional loads, macro-generated
names and external files cannot be resolved here. A listed requirement is not a
claim that its package's effects are modelled or even that its branch runs.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from auxflow.lexer import CatCode, tokenize
from auxflow.lexer.tokens import Token
from auxflow.parser.spans import Span

_LITERAL_NAME = re.compile(r"[A-Za-z0-9_./-]+\Z")
_WHITESPACE = {CatCode.SPACE, CatCode.END_OF_LINE, CatCode.COMMENT}


def local_file(name: str, suffix: str, source: Path, root: Path) -> Path | None:
    """Find only project-local files, without searching a TeX installation."""
    if not _LITERAL_NAME.fullmatch(name):
        return None
    relative = Path(f"{name}{suffix}")
    for directory in (source.parent, root.parent):
        candidate = directory / relative
        if candidate.is_file():
            return candidate.resolve()
    return None


def _skip_space(tokens: list[Token], index: int) -> int:
    while index < len(tokens) and tokens[index].catcode in _WHITESPACE:
        index += 1
    return index


def _literal_argument(tokens: list[Token], index: int) -> tuple[str, int] | None:
    """Read an optional argument followed by one simple literal brace group."""
    index = _skip_space(tokens, index)
    if index < len(tokens) and tokens[index].text == "[":
        depth = 1
        index += 1
        while index < len(tokens) and depth:
            token = tokens[index]
            if token.catcode not in {CatCode.COMMENT, CatCode.VERBATIM}:
                if token.text == "[":
                    depth += 1
                elif token.text == "]":
                    depth -= 1
            index += 1
        if depth:
            return None
        index = _skip_space(tokens, index)
    if index >= len(tokens) or tokens[index].catcode != CatCode.BEGIN_GROUP:
        return None
    index += 1
    content: list[str] = []
    while index < len(tokens) and tokens[index].catcode != CatCode.END_GROUP:
        token = tokens[index]
        if token.catcode not in {
            CatCode.LETTER,
            CatCode.OTHER,
            CatCode.SPACE,
            CatCode.END_OF_LINE,
            CatCode.COMMENT,
        }:
            return None
        if token.catcode != CatCode.COMMENT:
            content.append(token.text)
        index += 1
    if index >= len(tokens):
        return None
    return "".join(content), tokens[index].offset + len(tokens[index].text)


def requirements(path: Path) -> Iterator[tuple[str, Span]]:
    """Yield literal names and source spans of uncommented RequirePackage calls."""
    source = path.read_text(encoding="utf-8")
    tokens = tokenize(source, file_id=str(path))
    for index, token in enumerate(tokens):
        if token.catcode != CatCode.CONTROL_SEQUENCE or token.text != r"\RequirePackage":
            continue
        argument = _literal_argument(tokens, index + 1)
        if argument is None:
            continue
        names, end = argument
        for name in names.split(","):
            name = name.strip()
            if _LITERAL_NAME.fullmatch(name):
                yield name, Span(str(path), token.offset, end)
