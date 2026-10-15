r"""Phase 3 acceptance (sub-issue #23): recursive-descent core with one-token
lookahead.

Covers preamble, environments, groups, sectioning, and bare macro calls,
with correct nesting. Argument-signature-driven parsing is a separate
sub-issue (#24) and is not exercised here: every non-sectioning,
non-\begin/\end control sequence is expected to parse as a bare MacroCall.
"""

from __future__ import annotations

from auxflow.lexer import tokenize
from auxflow.parser import (
    Comment,
    Document,
    Environment,
    Group,
    MacroCall,
    Preamble,
    Sectioning,
    Text,
    VerbatimBlock,
    parse,
)


def _parse(source: str):
    tokens = tokenize(source, file_id="t.tex")
    return parse(tokens, file_id="t.tex")


# --- groups, with nesting -----------------------------------------------


def test_simple_group() -> None:
    result = _parse("{abc}")
    assert result.diagnostics == ()
    (group,) = result.document.children
    assert isinstance(group, Group)
    (text,) = group.children
    assert isinstance(text, Text)
    assert text.text == "abc"


def test_nested_groups() -> None:
    result = _parse("{a{b{c}d}e}")
    assert result.diagnostics == ()
    (outer,) = result.document.children
    assert isinstance(outer, Group)
    assert [type(n) for n in outer.children] == [Text, Group, Text]
    mid = outer.children[1]
    assert isinstance(mid, Group)
    assert [type(n) for n in mid.children] == [Text, Group, Text]
    inner = mid.children[1]
    assert isinstance(inner, Group)
    (inner_text,) = inner.children
    assert inner_text.text == "c"


def test_group_span_covers_braces() -> None:
    result = _parse("x{abc}y")
    group = result.document.children[1]
    assert isinstance(group, Group)
    assert group.span.start == 1
    assert group.span.end == 6  # '{abc}' is 5 chars starting at offset 1


# --- environments, with nesting ------------------------------------------


def test_environment_with_body() -> None:
    result = _parse("\\begin{itemize}\\item x\\end{itemize}")
    assert result.diagnostics == ()
    (env,) = result.document.children
    assert isinstance(env, Environment)
    assert env.name == "itemize"
    item_call = env.children[0]
    assert isinstance(item_call, MacroCall)
    assert item_call.name == "\\item"


def test_nested_environments() -> None:
    source = "\\begin{outer}\\begin{inner}x\\end{inner}\\end{outer}"
    result = _parse(source)
    assert result.diagnostics == ()
    (outer,) = result.document.children
    assert isinstance(outer, Environment)
    assert outer.name == "outer"
    (inner,) = outer.children
    assert isinstance(inner, Environment)
    assert inner.name == "inner"


def test_mismatched_end_name_does_not_close_the_environment() -> None:
    # \end{wrong} must not terminate \begin{right}; only an exact name
    # match does. The document-level \end{right} is what actually closes it.
    source = "\\begin{right}\\end{wrong}\\end{right}"
    result = _parse(source)
    (env,) = result.document.children
    assert isinstance(env, Environment)
    assert env.name == "right"
    # the stray \end{wrong} is consumed as ordinary content inside 'right'
    inner_macro_calls = [n for n in env.children if isinstance(n, MacroCall)]
    assert any(m.name == "\\end" for m in inner_macro_calls)


def test_document_environment_splits_preamble_from_body() -> None:
    source = "\\documentclass{article}\\begin{document}hi\\end{document}"
    result = _parse(source)
    assert result.diagnostics == ()
    preamble, doc_env = result.document.children
    assert isinstance(preamble, Preamble)
    assert isinstance(preamble.children[0], MacroCall)
    assert preamble.children[0].name == "\\documentclass"
    assert isinstance(doc_env, Environment)
    assert doc_env.name == "document"


def test_no_document_environment_means_no_preamble_wrapper() -> None:
    result = _parse("just text")
    assert not any(isinstance(n, Preamble) for n in result.document.children)


# --- sectioning -------------------------------------------------------------


def test_section_with_title() -> None:
    result = _parse("\\section{Introduction}")
    (sec,) = result.document.children
    assert isinstance(sec, Sectioning)
    assert sec.level == "section"
    (title_text,) = sec.title
    assert isinstance(title_text, Text)
    assert title_text.text == "Introduction"


def test_chapter_and_subsection_levels() -> None:
    result = _parse("\\chapter{One}\\subsection{Two}")
    chapter, subsection = result.document.children
    assert isinstance(chapter, Sectioning)
    assert chapter.level == "chapter"
    assert isinstance(subsection, Sectioning)
    assert subsection.level == "subsection"


def test_sectioning_title_can_contain_nested_groups() -> None:
    result = _parse("\\section{A {bold} word}")
    (sec,) = result.document.children
    assert isinstance(sec, Sectioning)
    assert [type(n) for n in sec.title] == [Text, Group, Text]


def test_section_without_title_degrades_to_bare_macro_call() -> None:
    result = _parse("\\section not a group")
    (node, *_rest) = result.document.children
    assert isinstance(node, MacroCall)
    assert node.name == "\\section"


# --- macro calls (bare, no signature table in this sub-issue) --------------


def test_unknown_macro_is_a_bare_macro_call_with_no_args() -> None:
    result = _parse("\\textbf{bold}")
    macro, group = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\textbf"
    assert macro.args == ()
    assert isinstance(group, Group)


def test_text_before_a_macro_call_is_flushed_in_order() -> None:
    # Regression: a bare macro call used to skip flushing pending text,
    # corrupting node order and merging text from before and after the call.
    result = _parse("a\\foo b")
    before, macro, after = result.document.children
    assert isinstance(before, Text)
    assert before.text == "a"
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\foo"
    assert isinstance(after, Text)
    assert after.text == " b"


# --- comments and verbatim pass through as their own node kinds ------------


def test_comment_becomes_a_comment_node() -> None:
    result = _parse("a%hi\nb")
    text1, comment, text2 = result.document.children
    assert isinstance(comment, Comment)
    assert comment.text == "%hi\n"
    assert isinstance(text1, Text)
    assert isinstance(text2, Text)


def test_verb_becomes_a_verbatim_block_node() -> None:
    result = _parse("\\verb|a{b|")
    macro, verbatim = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\verb"
    assert isinstance(verbatim, VerbatimBlock)
    assert verbatim.text == "|a{b|"


# --- top-level document shape -----------------------------------------------


def test_parse_returns_a_document_with_whole_source_span() -> None:
    result = _parse("{x}")
    assert isinstance(result.document, Document)
    assert result.document.span.start == 0
    assert result.document.span.end == 3
