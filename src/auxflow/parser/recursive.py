r"""Hand-written recursive-descent parser, one token of lookahead.

docs/COMPILER-PIPELINE.md section 2: recover document structure (preamble,
environments, macro calls, groups, sectioning) from a token stream.

Argument-signature-driven parsing: a control sequence listed in
auxflow.parser.signatures.SIGNATURES consumes exactly the mandatory/optional
groups its signature specifies (docs/COMPILER-PIPELINE.md section 2:
`\label{}` one mandatory, `\includegraphics[]{}` one optional and one
mandatory); an unlisted control sequence becomes a bare `MacroCall` with no
arguments.

Malformed input (an unterminated group, environment, or optional argument)
never raises: the cursor accumulates a `Diagnostic` and the enclosing node
closes at end of input, so callers always get a tree back.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from auxflow.lexer.catcode import CatCode
from auxflow.lexer.tokens import Token
from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.nodes import (
    Argument,
    Comment,
    Document,
    Environment,
    Group,
    MacroCall,
    Node,
    Preamble,
    Sectioning,
    Text,
    VerbatimBlock,
)
from auxflow.parser.signatures import SIGNATURES
from auxflow.parser.spans import Span

_SECTIONING_LEVELS: dict[str, str] = {
    "\\chapter": "chapter",
    "\\section": "section",
    "\\subsection": "subsection",
}


@dataclass(frozen=True)
class ParseResult:
    document: Document
    diagnostics: tuple[Diagnostic, ...]


class _Cursor:
    __slots__ = ("diagnostics", "file_id", "i", "tokens")

    def __init__(self, tokens: list[Token], file_id: str) -> None:
        self.tokens = tokens
        self.i = 0
        self.file_id = file_id
        self.diagnostics: list[Diagnostic] = []

    def peek(self) -> Token | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def advance(self) -> Token:
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def end_offset(self) -> int:
        """Offset just past the last consumed token, for a span that reaches EOF."""
        if self.i == 0:
            return 0
        prev = self.tokens[self.i - 1]
        return prev.offset + len(prev.text)


def parse(tokens: list[Token], file_id: str) -> ParseResult:
    cursor = _Cursor(tokens, file_id)
    children = _parse_nodes(cursor, stop=lambda c: False)
    start = tokens[0].offset if tokens else 0
    span = Span(file_id, start, cursor.end_offset())

    preamble: list[Node] = []
    rest: list[Node] = []
    seen_document = False
    for node in children:
        if seen_document:
            rest.append(node)
        elif isinstance(node, Environment) and node.name == "document":
            seen_document = True
            rest.append(node)
        else:
            preamble.append(node)

    if seen_document:
        preamble_start = preamble[0].span.start if preamble else span.start
        preamble_end = preamble[-1].span.end if preamble else preamble_start
        top_children: tuple[Node, ...] = (
            Preamble(Span(file_id, preamble_start, preamble_end), tuple(preamble)),
            *rest,
        )
    else:
        top_children = tuple(children)

    return ParseResult(Document(span, top_children), tuple(cursor.diagnostics))


def _parse_nodes(cursor: _Cursor, stop: Callable[[_Cursor], bool]) -> list[Node]:
    nodes: list[Node] = []
    text_run: list[Token] = []

    def flush_text() -> None:
        if not text_run:
            return
        span = Span(
            cursor.file_id,
            text_run[0].offset,
            text_run[-1].offset + len(text_run[-1].text),
        )
        nodes.append(Text(span, "".join(t.text for t in text_run)))
        text_run.clear()

    while True:
        tok = cursor.peek()
        if tok is None or stop(cursor):
            break

        if tok.catcode == CatCode.CONTROL_SEQUENCE:
            if tok.text == "\\begin":
                flush_text()
                nodes.append(_parse_environment(cursor))
                continue
            if tok.text in _SECTIONING_LEVELS:
                flush_text()
                nodes.append(_parse_sectioning(cursor))
                continue
            flush_text()
            nodes.append(_parse_macro_call(cursor))
            continue

        if tok.catcode == CatCode.BEGIN_GROUP:
            flush_text()
            nodes.append(_parse_group(cursor))
            continue

        if tok.catcode == CatCode.COMMENT:
            flush_text()
            c = cursor.advance()
            nodes.append(Comment(Span(cursor.file_id, c.offset, c.offset + len(c.text)), c.text))
            continue

        if tok.catcode == CatCode.VERBATIM:
            flush_text()
            v = cursor.advance()
            nodes.append(
                VerbatimBlock(Span(cursor.file_id, v.offset, v.offset + len(v.text)), v.text)
            )
            continue

        text_run.append(cursor.advance())

    flush_text()
    return nodes


def _at_end_group(cursor: _Cursor) -> bool:
    tok = cursor.peek()
    return tok is not None and tok.catcode == CatCode.END_GROUP


def _parse_group(cursor: _Cursor) -> Group:
    open_tok = cursor.advance()  # '{'
    children = _parse_nodes(cursor, _at_end_group)
    close_tok = cursor.peek()
    if close_tok is not None and close_tok.catcode == CatCode.END_GROUP:
        cursor.advance()
        end = close_tok.offset + 1
    else:
        end = cursor.end_offset()
        cursor.diagnostics.append(
            Diagnostic(
                Span(cursor.file_id, open_tok.offset, open_tok.offset + 1),
                "unterminated group: '{' has no matching '}'",
            )
        )
    return Group(Span(cursor.file_id, open_tok.offset, end), tuple(children))


def _read_braced_name(cursor: _Cursor) -> str | None:
    """Read a `{identifier}` immediately at the cursor, e.g. an environment
    name. Returns None (and leaves the cursor where it was) if the next
    token is not '{'."""
    tok = cursor.peek()
    if tok is None or tok.catcode != CatCode.BEGIN_GROUP:
        return None
    group = _parse_group(cursor)
    return "".join(_text_of(n) for n in group.children)


def _text_of(node: Node) -> str:
    return node.text if isinstance(node, Text) else ""


def _parse_environment(cursor: _Cursor) -> Environment | MacroCall:
    begin_tok = cursor.advance()  # '\begin'
    name = _read_braced_name(cursor)
    if name is None:
        # '\begin' not followed by a name: not a real environment, degrade
        # to a bare macro call rather than guessing.
        span = Span(cursor.file_id, begin_tok.offset, begin_tok.offset + len(begin_tok.text))
        return MacroCall(span, begin_tok.text, ())

    def at_matching_end(c: _Cursor) -> bool:
        tok = c.peek()
        if tok is None or tok.catcode != CatCode.CONTROL_SEQUENCE or tok.text != "\\end":
            return False
        saved = c.i
        c.advance()
        end_name = _read_braced_name(c)
        c.i = saved
        return end_name == name

    children = _parse_nodes(cursor, at_matching_end)

    if at_matching_end(cursor):
        cursor.advance()  # '\end'
        _read_braced_name(cursor)
        end = cursor.end_offset()
    else:
        end = cursor.end_offset()
        cursor.diagnostics.append(
            Diagnostic(
                Span(cursor.file_id, begin_tok.offset, begin_tok.offset + len(begin_tok.text)),
                f"unterminated environment: \\begin{{{name}}} has no matching \\end{{{name}}}",
            )
        )

    return Environment(Span(cursor.file_id, begin_tok.offset, end), name, tuple(children))


def _parse_sectioning(cursor: _Cursor) -> Sectioning | MacroCall:
    cs_tok = cursor.advance()
    level = _SECTIONING_LEVELS[cs_tok.text]
    tok = cursor.peek()
    if tok is None or tok.catcode != CatCode.BEGIN_GROUP:
        # no title argument present: degrade to a bare macro call.
        span = Span(cursor.file_id, cs_tok.offset, cs_tok.offset + len(cs_tok.text))
        return MacroCall(span, cs_tok.text, ())
    title_group = _parse_group(cursor)
    span = Span(cursor.file_id, cs_tok.offset, title_group.span.end)
    return Sectioning(span, level, title_group.children)  # type: ignore[arg-type]


def _at_close_bracket(cursor: _Cursor) -> bool:
    tok = cursor.peek()
    return tok is not None and tok.catcode == CatCode.OTHER and tok.text == "]"


def _parse_optional_arg(cursor: _Cursor) -> Argument | None:
    """Read a `[...]` optional argument. Braces nested inside are handled by
    the ordinary `_parse_group` recursion in `_parse_nodes`, so a `]`
    inside a nested `{...}` is never mistaken for the closing bracket."""
    tok = cursor.peek()
    if tok is None or tok.catcode != CatCode.OTHER or tok.text != "[":
        return None
    open_tok = cursor.advance()  # '['
    children = _parse_nodes(cursor, _at_close_bracket)
    close_tok = cursor.peek()
    if close_tok is not None and close_tok.catcode == CatCode.OTHER and close_tok.text == "]":
        cursor.advance()
    else:
        cursor.diagnostics.append(
            Diagnostic(
                Span(cursor.file_id, open_tok.offset, open_tok.offset + 1),
                "unterminated optional argument: '[' has no matching ']'",
            )
        )
    return Argument("optional", tuple(children))


def _parse_mandatory_arg(cursor: _Cursor) -> Argument | None:
    tok = cursor.peek()
    if tok is None or tok.catcode != CatCode.BEGIN_GROUP:
        return None
    group = _parse_group(cursor)
    return Argument("mandatory", group.children)


def _parse_macro_call(cursor: _Cursor) -> MacroCall:
    cs_tok = cursor.advance()
    signature = SIGNATURES.get(cs_tok.text)
    args: list[Argument] = []
    end = cs_tok.offset + len(cs_tok.text)

    if signature is not None:
        for kind in signature.args:
            if kind == "optional":
                arg = _parse_optional_arg(cursor)
                if arg is None:
                    continue  # genuinely absent; optional arguments may be omitted
            else:
                arg = _parse_mandatory_arg(cursor)
                if arg is None:
                    break  # malformed usage: stop consuming, keep what parsed so far
            args.append(arg)
            end = cursor.end_offset()

    return MacroCall(Span(cursor.file_id, cs_tok.offset, end), cs_tok.text, tuple(args))
