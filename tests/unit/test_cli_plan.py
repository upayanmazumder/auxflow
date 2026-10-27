r"""Plan CLI emits JSON or explained steps and refuses amplifying input."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from auxflow import cli

_CERTIFIED = r"\cite{k}\bibliography{refs}\tableofcontents\section{One}\label{x}"
_AMPLIFYING = r"\newcounter{n}\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}\label{l}"


def test_certified_plan_json_has_bibliography_after_first_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(_CERTIFIED)

    assert cli.main(["plan", str(doc)]) == 0

    plan = json.loads(capsys.readouterr().out)
    tools = [step["tool"] for step in plan["steps"]]
    assert plan["classification"] == "CERTIFIED"
    assert plan["predicted_runs"] == 4
    assert tools == ["pdflatex", "bibtex", "pdflatex", "pdflatex", "pdflatex"]
    assert [step["verify_after"] for step in plan["steps"]] == [False, False, False, False, True]
    assert plan["arg_stats"]["V"] > 0
    assert plan["arg_stats"]["analysis_ms"] >= 0


def test_explain_numbers_each_pass_and_names_the_bibliography_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(_CERTIFIED)

    assert cli.main(["plan", "--explain", str(doc)]) == 0

    output = capsys.readouterr().out
    assert output.startswith("auxflow: CERTIFIED plan")
    assert "1. pdflatex pass 1 of 4" in output
    assert "2. bibtex" in output
    assert "5. pdflatex pass 4 of 4" in output
    assert "P=3" not in output


def test_unknown_plan_uses_conservative_engine_schedule(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(r"\usepackage{exotic}\label{x}")

    assert cli.main(["plan", str(doc)]) == 0

    plan = json.loads(capsys.readouterr().out)
    assert plan["classification"] == "UNKNOWN"
    assert [step["tool"] for step in plan["steps"]] == ["pdflatex"] * 3
    assert plan["steps"][-1]["verify_after"] is True
    assert plan["stop_condition"] == "aux_fixpoint"


def test_amplifying_plan_refuses_with_diagnosis_unless_forced(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "main.tex"
    doc.write_text(_AMPLIFYING)

    assert cli.main(["plan", str(doc)]) == 1
    refusal = capsys.readouterr().out
    assert "AMPLIFYING CYCLE" in refusal
    assert "may not converge" in refusal
    assert "No build plan emitted" in refusal

    assert cli.main(["plan", "--force", str(doc)]) == 0
    forced = json.loads(capsys.readouterr().out)
    assert forced["classification"] == "AMPLIFYING"
    assert [step["tool"] for step in forced["steps"]] == ["pdflatex"] * 3
    assert forced["max_runs"] == 6
    assert forced["diagnostics"][0]["message"].startswith("AMPLIFYING CYCLE")
