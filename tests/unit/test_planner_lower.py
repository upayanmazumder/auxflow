r"""Build-plan rules use reachability, actual facts, and the classification."""

from __future__ import annotations

from auxflow.analysis.classify import classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import build_forest
from auxflow.ir import lower
from auxflow.ir.model import Fact, FactKind
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.parser.spans import Span
from auxflow.planner.lower import build_plan
from auxflow.semantic.resolve import declare, resolve


def _plan(
    source: str,
    *,
    other_files: dict[str, str] | None = None,
    force: bool = False,
    spellcheck: bool = False,
    with_index: bool = False,
):
    files = {"main.tex": source, **(other_files or {})}
    documents = {
        file_id: parse(tokenize(text, file_id=file_id), file_id=file_id).document
        for file_id, text in files.items()
    }
    forest = build_forest(documents)
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, build_condensation(graph, components), labels)
    classification = classify(graph, components, labels, stable_pass)
    if with_index:
        next_id = max(graph.facts, default=-1) + 1
        graph.facts[next_id] = Fact(
            next_id,
            FactKind.INDEX_ENTRY,
            "term",
            "exists",
            "engine",
            None,
            Span("main.tex", 0, 1),
        )
    return build_plan(
        forest,
        "main.tex",
        graph,
        components,
        classification,
        stable_pass,
        analysis_ms=1.5,
        force=force,
        spellcheck=spellcheck,
    )


def test_bibtex_requires_both_citation_facts_and_bibliography_command() -> None:
    assert "bibtex" not in [step.tool for step in _plan(r"\cite{k}").steps]
    assert "bibtex" not in [step.tool for step in _plan(r"\bibliography{refs}").steps]

    plan = _plan(r"\cite{k}\bibliography{refs}")
    tools = [step.tool for step in plan.steps]
    assert tools.index("bibtex") == tools.index("pdflatex") + 1
    assert "1 CITE_USE facts" in plan.steps[tools.index("bibtex")].reason
    assert r"\bibliography at main.tex:" in plan.steps[tools.index("bibtex")].reason


def test_per_file_tooling_skips_unreachable_files() -> None:
    plan = _plan(
        r"\input{chapter}",
        other_files={"chapter.tex": r"\label{x}", "unused.tex": r"\cite{y}\bibliography{refs}"},
        spellcheck=True,
    )

    checked = [step.args for step in plan.steps if step.tool == "spellcheck"]
    assert checked == [["chapter.tex"], ["main.tex"]]
    assert "bibtex" not in [step.tool for step in plan.steps]


def test_index_tool_requires_index_fact_and_follows_first_engine_run() -> None:
    assert "makeindex" not in [step.tool for step in _plan(r"\label{x}").steps]
    plan = _plan(r"\label{x}", with_index=True)
    tools = [step.tool for step in plan.steps]
    assert tools.index("makeindex") == tools.index("pdflatex") + 1
    assert plan.steps[tools.index("makeindex")].reason == "INDEX_ENTRY at main.tex:0-1"


def test_certified_plan_uses_derived_runs_and_verifies_final_engine_step() -> None:
    plan = _plan(r"\tableofcontents\section{One}\label{x}")
    engines = [step for step in plan.steps if step.tool == "pdflatex"]

    assert plan.classification == "CERTIFIED"
    assert plan.predicted_runs == 3
    assert len(engines) == plan.predicted_runs
    assert [step.verify_after for step in engines] == [False, False, True]
    assert "P=2 so runs=P+1" in engines[-1].reason
    assert plan.stop_condition == "planned_count"


def test_unknown_plan_uses_conservative_floor_and_final_verification() -> None:
    plan = _plan(r"\usepackage{exotic}\label{x}")
    engines = [step for step in plan.steps if step.tool == "pdflatex"]

    assert plan.classification == "UNKNOWN"
    assert plan.predicted_runs is None
    assert len(engines) == 3
    assert [step.verify_after for step in engines] == [False, False, True]
    assert all("UNKNOWN conservative default" in step.reason for step in engines)
    assert plan.stop_condition == "aux_fixpoint"


def test_amplifying_refuses_without_force_and_force_uses_capped_floor() -> None:
    source = r"\newcounter{n}\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}\label{l}"
    refused = _plan(source)
    forced = _plan(source, force=True)

    assert refused.classification == "AMPLIFYING"
    assert refused.steps == []
    assert len(refused.diagnostics) == 1
    assert "may not converge" in refused.diagnostics[0].message
    assert refused.max_runs == 6
    assert [step.tool for step in forced.steps] == ["pdflatex"] * 3
    assert forced.steps[-1].verify_after
    assert forced.stop_condition == "cap"
