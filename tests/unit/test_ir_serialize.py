r"""Phase 7 serialisation: JSON round-trip and parseable, colour-coded DOT."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pydot
import pytest

from auxflow.ast import build_forest
from auxflow.ir import DepType, FactKind, from_json, lower, to_dot, to_json
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _lower(source: str):
    document = parse(tokenize(source, file_id="main.tex"), file_id="main.tex").document
    forest = build_forest({"main.tex": document})
    return lower(forest, resolve(forest, declare(forest)))


def _edges(arg) -> list[tuple[int, int, int, str, str]]:
    return sorted(
        (e.source, e.destination, e.pass_lag, e.dependency_type.name, e.reason) for e in arg.edges
    )


def _graph_nodes(parsed_nodes) -> dict[str, object]:
    return {node.get_name(): node for node in parsed_nodes if node.get_name().startswith("f")}


def test_json_round_trip_preserves_an_identical_arg() -> None:
    graph = _lower(
        "\\tableofcontents\\section{One}\\label{a}\\pageref{a}"
        "\\cite{k}\\bibliography{refs}\\forloop{n}{0}{\\value{n}<\\pageref{a}}{~\\newpage}"
    )

    text = to_json(graph)
    restored = from_json(text)

    assert to_json(restored) == text
    assert restored.facts == graph.facts
    assert _edges(restored) == _edges(graph)
    assert len(restored.edges) == len(graph.edges)


def test_dot_output_parses_and_separates_components_and_edge_types() -> None:
    graph = _lower("\\tableofcontents\\section{One}\\label{a}\\pageref{a}")
    dot = to_dot(graph)

    parsed = pydot.graph_from_dot_data(dot)
    assert parsed is not None and len(parsed) == 1
    nodes = _graph_nodes(parsed[0].get_nodes())
    assert sorted(nodes) == sorted(f"f{fact_id}" for fact_id in graph.facts)
    assert len(parsed[0].get_edges()) == len(graph.edges)

    exists = next(f for f in graph.facts.values() if f.kind is FactKind.TOC_ENTRY)
    value = next(
        f for f in graph.facts.values() if f.kind is FactKind.TOC_ENTRY and f.component == "value"
    )
    assert nodes[f"f{exists.fact_id}"].get_fillcolor() != nodes[f"f{value.fact_id}"].get_fillcolor()

    colours = {edge.get_label().strip('"'): edge.get_color() for edge in parsed[0].get_edges()}
    assert colours["LAYOUT lag 0"] != colours["AUX_ROUNDTRIP lag 1"]
    assert DepType.LAYOUT.name in dot and DepType.AUX_ROUNDTRIP.name in dot


def test_dot_is_deterministic_and_escapes_keys() -> None:
    graph = _lower("\\label{a:b}\\ref{a:b}")
    dot = to_dot(graph)
    assert dot == to_dot(graph)
    parsed = pydot.graph_from_dot_data(dot)
    nodes = _graph_nodes(parsed[0].get_nodes()).values()
    labels = " ".join(str(node.get_label()) for node in nodes)
    assert "a:b" in labels


def test_dot_renders_with_graphviz_when_installed() -> None:
    if shutil.which("dot") is None:
        pytest.skip("graphviz 'dot' binary is not installed")
    graph = _lower("\\label{a}\\pageref{a}")
    completed = subprocess.run(
        ["dot", "-Tsvg"],
        input=to_dot(graph),
        capture_output=True,
        text=True,
        check=True,
    )
    assert "<svg" in completed.stdout


def test_graph_cli_writes_dot_to_file_and_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from auxflow import cli

    doc = tmp_path / "doc.tex"
    doc.write_text("\\label{a}\\ref{a}")
    target = tmp_path / "arg.dot"

    assert cli.main(["graph", str(doc), "-o", str(target)]) == 0
    written = target.read_text(encoding="utf-8")
    assert written.startswith("digraph arg {")
    assert capsys.readouterr().out == ""

    assert cli.main(["graph", str(doc)]) == 0
    assert capsys.readouterr().out == written
