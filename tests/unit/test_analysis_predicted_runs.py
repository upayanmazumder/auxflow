r"""Phase 10 (sub-issue #50): deriving P and the predicted run count."""

from __future__ import annotations

from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass, predicted_runs
from auxflow.ast import build_forest
from auxflow.ir import lower
from auxflow.ir.graph import ARG
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _predicted_runs(source: str) -> int:
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    graph = lower(forest, resolve(forest, declare(forest)))
    components = tarjan(graph)
    condensation = build_condensation(graph, components)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, condensation, labels)
    return predicted_runs(graph, stable_pass)


def test_backward_reference_example_derives_predicted_runs_2() -> None:
    assert (
        _predicted_runs("\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}.")
        == 2
    )


def test_table_of_contents_example_derives_predicted_runs_3() -> None:
    assert _predicted_runs("\\tableofcontents\\section{First}\\label{x}") == 3


def test_bibliography_cascade_example_derives_predicted_runs_4() -> None:
    assert _predicted_runs("\\tableofcontents\\cite{k}\\bibliography{refs}") == 4


def test_document_with_no_facts_derives_predicted_runs_1() -> None:
    assert predicted_runs(ARG(facts={}, edges=[]), {}) == 1
