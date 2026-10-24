r"""Inert packages and commands keep a document certifiable; anything else stays opaque."""

from __future__ import annotations

from auxflow.analysis.classify import State, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _state(source: str):
    document = parse(tokenize(source, file_id="doc.tex"), file_id="doc.tex").document
    forest = build_forest({"doc.tex": document})
    graph = lower(forest, resolve(forest, declare(forest)))
    taint, _ = propagate_taint(graph, seed_facts(graph))
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, build_condensation(graph, components), labels)
    return classify(graph, components, labels, stable_pass)


def test_layout_packages_and_typesetting_commands_do_not_block_certification() -> None:
    source = (
        r"\usepackage[margin=1in]{geometry}\usepackage{setspace}\usepackage{xcolor}"
        r"\begin{enumerate}\item \textbf{bold} \textcolor{red}{text}\end{enumerate}"
    )

    assert _state(source).state is State.CERTIFIED


def test_unlisted_package_still_makes_document_unknown() -> None:
    assert _state(r"\usepackage{tikz}\label{a}\ref{a}").state is State.UNKNOWN


def test_unlisted_command_still_makes_document_unknown() -> None:
    assert _state(r"\csname relax\endcsname").state is State.UNKNOWN


def test_local_macro_with_inert_body_is_certifiable() -> None:
    source = r"\newcommand{\red}[1]{\textcolor{red}{#1}}\red{word}"

    assert _state(source).state is State.CERTIFIED


def test_local_macro_hiding_an_unlisted_command_stays_unknown() -> None:
    source = r"\newcommand{\hide}[1]{\mystery{#1}}\hide{word}"

    assert _state(source).state is State.UNKNOWN


def test_eqref_is_resolved_like_a_number_reference() -> None:
    result = _state(r"\label{eq:a}See \eqref{eq:a}.")

    assert result.state is State.CERTIFIED
    assert result.predicted_runs == 2
