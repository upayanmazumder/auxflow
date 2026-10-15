r"""Phase 4 acceptance (sub-issue #28): multi-file forest and inclusion
graph with cycle detection.

Covers: a two-file include chain links correctly; a self-including fixture
is flagged as a cycle; a mutually-including fixture is flagged as a cycle,
in both cases naming the participating file ids.
"""

from __future__ import annotations

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse


def _doc(source: str, file_id: str):
    tokens = tokenize(source, file_id=file_id)
    return parse(tokens, file_id=file_id).document


# --- a two-file include chain -----------------------------------------------


def test_two_file_input_chain_links_correctly() -> None:
    documents = {
        "main.tex": _doc("\\input{chapter1.tex}", "main.tex"),
        "chapter1.tex": _doc("hello", "chapter1.tex"),
    }
    forest = build_forest(documents)
    assert len(forest.edges) == 1
    edge = forest.edges[0]
    assert edge.source == "main.tex"
    assert edge.target == "chapter1.tex"
    assert edge.kind == "input"
    assert forest.cycles == ()
    assert forest.includer_of("chapter1.tex") == "main.tex"
    assert forest.includer_of("main.tex") is None  # a root: never included
    assert forest.reachable_from("main.tex") == frozenset({"main.tex", "chapter1.tex"})


def test_include_kind_is_distinguished_from_input() -> None:
    documents = {
        "main.tex": _doc("\\include{ch1.tex}", "main.tex"),
        "ch1.tex": _doc("x", "ch1.tex"),
    }
    forest = build_forest(documents)
    assert forest.edges[0].kind == "include"


def test_three_file_chain_is_fully_reachable_and_acyclic() -> None:
    documents = {
        "main.tex": _doc("\\input{a.tex}", "main.tex"),
        "a.tex": _doc("\\input{b.tex}", "a.tex"),
        "b.tex": _doc("leaf", "b.tex"),
    }
    forest = build_forest(documents)
    assert len(forest.edges) == 2
    assert forest.cycles == ()
    assert forest.reachable_from("main.tex") == frozenset({"main.tex", "a.tex", "b.tex"})
    assert forest.includer_of("b.tex") == "a.tex"


# --- self-including ----------------------------------------------------


def test_self_including_file_is_flagged_as_a_cycle() -> None:
    documents = {"main.tex": _doc("\\input{main.tex}", "main.tex")}
    forest = build_forest(documents)
    assert len(forest.cycles) == 1
    assert forest.cycles[0] == ("main.tex",)


# --- mutually-including -------------------------------------------------


def test_mutually_including_files_are_flagged_as_a_cycle() -> None:
    documents = {
        "a.tex": _doc("\\input{b.tex}", "a.tex"),
        "b.tex": _doc("\\input{a.tex}", "b.tex"),
    }
    forest = build_forest(documents)
    assert len(forest.cycles) == 1
    cycle = forest.cycles[0]
    assert set(cycle) == {"a.tex", "b.tex"}


def test_cycle_through_a_third_file_names_every_participant() -> None:
    documents = {
        "a.tex": _doc("\\input{b.tex}", "a.tex"),
        "b.tex": _doc("\\input{c.tex}", "b.tex"),
        "c.tex": _doc("\\input{a.tex}", "c.tex"),
    }
    forest = build_forest(documents)
    assert len(forest.cycles) == 1
    assert set(forest.cycles[0]) == {"a.tex", "b.tex", "c.tex"}


# --- no false positives -------------------------------------------------


def test_no_cycle_reported_when_there_are_no_includes() -> None:
    documents = {"main.tex": _doc("no includes here", "main.tex")}
    forest = build_forest(documents)
    assert forest.edges == ()
    assert forest.cycles == ()


def test_unknown_macro_named_similarly_is_not_mistaken_for_an_include() -> None:
    documents = {"main.tex": _doc("\\inputfoo{not-an-include}", "main.tex")}
    forest = build_forest(documents)
    assert forest.edges == ()
