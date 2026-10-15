r"""Phase 3 acceptance (sub-issue #24): argument-signature table and
optional-argument handling.

Covers mandatory-only, optional+mandatory, nested-brace optional, and
unknown-macro cases, per the sub-issue's acceptance criteria.
"""

from __future__ import annotations

from auxflow.lexer import tokenize
from auxflow.parser import Argument, Group, MacroCall, Text, parse


def _parse(source: str):
    tokens = tokenize(source, file_id="t.tex")
    return parse(tokens, file_id="t.tex")


# --- mandatory-only ----------------------------------------------------


def test_mandatory_only_signature() -> None:
    result = _parse("\\label{fig:intro}")
    assert result.diagnostics == ()
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\label"
    assert len(macro.args) == 1
    arg = macro.args[0]
    assert isinstance(arg, Argument)
    assert arg.kind == "mandatory"
    (text,) = arg.content
    assert isinstance(text, Text)
    assert text.text == "fig:intro"


def test_two_mandatory_arguments_in_order() -> None:
    result = _parse("\\setcounter{page}{3}")
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    assert len(macro.args) == 2
    assert [a.kind for a in macro.args] == ["mandatory", "mandatory"]
    assert macro.args[0].content[0].text == "page"  # type: ignore[union-attr]
    assert macro.args[1].content[0].text == "3"  # type: ignore[union-attr]


# --- optional + mandatory -----------------------------------------------


def test_optional_then_mandatory_both_present() -> None:
    result = _parse("\\includegraphics[width=5cm]{plot.png}")
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    assert [a.kind for a in macro.args] == ["optional", "mandatory"]
    assert macro.args[0].content[0].text == "width=5cm"  # type: ignore[union-attr]
    assert macro.args[1].content[0].text == "plot.png"  # type: ignore[union-attr]


def test_optional_argument_may_be_omitted() -> None:
    result = _parse("\\includegraphics{plot.png}")
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    # the optional slot is simply absent; only the mandatory arg is recorded
    assert [a.kind for a in macro.args] == ["mandatory"]
    assert macro.args[0].content[0].text == "plot.png"  # type: ignore[union-attr]


# --- nested braces inside an optional argument ---------------------------


def test_nested_brace_inside_optional_argument() -> None:
    result = _parse("\\includegraphics[width={5cm}]{plot.png}")
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    optional_arg = macro.args[0]
    assert optional_arg.kind == "optional"
    # "width=" as Text, then a nested Group for "{5cm}"
    assert [type(n) for n in optional_arg.content] == [Text, Group]
    group = optional_arg.content[1]
    assert isinstance(group, Group)
    assert group.children[0].text == "5cm"  # type: ignore[union-attr]


def test_closing_bracket_inside_nested_braces_does_not_end_the_optional_arg() -> None:
    # A ']' inside a nested '{...}' must not be mistaken for the optional
    # argument's own closing bracket.
    result = _parse("\\includegraphics[a{]}b]{plot.png}")
    (macro,) = result.document.children
    assert isinstance(macro, MacroCall)
    optional_arg = macro.args[0]
    assert optional_arg.kind == "optional"
    assert [type(n) for n in optional_arg.content] == [Text, Group, Text]
    assert optional_arg.content[1].children[0].text == "]"  # type: ignore[union-attr]


# --- unknown macros --------------------------------------------------------


def test_macro_not_in_the_signature_table_is_a_bare_macro_call() -> None:
    result = _parse("\\emph{word}")
    macro, group = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\emph"
    assert macro.args == ()
    assert isinstance(group, Group)


# --- malformed usage degrades without crashing ------------------------------


def test_mandatory_argument_missing_stops_consuming_further_args() -> None:
    result = _parse("\\setcounter{page} not a group")
    (macro, *_rest) = result.document.children
    assert isinstance(macro, MacroCall)
    assert macro.name == "\\setcounter"
    assert len(macro.args) == 1  # second mandatory arg absent; call degrades gracefully
