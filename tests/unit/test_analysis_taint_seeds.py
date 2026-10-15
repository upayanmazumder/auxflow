r"""Phase 9 (sub-issue #45): taint seed computation."""

from __future__ import annotations

from auxflow.analysis.taint import seed_facts
from auxflow.ast import build_forest
from auxflow.ir import FactKind, lower
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _lower(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def test_pageref_bounding_a_forloop_is_seeded() -> None:
    r"""docs/IR.md "Amplifying cycle": \pageref{l} bounds the \forloop."""
    graph = _lower(
        "\\newcounter{n}\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}"
        "Last page label here\\label{l}."
    )

    seeds = seed_facts(graph)

    pageref = next(f for f in graph.facts.values() if f.kind is FactKind.PAGEREF_USE)
    counter_read = next(f for f in graph.facts.values() if f.kind is FactKind.COUNTER_READ)
    assert seeds == {pageref.fact_id, counter_read.fact_id}


def test_backward_reference_only_document_seeds_nothing() -> None:
    r"""docs/IR.md "Backward reference, no generated lists": no
    ControlConstruct at all, so the seed set is empty."""
    graph = _lower("\\chapter{One}\\label{c:one}\\chapter{Two} Refer to Chapter~\\ref{c:one}.")

    assert seed_facts(graph) == set()


def test_reference_rendered_only_in_a_loop_body_is_not_seeded() -> None:
    r"""A value merely printed in a loop body (not its condition/bound) does
    not control how many iterations occur, so it is not seeded."""
    graph = _lower("\\newcounter{n}\\label{l}\\whiledo{\\value{n}<3}{Page \\ref{l}~\\newpage}")

    seeds = seed_facts(graph)
    body_ref = next(f for f in graph.facts.values() if f.kind is FactKind.REF_USE)
    condition_counter_read = next(
        f
        for f in graph.facts.values()
        if f.kind is FactKind.COUNTER_READ and f.metadata.get("control_role") == "condition"
    )
    assert body_ref.fact_id not in seeds
    assert condition_counter_read.fact_id in seeds
