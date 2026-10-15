r"""Phase 10 (sub-issue #48): singleton-component stable-pass recurrence.

Both worked examples here involve only singleton (acyclic) components --
no feedback at all before taint runs -- so they exercise exactly the
`else` branch of docs/STATIC-ANALYSIS.md section 4's recurrence.
"""

from __future__ import annotations

from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.ast import build_forest
from auxflow.ir import FactKind, lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _pipeline(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    graph = lower(forest, resolve(forest, declare(forest)))
    components = tarjan(graph)
    condensation = build_condensation(graph, components)
    labels = classify_components(graph, components)
    return graph, compute_stable_pass(graph, condensation, labels)


def test_backward_reference_example_yields_label_number_1_and_ref_use_2() -> None:
    graph, result = _pipeline(
        "\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}."
    )

    label_number = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_NUMBER)
    ref_use = next(f for f in graph.facts.values() if f.kind is FactKind.REF_USE)
    assert result[label_number.fact_id] == 1
    assert result[ref_use.fact_id] == 2


def test_table_of_contents_example_yields_content_volume_2_and_label_page_2() -> None:
    graph, result = _pipeline("\\tableofcontents\\section{First}\\label{x}")

    volume = next(f for f in graph.facts.values() if f.kind is FactKind.CONTENT_VOLUME)
    label_page = next(f for f in graph.facts.values() if f.kind is FactKind.LABEL_PAGE)
    assert result[volume.fact_id] == 2
    assert result[label_page.fact_id] == 2
