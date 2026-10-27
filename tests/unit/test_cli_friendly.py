r"""Human-facing CLI behavior: locations, hints, suggestions, progress, JSON, doctor."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from auxflow import cli
from auxflow.planner.model import BuildPlan, Step
from auxflow.runtime.execute import execute

_AMPLIFYING = (
    "\\newcounter{n}\n\\forloop{n}{0}{\\value{n} < \\pageref{l}}{~\\newpage}\nHere\\label{l}.\n"
)
_ENGINE = r"""#!/usr/bin/env python3
from pathlib import Path
import sys

jobname = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("-jobname="))
Path(f"{jobname}.aux").write_text("\\newlabel{x}{{1}{1}}\n")
print("engine output")
"""


def _doc(tmp_path: Path, text: str, name: str = "main.tex") -> Path:
    path = tmp_path / name
    path.write_text(text)
    return path


def _engine_on_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("pdflatex", "bibtex", "makeindex"):
        tool = bin_dir / name
        tool.write_text(_ENGINE)
        tool.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])


def _no_tex_on_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))


@pytest.fixture(autouse=True)
def _no_update_notices(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUXFLOW_NO_UPDATE_CHECK", "1")


# --- locations ---------------------------------------------------------------------------


def test_check_reports_line_and_column_not_character_offsets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, "first line\n  \\ref{absent}\n")

    assert cli.main(["check", str(doc)]) == 1

    assert f"{doc}:2:3: error: undefined reference: 'absent'" in capsys.readouterr().out


def test_paths_under_the_working_directory_print_relative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _doc(tmp_path, _AMPLIFYING, "doc.tex")
    monkeypatch.chdir(tmp_path)

    assert cli.main(["classify", "doc.tex"]) == 1

    out = capsys.readouterr().out
    assert str(tmp_path) not in out
    assert re.search(r"doc\.tex:\d+:\d+", out)
    assert not re.search(r"\.tex:\d+-\d+", out)


def test_amplifying_report_uses_plain_words_until_verbose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["classify", str(doc)]) == 1
    plain = capsys.readouterr().out
    assert cli.main(["classify", "-v", str(doc)]) == 1
    verbose = capsys.readouterr().out

    assert "PAGEREF_USE" not in plain
    assert "CONTENT_VOLUME" not in plain
    assert "page reference" in plain
    assert "PAGEREF_USE" in verbose


# --- check summary -----------------------------------------------------------------------


def test_check_names_the_convergence_state_so_it_agrees_with_classify(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["check", str(doc)]) == 0
    err = capsys.readouterr().err

    assert "AMPLIFYING" in err
    assert "auxflow classify" in err


def test_quiet_check_prints_nothing_when_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, r"\label{a}\ref{a}")

    assert cli.main(["--quiet", "check", str(doc)]) == 0
    captured = capsys.readouterr()

    assert captured.out == captured.err == ""


# --- command suggestions -----------------------------------------------------------------


def test_misspelled_command_suggests_the_nearest_command(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["clasify", "x.tex"])

    err = capsys.readouterr().err
    assert excinfo.value.code == 2
    assert "Did you mean 'classify'?" in err
    assert "choose from" not in err


def test_unrelated_command_points_to_help_without_a_guess(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["zzzzzz"])

    err = capsys.readouterr().err
    assert excinfo.value.code == 2
    assert "Did you mean" not in err
    assert "auxflow help" in err


# --- plan wording and JSON ---------------------------------------------------------------


def test_plan_explain_describes_passes_in_plain_words(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, r"\section{A}\label{a}\ref{a}")

    assert cli.main(["plan", "--explain", str(doc)]) == 0
    out = capsys.readouterr().out

    assert "pass 1 of 2" in out
    assert "P=" not in out
    assert "CERTIFIED derived bound" not in out
    assert "auxflow run" in out


def test_plan_json_prints_the_refusal_as_json_and_still_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["plan", "--json", str(doc)]) == 1
    plan = json.loads(capsys.readouterr().out)

    assert plan["classification"] == "AMPLIFYING"
    assert plan["steps"] == []


def test_forcing_an_amplifying_plan_warns_that_the_result_may_not_settle(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["plan", "--force", str(doc)]) == 0

    assert "--force" in capsys.readouterr().err


# --- machine output ----------------------------------------------------------------------


def test_check_json_lists_diagnostics_with_line_and_column(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, "x\n\\ref{absent}\n")

    assert cli.main(["check", "--json", str(doc)]) == 1
    data = json.loads(capsys.readouterr().out)

    assert data["ok"] is False
    assert data["errors"] == 1
    assert data["convergence"] in {"CERTIFIED", "UNKNOWN"}
    assert data["diagnostics"][0]["line"] == 2
    assert data["diagnostics"][0]["column"] == 1
    assert data["diagnostics"][0]["severity"] == "error"


def test_classify_json_names_the_cycle_locations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["classify", "--json", str(doc)]) == 1
    data = json.loads(capsys.readouterr().out)

    assert data["state"] == "AMPLIFYING"
    assert data["predicted_runs"] is None
    assert {item["kind"] for item in data["cycle"]} >= {"PAGEREF_USE", "LABEL_PAGE"}
    assert all(item["line"] >= 1 for item in data["cycle"])


def test_classify_json_exit_status_still_honours_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, _AMPLIFYING)

    assert cli.main(["classify", "--json", "--force", str(doc)]) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "AMPLIFYING"


# --- next steps and quiet ----------------------------------------------------------------


def test_classify_suggests_a_next_step_on_stderr_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, r"\label{a}\ref{a}")

    assert cli.main(["classify", str(doc)]) == 0
    captured = capsys.readouterr()

    assert "Next:" in captured.err
    assert "auxflow run" in captured.err
    assert "Next:" not in captured.out


def test_quiet_classify_omits_the_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = _doc(tmp_path, r"\label{a}\ref{a}")

    assert cli.main(["--quiet", "classify", str(doc)]) == 0

    assert capsys.readouterr().err == ""


def test_quiet_suppresses_the_update_notice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(cli.update, "notify_and_check", lambda installed: calls.append(installed))
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")
    doc = _doc(tmp_path, r"\label{a}")

    monkeypatch.setattr(cli.sys, "argv", ["auxflow", "--quiet", "check", str(doc)])
    cli.main()
    assert calls == []

    monkeypatch.setattr(cli.sys, "argv", ["auxflow", "check", str(doc)])
    cli.main()
    assert calls == ["0.2.0"]


# --- missing TeX tools -------------------------------------------------------------------


def test_missing_engine_is_reported_before_anything_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _no_tex_on_path(tmp_path, monkeypatch)
    source = _doc(tmp_path, r"\label{x}")
    plan = BuildPlan(
        "CERTIFIED",
        1,
        [Step("pdflatex", [str(source)], "main", "run 1", True)],
        6,
        "planned_count",
        [],
        {},
        "arg-0.1",
    )

    report = execute(plan, tmp_path)

    assert report.status == "tool_error"
    assert report.runs == 0
    assert "pdflatex was not found on PATH" in report.message
    assert "auxflow plan" in report.message


def test_run_explains_a_missing_engine_in_plain_words(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _no_tex_on_path(tmp_path, monkeypatch)
    doc = _doc(tmp_path, r"\label{x}\ref{x}")

    assert cli.main(["run", str(doc)]) == 1

    err = capsys.readouterr().err
    assert "pdflatex was not found on PATH" in err
    assert "Errno" not in err


# --- progress ----------------------------------------------------------------------------


def test_run_reports_each_pass_on_stderr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    _engine_on_path(tmp_path, monkeypatch)
    doc = _doc(tmp_path, r"\label{x}\ref{x}")

    assert cli.main(["run", str(doc)]) == 0
    captured = capfd.readouterr()

    assert "pass 1 of 2 (pdflatex)" in captured.err
    assert "pass 2 of 2 (pdflatex)" in captured.err
    assert "engine output" in captured.out
    assert json.loads(captured.out.splitlines()[-1])["status"] == "CONVERGED"


def test_quiet_run_hides_progress_but_keeps_the_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    _engine_on_path(tmp_path, monkeypatch)
    doc = _doc(tmp_path, r"\label{x}\ref{x}")

    assert cli.main(["--quiet", "run", str(doc)]) == 0
    captured = capfd.readouterr()

    assert "pass 1 of" not in captured.err
    assert json.loads(captured.out.splitlines()[-1])["status"] == "CONVERGED"


# --- doctor ------------------------------------------------------------------------------


def test_doctor_fails_and_names_the_missing_engine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _no_tex_on_path(tmp_path, monkeypatch)

    assert cli.main(["doctor"]) == 1
    out = capsys.readouterr().out

    assert "pdflatex" in out
    assert "not found" in out


def test_doctor_passes_with_an_engine_and_treats_other_tools_as_optional(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    engine = bin_dir / "pdflatex"
    engine.write_text(_ENGINE)
    engine.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))

    assert cli.main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)

    tools = {item["name"]: item for item in data["tools"]}
    assert tools["pdflatex"]["found"] is True
    assert tools["bibtex"]["found"] is False
    assert tools["bibtex"]["required"] is False
    assert data["ok"] is True
