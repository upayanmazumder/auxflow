"""The TeX category-code table.

Sixteen category codes (0-15), per the standard LaTeX/TeX default assignment.
`CATEGORY_TABLE` classifies every one of the 256 possible byte values; code
points above 255 (non-ASCII text) default to OTHER, since AuxFlow's declared
subset does not depend on Unicode letter classification.

AuxFlow does not support category-code redefinition (docs/SCOPE.md DO NOT
BUILD: "Invalidates the lexer's own assumptions"), so this table is fixed for
the lifetime of a run.
"""

from __future__ import annotations

from enum import IntEnum


class CatCode(IntEnum):
    """The 16 standard TeX category codes, plus two AuxFlow-internal token
    kinds for constructs the scanner groups into a single `Token`: a full
    control sequence (escape plus its name) and an opaque verbatim span.
    Only values 0-15 ever appear in `CATEGORY_TABLE`; 16 and 17 are assigned
    by the scanner, never looked up per-character.
    """

    ESCAPE = 0
    BEGIN_GROUP = 1
    END_GROUP = 2
    MATH_SHIFT = 3
    ALIGNMENT_TAB = 4
    END_OF_LINE = 5
    PARAMETER = 6
    SUPERSCRIPT = 7
    SUBSCRIPT = 8
    IGNORED = 9
    SPACE = 10
    LETTER = 11
    OTHER = 12
    ACTIVE = 13
    COMMENT = 14
    INVALID = 15
    CONTROL_SEQUENCE = 16
    VERBATIM = 17


def _build_category_table() -> tuple[CatCode, ...]:
    table = [CatCode.OTHER] * 256
    table[ord("\\")] = CatCode.ESCAPE
    table[ord("{")] = CatCode.BEGIN_GROUP
    table[ord("}")] = CatCode.END_GROUP
    table[ord("$")] = CatCode.MATH_SHIFT
    table[ord("&")] = CatCode.ALIGNMENT_TAB
    table[ord("\n")] = CatCode.END_OF_LINE
    table[ord("#")] = CatCode.PARAMETER
    table[ord("^")] = CatCode.SUPERSCRIPT
    table[ord("_")] = CatCode.SUBSCRIPT
    table[0] = CatCode.IGNORED  # NUL
    table[ord(" ")] = CatCode.SPACE
    table[ord("\t")] = CatCode.SPACE
    for letter in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        table[ord(letter)] = CatCode.LETTER
    table[ord("~")] = CatCode.ACTIVE
    table[ord("%")] = CatCode.COMMENT
    table[0x7F] = CatCode.INVALID  # DEL
    return tuple(table)


CATEGORY_TABLE: tuple[CatCode, ...] = _build_category_table()


def catcode_of(char: str) -> CatCode:
    """Category code of a single character. Non-Latin-1 code points (outside
    the 256-entry table) default to OTHER."""
    codepoint = ord(char)
    if codepoint < 256:
        return CATEGORY_TABLE[codepoint]
    return CatCode.OTHER
