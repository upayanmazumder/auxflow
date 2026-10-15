"""Phase 2 acceptance (sub-issue #20): category-code table and single-pass
table-driven scan.

Covers every one of the 16 standard category codes and both control-sequence
shapes (maximal letter run; exactly one other character). Comment-consuming
and verbatim-skipping behaviour belongs to sub-issue #21 and is tested there;
here `%` and `\\verb` are exercised only as plain catcode classification.
"""

from __future__ import annotations

from auxflow.lexer import CatCode, Token, tokenize
from auxflow.lexer.catcode import catcode_of


def _single(source: str) -> Token:
    tokens = tokenize(source, file_id="t.tex")
    assert len(tokens) == 1
    return tokens[0]


# --- each catcode class, via catcode_of directly -----------------------------


def test_catcode_escape() -> None:
    assert catcode_of("\\") == CatCode.ESCAPE


def test_catcode_begin_group() -> None:
    assert catcode_of("{") == CatCode.BEGIN_GROUP


def test_catcode_end_group() -> None:
    assert catcode_of("}") == CatCode.END_GROUP


def test_catcode_math_shift() -> None:
    assert catcode_of("$") == CatCode.MATH_SHIFT


def test_catcode_alignment_tab() -> None:
    assert catcode_of("&") == CatCode.ALIGNMENT_TAB


def test_catcode_end_of_line() -> None:
    assert catcode_of("\n") == CatCode.END_OF_LINE


def test_catcode_parameter() -> None:
    assert catcode_of("#") == CatCode.PARAMETER


def test_catcode_superscript() -> None:
    assert catcode_of("^") == CatCode.SUPERSCRIPT


def test_catcode_subscript() -> None:
    assert catcode_of("_") == CatCode.SUBSCRIPT


def test_catcode_ignored() -> None:
    assert catcode_of("\x00") == CatCode.IGNORED


def test_catcode_space() -> None:
    assert catcode_of(" ") == CatCode.SPACE
    assert catcode_of("\t") == CatCode.SPACE


def test_catcode_letter() -> None:
    assert catcode_of("a") == CatCode.LETTER
    assert catcode_of("Z") == CatCode.LETTER


def test_catcode_other() -> None:
    assert catcode_of("1") == CatCode.OTHER
    assert catcode_of(".") == CatCode.OTHER


def test_catcode_active() -> None:
    assert catcode_of("~") == CatCode.ACTIVE


def test_catcode_comment() -> None:
    assert catcode_of("%") == CatCode.COMMENT


def test_catcode_invalid() -> None:
    assert catcode_of("\x7f") == CatCode.INVALID


def test_catcode_non_latin1_defaults_to_other() -> None:
    assert catcode_of("Ā") == CatCode.OTHER  # U+0100, outside the 256-entry table


# --- both control-sequence shapes --------------------------------------------


def test_control_sequence_maximal_letter_run() -> None:
    tok = _single("\\section")
    assert tok.catcode == CatCode.CONTROL_SEQUENCE
    assert tok.text == "\\section"


def test_control_sequence_letter_run_stops_at_non_letter() -> None:
    tokens = tokenize("\\ref{x}", file_id="t.tex")
    assert tokens[0].catcode == CatCode.CONTROL_SEQUENCE
    assert tokens[0].text == "\\ref"
    assert tokens[1].catcode == CatCode.BEGIN_GROUP


def test_control_sequence_single_other_character() -> None:
    tok = _single("\\%")
    assert tok.catcode == CatCode.CONTROL_SEQUENCE
    assert tok.text == "\\%"


def test_control_sequence_single_other_character_backslash() -> None:
    tok = _single("\\\\")
    assert tok.catcode == CatCode.CONTROL_SEQUENCE
    assert tok.text == "\\\\"


def test_control_sequence_lone_escape_at_end_of_input() -> None:
    tok = _single("\\")
    assert tok.catcode == CatCode.CONTROL_SEQUENCE
    assert tok.text == "\\"


# --- token position bookkeeping ----------------------------------------------


def test_token_positions_track_line_and_column() -> None:
    tokens = tokenize("a\nb", file_id="t.tex")
    assert (tokens[0].line, tokens[0].col, tokens[0].offset) == (1, 1, 0)
    assert (tokens[1].line, tokens[1].col, tokens[1].offset) == (1, 2, 1)  # the newline itself
    assert (tokens[2].line, tokens[2].col, tokens[2].offset) == (2, 1, 2)


def test_tokens_carry_file_id() -> None:
    tok = _single("x")
    assert tok.file_id == "t.tex"


def test_empty_source_produces_no_tokens() -> None:
    assert tokenize("", file_id="t.tex") == []
