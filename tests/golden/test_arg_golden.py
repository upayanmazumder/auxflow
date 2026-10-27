r"""Phase 7 acceptance golden test for ARG serialisation.

Verifies that ``to_json`` produces output that is byte-for-byte identical to
the checked-in golden snapshot (fixtures/simple_document.arg.json) and that
calling ``to_json`` twice on the same ARG object returns identical strings
(idempotence / stability).

The fixture (fixtures/simple_document.tex) exercises documentclass, usepackage,
the document environment, sectioning, ref, a nested figure environment,
includegraphics with an optional argument, caption and label -- enough node
kinds to exercise every fact kind the ARG currently models for this document.
Regenerate the golden file only deliberately (tests/README.md: golden snapshots
are "regenerated deliberately and never automatically").
"""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import build_forest
from auxflow.ir import lower, to_json
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve

_FIXTURES = Path(__file__).parent / "fixtures"


def test_arg_json_matches_the_golden_file() -> None:
    source = (_FIXTURES / "simple_document.tex").read_text()
    expected = (_FIXTURES / "simple_document.arg.json").read_text()

    tokens = tokenize(source, file_id="simple_document.tex")
    doc = parse(tokens, file_id="simple_document.tex").document
    forest = build_forest({"simple_document.tex": doc})
    tables = declare(forest)
    tables = resolve(forest, tables)
    arg = lower(forest, tables)

    assert to_json(arg) == expected.rstrip("\n")


def test_arg_json_is_stable_across_calls() -> None:
    source = (_FIXTURES / "simple_document.tex").read_text()

    tokens = tokenize(source, file_id="simple_document.tex")
    doc = parse(tokens, file_id="simple_document.tex").document
    forest = build_forest({"simple_document.tex": doc})
    tables = declare(forest)
    tables = resolve(forest, tables)
    arg = lower(forest, tables)

    first = to_json(arg)
    second = to_json(arg)
    assert first == second
