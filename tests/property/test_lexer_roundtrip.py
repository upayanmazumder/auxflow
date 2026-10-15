"""Phase 2 acceptance (sub-issue #22): the lexer round-trip property.

Concatenating token `text` in order must reproduce the original source bytes
exactly, for arbitrary inputs. Every character is covered by exactly one
token with no gaps and no overlaps, by construction of the scanner: this
property test is what proves that construction over randomly generated
input rather than only over the hand-picked unit-test cases.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from auxflow.lexer import tokenize

# The scanner's alphabet of interest: TeX-special characters plus ordinary
# letters, digits and whitespace. Restricting to Latin-1 keeps catcode_of's
# non-Latin-1 OTHER fallback exercised separately (test_lexer_scanner.py)
# rather than drowning out the structural cases here.
_ALPHABET = st.sampled_from("\\{}$&\n#^_ \tabcXYZ123.%~|+\x00")

_SOURCES = st.text(alphabet=_ALPHABET, max_size=200)


@given(source=_SOURCES)
def test_token_text_concatenation_reproduces_the_source(source: str) -> None:
    tokens = tokenize(source, file_id="t.tex")
    assert "".join(token.text for token in tokens) == source


@given(source=_SOURCES)
def test_tokens_cover_the_source_with_no_gaps_or_overlaps(source: str) -> None:
    tokens = tokenize(source, file_id="t.tex")
    expected_offset = 0
    for token in tokens:
        assert token.offset == expected_offset
        expected_offset += len(token.text)
    assert expected_offset == len(source)
