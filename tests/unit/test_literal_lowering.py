r"""Literal environment bodies must not generate facts or certify unmodelled listings."""

from auxflow.ast import build_forest
from auxflow.ir.graph import lower
from auxflow.ir.model import FactKind
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _lower(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def test_verbatim_code_adds_no_reference_facts() -> None:
    graph = _lower(
        r"\begin{verbatim}\label{fake}\pageref{fake}\includegraphics{missing}"
        r"\end{verbatim}\label{real}\pageref{real}"
    )
    labels = [fact.key for fact in graph.facts.values() if fact.kind is FactKind.LABEL_NUMBER]
    refs = [fact.key for fact in graph.facts.values() if fact.kind is FactKind.PAGEREF_USE]
    assert labels == ["real"]
    assert refs == ["real"]
    assert not any(
        fact.kind is FactKind.OPAQUE and fact.key == r"\includegraphics"
        for fact in graph.facts.values()
    )


def test_listing_code_adds_no_references_but_environment_remains_opaque() -> None:
    graph = _lower(
        r"\begin{lstlisting}\label{fake}\pageref{fake}\includegraphics{missing}"
        r"\end{lstlisting}\label{real}\pageref{real}"
    )
    labels = [fact.key for fact in graph.facts.values() if fact.kind is FactKind.LABEL_NUMBER]
    refs = [fact.key for fact in graph.facts.values() if fact.kind is FactKind.PAGEREF_USE]
    assert labels == ["real"]
    assert refs == ["real"]
    assert any(
        fact.kind is FactKind.OPAQUE and fact.metadata["reason"] == "unmodelled environment"
        for fact in graph.facts.values()
    )
    assert all(fact.opaque for fact in graph.facts.values())
