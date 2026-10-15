r"""Phase 3 acceptance (sub-issue #25): error recovery on malformed input.

Malformed input (unbalanced braces, unterminated environments) must produce
a partial AST plus diagnostics rather than a crash. The mechanism itself
(auxflow.parser.recursive._Cursor.diagnostics) was built as part of sub-issue
#23's group/environment parsing; this sub-issue is where that mechanism's
behaviour against malformed fixtures is specified and locked down by tests.
"""

from __future__ import annotations

from auxflow.lexer import tokenize
from auxflow.parser import (
    ControlConstruct,
    Diagnostic,
    Document,
    Environment,
    Group,
    MacroCall,
    MacroDef,
    Text,
    parse,
)


def _parse(source: str):
    tokens = tokenize(source, file_id="t.tex")
    return parse(tokens, file_id="t.tex")


# --- unbalanced braces ----------------------------------------------------


def test_unterminated_group_returns_a_tree_not_a_crash() -> None:
    result = _parse("a{bc")
    assert isinstance(result.document, Document)
    text, group = result.document.children
    assert isinstance(text, Text)
    assert text.text == "a"
    assert isinstance(group, Group)
    assert group.children[0].text == "bc"  # type: ignore[union-attr]


def test_unterminated_group_reports_the_opening_brace_span() -> None:
    result = _parse("x{abc")
    (diag,) = result.diagnostics
    assert isinstance(diag, Diagnostic)
    assert diag.span.start == 1
    assert diag.span.end == 2  # exactly the unmatched '{'
    assert "unterminated group" in diag.message


def test_unterminated_mandatory_argument_reports_a_diagnostic() -> None:
    result = _parse("\\label{fig:a")
    (diag,) = result.diagnostics
    assert "unterminated group" in diag.message
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.args[0].content[0].text == "fig:a"  # type: ignore[union-attr]


def test_unterminated_optional_argument_reports_a_diagnostic() -> None:
    result = _parse("\\includegraphics[width=5cm{plot.png}")
    assert len(result.diagnostics) >= 1
    assert any("unterminated optional argument" in d.message for d in result.diagnostics)


def test_deeply_nested_unterminated_groups_report_one_diagnostic_each() -> None:
    result = _parse("a{b{c{d")
    assert len(result.diagnostics) == 3
    for diag in result.diagnostics:
        assert "unterminated group" in diag.message


def test_stray_closing_brace_with_no_matching_open_does_not_crash() -> None:
    # No group was ever opened, so there is nothing to diagnose: '}' falls
    # back to being ordinary text.
    result = _parse("abc}def")
    assert result.diagnostics == ()
    (text,) = result.document.children
    assert isinstance(text, Text)
    assert text.text == "abc}def"


# --- unterminated environments ---------------------------------------------


def test_unterminated_environment_returns_a_partial_tree() -> None:
    result = _parse("\\begin{itemize}\\item one")
    (env,) = result.document.children
    assert isinstance(env, Environment)
    assert env.name == "itemize"
    item_call = env.children[0]
    assert isinstance(item_call, MacroCall)
    assert item_call.name == "\\item"


def test_unterminated_environment_reports_the_begin_span_and_names_the_environment() -> None:
    result = _parse("\\begin{figure}x")
    (diag,) = result.diagnostics
    assert diag.span.start == 0
    assert diag.span.end == len("\\begin")
    assert "figure" in diag.message
    assert "unterminated environment" in diag.message


def test_nested_environment_unterminated_only_the_outer_one_is_diagnosed() -> None:
    # The inner environment IS properly closed; only the outer is malformed
    # (it never sees its own \\end).
    result = _parse("\\begin{outer}\\begin{inner}x\\end{inner}y")
    assert len(result.diagnostics) == 1
    assert "outer" in result.diagnostics[0].message
    (outer,) = result.document.children
    assert isinstance(outer, Environment)
    assert outer.name == "outer"
    inner = outer.children[0]
    assert isinstance(inner, Environment)
    assert inner.name == "inner"


def test_mismatched_end_name_does_not_falsely_close_and_is_still_diagnosed() -> None:
    # '\\end{outer}' appearing while 'inner' is open does not close
    # 'inner'; it is swallowed as ordinary content, so 'inner' itself ends
    # up unterminated (and, transitively, so does 'outer', since its
    # closer was consumed by 'inner').
    result = _parse("\\begin{outer}\\begin{inner}x\\end{outer}")
    assert len(result.diagnostics) == 2
    names = {d.message.split("\\begin{")[1].split("}")[0] for d in result.diagnostics}
    assert names == {"outer", "inner"}


def test_begin_with_no_name_group_degrades_to_a_bare_macro_call_without_crashing() -> None:
    result = _parse("\\begin not a name")
    (node, *_rest) = result.document.children
    assert isinstance(node, MacroCall)
    assert node.name == "\\begin"
    assert result.diagnostics == ()


# --- combined malformed input ------------------------------------------------


def test_multiple_independent_errors_are_all_reported() -> None:
    source = "\\begin{a}x{y\\begin{b}z"
    result = _parse(source)
    assert len(result.diagnostics) == 3  # unterminated 'a', unterminated '{', unterminated 'b'
    assert all(isinstance(d, Diagnostic) for d in result.diagnostics)
    # every diagnostic span lies within the source
    for d in result.diagnostics:
        assert 0 <= d.span.start < d.span.end <= len(source)


def test_missing_loop_body_reports_diagnostic_and_keeps_condition() -> None:
    source = r"\forloop{n}{0}{\pageref{x}}text"
    result = _parse(source)
    loop, trailing = result.document.children
    assert isinstance(loop, ControlConstruct)
    assert loop.condition[0].name == r"\pageref"  # type: ignore[union-attr]
    assert loop.body == ()
    assert loop.span.end == source.index("text")
    assert isinstance(trailing, Text) and trailing.text == "text"
    assert len(result.diagnostics) == 1
    assert "body" in result.diagnostics[0].message


def test_unterminated_macro_body_reports_nested_unmatched_braces_and_keeps_tokens() -> None:
    source = r"\newcommand{\foo}[2]{a{b"
    result = _parse(source)
    (definition,) = result.document.children
    assert isinstance(definition, MacroDef)
    assert definition.name == r"\foo"
    assert definition.arity == 2
    assert "".join(token.text for token in definition.body_tokens) == "a{b"
    assert definition.span.end == len(source)
    assert len(result.diagnostics) == 2
    assert {d.span.start for d in result.diagnostics} == {
        source.index("{a"),
        source.index("{b"),
    }


def test_missing_macro_body_reports_diagnostic_without_consuming_following_text() -> None:
    source = r"\renewcommand{\foo}[1]plain"
    result = _parse(source)
    definition, trailing = result.document.children
    assert isinstance(definition, MacroDef)
    assert definition.body_tokens == ()
    assert definition.span.end == source.index("plain")
    assert isinstance(trailing, Text) and trailing.text == "plain"
    assert any("body" in d.message for d in result.diagnostics)
