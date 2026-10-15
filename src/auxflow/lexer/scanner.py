r"""Single-pass, table-driven lexical scanner.

docs/COMPILER-PIPELINE.md section 1: classify every character by category
code; group characters into tokens. Every character outside a control
sequence is its own token -- TeX's own tokenizer does not merge ordinary
characters into words either; that happens later, during typesetting.

Comment and verbatim recognition is layered on top of this scan in a later
phase 2 sub-issue (docs/LANGUAGE-SUBSET.md "Required": `%`, `\%`, `\verb`,
`verbatim`); this module alone classifies every catcode and both
control-sequence shapes.
"""

from __future__ import annotations

from auxflow.lexer.catcode import CatCode, catcode_of
from auxflow.lexer.tokens import Token


def tokenize(source: str, file_id: str) -> list[Token]:
    """Scan `source` into a flat token stream.

    Control sequences: an ESCAPE character followed by either a maximal run
    of LETTER characters, or exactly one character of any other category
    (the "control symbol" shape, e.g. `\\%`, `\\\\`). A lone escape at end of
    input is its own degenerate control-sequence token.

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
            tokens.append(
                Token(CatCode.CONTROL_SEQUENCE, text, file_id, start_line, start_col, start_offset)
            )
            advance(length)
            continue

        tokens.append(Token(code, ch, file_id, start_line, start_col, start_offset))
        advance(1)

    return tokens
