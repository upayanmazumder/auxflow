r"""Phase 11 (sub-issue #52): the benign-cycle report, higher verbosity only.

No currently modelled construct produces a real pre-taint cycle (the
exists/value split is designed to prevent that -- see
test_analysis_classify.py), so this is exercised on a synthetic ARG,
matching the established pattern for this exact label in phases 8, 10 and 11.
"""

from __future__ import annotations

from auxflow.analysis.classify import classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.report import render
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind
from auxflow.parser.spans import Span

_SOURCE = "\\tableofcontents\n"
_SPAN = Span("main.tex", 0, len(_SOURCE))


def _benign_arg() -> ARG:
    facts = {
        0: Fact(0, FactKind.LIST_EXTENT, "toc", "value", "engine", None, _SPAN),
        1: Fact(1, FactKind.CONTENT_VOLUME, None, "value", "engine", None, _SPAN),
    }
    edges = [
        DepEdge(0, 1, 1, DepType.LAYOUT, "toc extent shifts pagination"),
        DepEdge(1, 0, 1, DepType.LAYOUT, "pagination affects toc extent"),
    ]
    return ARG(facts=facts, edges=edges)


def test_benign_report_is_suppressed_below_the_verbose_threshold() -> None:
    arg = _benign_arg()
    components = tarjan(arg)
    condensation = build_condensation(arg, components)
    labels = classify_components(arg, components)
    stable_pass = compute_stable_pass(arg, condensation, labels)
    classification = classify(arg, components, labels, stable_pass)

    assert render(arg, {"main.tex": _SOURCE}, classification, stable_pass, verbose=False) is None


def test_benign_report_names_both_facts_and_uses_required_wording() -> None:
    arg = _benign_arg()
    components = tarjan(arg)
    condensation = build_condensation(arg, components)
    labels = classify_components(arg, components)
    stable_pass = compute_stable_pass(arg, condensation, labels)
    classification = classify(arg, components, labels, stable_pass)

    report = render(arg, {"main.tex": _SOURCE}, classification, stable_pass, verbose=True)

    assert report is not None
    assert report.startswith("auxflow: note: benign feedback cycle (2 facts)")
    assert "LIST_EXTENT(toc)" in report
    assert "CONTENT_VOLUME" in report
    assert "main.tex:1:1" in report
    assert "Classified BENIGN_CYCLIC." in report
    assert "cannot converge" not in report
