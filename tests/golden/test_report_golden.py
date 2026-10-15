r"""Phase 11 (sub-issue #52): the four NON-CONVERGENCE.md diagnostic reports,
byte-for-byte golden tests.

These golden files are generated from this project's own fixtures running
through the real pipeline, not a literal transcription of
docs/NON-CONVERGENCE.md's illustrative prose (whose example facts and spans
are not drawn from any real corpus document). They match the documented
*template structure* exactly -- header line, blank-line sections, indented
cycle/chain listing with arrows, likely-cause paragraph, required wording
("may not converge", never "cannot converge") -- and are locked down the
same way as every other golden fixture in this project (tests/README.md:
regenerated deliberately, never automatically).
"""

from __future__ import annotations

from pathlib import Path

from auxflow.analysis.classify import classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.report import render
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve

_FIXTURES = Path(__file__).parent / "fixtures"


def _pipeline(file_id: str):
    source = (_FIXTURES / file_id).read_text()
    document = parse(tokenize(source, file_id=file_id), file_id=file_id).document
    forest = build_forest({file_id: document})
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    condensation = build_condensation(graph, components)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, condensation, labels)
    classification = classify(graph, components, labels, stable_pass)
    report = render(graph, {file_id: source}, classification, stable_pass)
    assert report is not None
    return report


def test_amplifying_report_matches_the_golden_file() -> None:
    report = _pipeline("non_convergence_amplifying.tex")
    expected = (_FIXTURES / "non_convergence_amplifying.txt").read_text()
    assert report == expected
    assert "AMPLIFYING" in report
    assert "may not converge" in report
    assert "cannot converge" not in report
    assert "will not terminate" not in report


def test_certified_report_matches_the_golden_file() -> None:
    report = _pipeline("non_convergence_certified.tex")
    expected = (_FIXTURES / "non_convergence_certified.txt").read_text()
    assert report == expected
    assert "CERTIFIED" in report


def test_unknown_report_matches_the_golden_file() -> None:
    report = _pipeline("non_convergence_unknown.tex")
    expected = (_FIXTURES / "non_convergence_unknown.txt").read_text()
    assert report == expected
    assert "UNKNOWN" in report
