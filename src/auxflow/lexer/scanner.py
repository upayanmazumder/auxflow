r"""Single-pass, table-driven lexical scanner.

docs/COMPILER-PIPELINE.md section 1: classify every character by category
code; group characters into tokens. Every character outside a control
sequence is its own token -- TeX's own tokenizer does not merge ordinary
characters into words either; that happens later, during typesetting.

Comments and verbatim regions are recognised and emitted as single opaque
tokens so that later phases never see their contents as syntax
(docs/LANGUAGE-SUBSET.md "Required": `%`, `\%`, `\verb`, `verbatim`).
"""

from __future__ import annotations

from auxflow.lexer.catcode import CatCode, catcode_of
from auxflow.lexer.tokens import Token

_VERBATIM_ENV_OPEN = "{verbatim}"
_VERBATIM_ENV_CLOSE = "\\end{verbatim}"


def tokenize(source: str, file_id: str) -> list[Token]:
    r"""Scan `source` into a flat token stream.

    Control sequences: an ESCAPE character followed by either a maximal run
    of LETTER characters, or exactly one character of any other category
    (the "control symbol" shape, e.g. `\%`, `\\`). A lone escape at end of
    input is its own degenerate control-sequence token. `\%` is therefore
    never seen by the comment rule below: the escape consumes the `%` as
    part of the control sequence before it could start a comment.

    `%` (when not escaped) starts a comment that runs to the end of the
    line, including the newline, plus any leading whitespace on the next
    line; the whole span is one COMMENT token.

    `\verb<delim>...<delim>` takes its delimiter from the character
    immediately following `\verb` (no space skipping) and everything up to
    and including the matching delimiter is one VERBATIM token. An
    unterminated `\verb` conservatively consumes to end of input rather than
    silently dropping content.

    `\begin{verbatim}...\end{verbatim}`: the `\begin`/`\end` control
    sequences and the `{verbatim}` group tokenise normally (the parser needs
    them to recognise the environment); only the body between them is one
    opaque VERBATIM token. An unterminated environment consumes to end of
    input.

    Every other character is a single-character token carrying its own
    category code.
    """
    tokens: list[Token] = []
    n = len(source)
    i = 0
    line = 1
    col = 1

    def advance(count: int) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if source[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    def emit(
        catcode: CatCode, text: str, start_line: int, start_col: int, start_offset: int
    ) -> None:
        tokens.append(Token(catcode, text, file_id, start_line, start_col, start_offset))

    def emit_single_char() -> None:
        start_line, start_col, start_offset = line, col, i
        ch = source[i]
        emit(catcode_of(ch), ch, start_line, start_col, start_offset)
        advance(1)

    while i < n:
        start_line, start_col, start_offset = line, col, i
        ch = source[i]
        code = catcode_of(ch)

        if code == CatCode.ESCAPE:
            j = i + 1
            if j < n and catcode_of(source[j]) == CatCode.LETTER:
                k = j
                while k < n and catcode_of(source[k]) == CatCode.LETTER:
                    k += 1
                length = k - i
            elif j < n:
                length = 2  # escape plus exactly one other character
            else:
                length = 1  # lone escape at end of input
            text = source[i : i + length]
            emit(CatCode.CONTROL_SEQUENCE, text, start_line, start_col, start_offset)
            advance(length)

            if text == "\\verb" and i < n:
                delim = source[i]
                v_line, v_col, v_offset = line, col, i
                close = source.find(delim, i + 1)
                end = close + 1 if close != -1 else n
                emit(CatCode.VERBATIM, source[i:end], v_line, v_col, v_offset)
                advance(end - i)
            elif text == "\\begin" and source.startswith(_VERBATIM_ENV_OPEN, i):
                for _ in _VERBATIM_ENV_OPEN:
                    emit_single_char()
                v_line, v_col, v_offset = line, col, i
                close = source.find(_VERBATIM_ENV_CLOSE, i)
                end = close if close != -1 else n
                if end > i:
                    emit(CatCode.VERBATIM, source[i:end], v_line, v_col, v_offset)
                    advance(end - i)
            continue

        if code == CatCode.COMMENT:
            newline = source.find("\n", i)
            end = n if newline == -1 else newline + 1
            while end < n and catcode_of(source[end]) == CatCode.SPACE:
                end += 1
            emit(CatCode.COMMENT, source[i:end], start_line, start_col, start_offset)
            advance(end - i)
            continue

        emit_single_char()

    return tokens
