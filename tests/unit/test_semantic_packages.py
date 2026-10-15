r"""Phase 6 package warning follows PackageTable model status."""

from __future__ import annotations

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.diagnostics import check_packages
from auxflow.semantic.resolve import declare


def _warnings(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return check_packages(forest, declare(forest))


def test_unmodelled_package_warns_at_usepackage_span() -> None:
    source = "\\usepackage{exotic}"

    warnings = _warnings(source)

    assert len(warnings) == 1
    assert warnings[0].message == "unmodelled package: 'exotic'"
    assert warnings[0].severity == "warning"
    assert warnings[0].span.file_id == "main.tex"
    assert (warnings[0].span.start, warnings[0].span.end) == (0, len(source))


def test_modelled_package_does_not_warn() -> None:
    assert _warnings("\\usepackage{graphicx}") == []
