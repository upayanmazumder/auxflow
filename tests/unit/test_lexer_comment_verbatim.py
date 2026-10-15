r"""Phase 2 acceptance (sub-issue #21): comment and verbatim handling.

`%` starts a comment and consumes the following newline plus leading
whitespace on the next line; `\%` does not. `\verb|...|` takes its
delimiter from the next character; the `verbatim` env body is skipped.
Comment and verbatim spans must be tokenised as opaque regions -- one
token each -- never decomposed into their internal characters.
"""

from __future__ import annotations

from auxflow.lexer import CatCode, tokenize

# --- comments -----------------------------------------------------------


def test_comment_consumes_to_end_of_line_including_newline() -> None:
    tokens = tokenize("a% comment\nb", file_id="t.tex")
    assert tokens[0].text == "a"
    assert tokens[1].catcode == CatCode.COMMENT
    assert tokens[1].text == "% comment\n"
    assert tokens[2].text == "b"


def test_comment_consumes_leading_whitespace_on_next_line() -> None:
    tokens = tokenize("a%c\n   b", file_id="t.tex")
    assert tokens[1].catcode == CatCode.COMMENT
    assert tokens[1].text == "%c\n   "
    assert tokens[2].text == "b"


def test_comment_at_end_of_input_with_no_trailing_newline() -> None:
    tokens = tokenize("a%c", file_id="t.tex")
    assert tokens[1].catcode == CatCode.COMMENT
    assert tokens[1].text == "%c"


def test_comment_span_is_a_single_opaque_token() -> None:
    tokens = tokenize("%this {has} $syntax$ \\in it\n", file_id="t.tex")
    comment_tokens = [t for t in tokens if t.catcode == CatCode.COMMENT]
    assert len(comment_tokens) == 1
    assert comment_tokens[0].text == "%this {has} $syntax$ \\in it\n"


def test_escaped_percent_is_not_a_comment() -> None:
    tokens = tokenize("a\\%b", file_id="t.tex")
    assert [t.catcode for t in tokens] == [
        CatCode.LETTER,
        CatCode.CONTROL_SEQUENCE,
        CatCode.LETTER,
    ]
    assert tokens[1].text == "\\%"
    assert all(t.catcode != CatCode.COMMENT for t in tokens)


# --- \verb ----------------------------------------------------------------


def test_verb_takes_delimiter_from_next_character() -> None:
    tokens = tokenize("\\verb|a{b}c|", file_id="t.tex")
    assert tokens[0].catcode == CatCode.CONTROL_SEQUENCE
    assert tokens[0].text == "\\verb"
    assert tokens[1].catcode == CatCode.VERBATIM
    assert tokens[1].text == "|a{b}c|"
    assert len(tokens) == 2


def test_verb_with_a_different_delimiter() -> None:
    tokens = tokenize("\\verb+x+", file_id="t.tex")
    assert tokens[1].catcode == CatCode.VERBATIM
    assert tokens[1].text == "+x+"


def test_verb_body_is_never_decomposed_into_syntax() -> None:
    tokens = tokenize("\\verb|\\foo{bar}|", file_id="t.tex")
    assert len(tokens) == 2
    assert tokens[1].text == "|\\foo{bar}|"


def test_unterminated_verb_consumes_to_end_of_input() -> None:
    tokens = tokenize("\\verb|unterminated", file_id="t.tex")
    assert tokens[1].catcode == CatCode.VERBATIM
    assert tokens[1].text == "|unterminated"


# --- verbatim environment ---------------------------------------------------


def test_verbatim_environment_body_is_one_opaque_token() -> None:
    source = "\\begin{verbatim}\\foo{bar}%not a comment\\end{verbatim}"
    tokens = tokenize(source, file_id="t.tex")
    verbatim_tokens = [t for t in tokens if t.catcode == CatCode.VERBATIM]
    assert len(verbatim_tokens) == 1
    assert verbatim_tokens[0].text == "\\foo{bar}%not a comment"


def test_verbatim_environment_begin_and_end_markers_tokenise_normally() -> None:
    source = "\\begin{verbatim}x\\end{verbatim}"
    tokens = tokenize(source, file_id="t.tex")
    cs_tokens = [t.text for t in tokens if t.catcode == CatCode.CONTROL_SEQUENCE]
    assert cs_tokens == ["\\begin", "\\end"]
    group_tokens = [t.catcode for t in tokens if t.catcode == CatCode.BEGIN_GROUP]
    assert len(group_tokens) == 2


def test_unterminated_verbatim_environment_consumes_to_end_of_input() -> None:
    source = "\\begin{verbatim}never closed"
    tokens = tokenize(source, file_id="t.tex")
    verbatim_tokens = [t for t in tokens if t.catcode == CatCode.VERBATIM]
    assert len(verbatim_tokens) == 1
    assert verbatim_tokens[0].text == "never closed"


def test_empty_verbatim_environment_body_emits_no_verbatim_token() -> None:
    source = "\\begin{verbatim}\\end{verbatim}"
    tokens = tokenize(source, file_id="t.tex")
    assert not any(t.catcode == CatCode.VERBATIM for t in tokens)
