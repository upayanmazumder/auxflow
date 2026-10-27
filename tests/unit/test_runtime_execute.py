r"""Exercise the executor with a deterministic TeX-like process.

The fixture executable writes actual auxiliary files across subprocess runs.
Tests assert state transitions, not calls to a substituted runner.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from auxflow.planner.model import BuildPlan, Step
from auxflow.runtime.execute import PredictionMiss, execute

_ENGINE = r"""#!/usr/bin/env python3
from pathlib import Path
import sys

import time
count = Path("engine.count")
run = int(count.read_text()) + 1 if count.exists() else 1
count.write_text(str(run))
mode = Path("mode.txt").read_text().strip()
if mode == "hang" or (mode == "hang-after" and run >= 3):
    time.sleep(5)
if mode == "error":
    print("engine failed")
    sys.exit(7)
jobname = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("-jobname="))
if mode == "empty":
    Path(f"{jobname}.aux").write_text("\\relax\n")
elif mode == "included":
    Path(f"{jobname}.aux").write_text("\\@input{chapter.aux}\n")
    Path("chapter.aux").write_text(f"\\newlabel{{x}}{{{{{min(run, 2)}}}{{1}}}}\n")
else:
    value = 1 if mode == "stable" else min(run, 2) if mode == "one-extra" else run
    Path(f"{jobname}.aux").write_text(f"\\newlabel{{x}}{{{{{value}}}{{1}}}}\n")
print(f"engine pass {run}")
"""


def _setup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str) -> Path:
    binary = tmp_path / "pdflatex"
    binary.write_text(_ENGINE)
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    (tmp_path / "mode.txt").write_text(mode)
    source = tmp_path / "main.tex"
    source.write_text(r"\documentclass{article}\begin{document}Hi\end{document}")
    return source


def _plan(source: Path, *, runs: int = 4, classification: str = "CERTIFIED") -> BuildPlan:
    steps = [
        Step("pdflatex", [str(source)], "main", f"run {run}", run == runs)
        for run in range(1, runs + 1)
    ]
    return BuildPlan(
        classification,
        runs if classification == "CERTIFIED" else None,
        steps,
        6,
        "planned_count" if classification == "CERTIFIED" else "aux_fixpoint",
        [],
        {},
        "arg-0.1",
    )


def test_early_fixpoint_stops_before_remaining_planned_steps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "stable")

    report = execute(_plan(source), tmp_path)

    assert report.status == "CONVERGED"
    assert report.stop_condition == "aux_fixpoint"
    assert report.runs == 2
    assert report.prediction_miss is None
    assert (tmp_path / "engine.count").read_text() == "2"


def test_included_auxiliary_file_changes_delay_fixpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "included")

    report = execute(_plan(source), tmp_path)

    assert report.status == "CONVERGED"
    assert report.runs == 3
    assert (tmp_path / "engine.count").read_text() == "3"


def test_never_stable_reaches_cap_with_failure_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    source = _setup(tmp_path, monkeypatch, "changing")

    report = execute(_plan(source, runs=3), tmp_path)

    assert report.status == "cap_exceeded"
    assert report.stop_condition == "cap"
    assert report.runs == 6
    assert report.exit_code == 1
    assert "suspected non-convergence" in report.message
    assert (tmp_path / "engine.count").read_text() == "6"
    assert report.prediction_miss == PredictionMiss(str(source), 3, 6)
    assert [r.message for r in caplog.records if r.message.startswith("prediction miss:")] == [
        f"prediction miss: document={source} predicted=3 observed=6"
    ]


def test_one_extension_run_records_exactly_one_prediction_miss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    source = _setup(tmp_path, monkeypatch, "one-extra")

    report = execute(_plan(source, runs=2), tmp_path)

    assert report.status == "CONVERGED"
    assert report.stop_condition == "aux_fixpoint"
    assert report.runs == 3
    assert report.prediction_miss == PredictionMiss(str(source), 2, 3)
    assert [r.message for r in caplog.records if r.message.startswith("prediction miss:")] == [
        f"prediction miss: document={source} predicted=2 observed=3"
    ]


def test_single_run_with_empty_auxiliary_state_meets_planned_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "empty")

    report = execute(_plan(source, runs=1), tmp_path)

    assert report.status == "CONVERGED"
    assert report.stop_condition == "planned_count"
    assert report.runs == 1


def test_tool_failure_keeps_original_log_and_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _setup(tmp_path, monkeypatch, "error")

    report = execute(_plan(source), tmp_path)

    assert report.status == "tool_error"
    assert report.exit_code == 1
    assert report.message == "pdflatex exited with status 7. See main.log for the error."
    assert capfd.readouterr().out == "engine failed\n"
    assert (tmp_path / "engine.count").read_text() == "1"


def test_hung_engine_stops_at_configured_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "hang")

    report = execute(_plan(source), tmp_path, timeout=0.05)

    assert report.status == "tool_error"
    assert report.exit_code == 1
    assert report.runs == 0
    assert report.message == "pdflatex timed out after 0.05 seconds"
    assert (tmp_path / "engine.count").read_text() == "1"


def test_extension_run_obeys_the_same_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "hang-after")

    report = execute(_plan(source, runs=2), tmp_path, timeout=0.05)

    assert report.status == "tool_error"
    assert report.runs == 2
    assert report.message == "pdflatex timed out after 0.05 seconds"
    assert (tmp_path / "engine.count").read_text() == "3"


def test_auxiliary_symlink_outside_work_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "stable")
    external = tmp_path.parent / f"{tmp_path.name}-private.toc"
    external.write_text("external contents")
    (tmp_path / "main.toc").symlink_to(external)

    report = execute(_plan(source), tmp_path)

    assert report.status == "tool_error"
    assert report.runs == 1
    assert "escapes work directory" in report.message


def test_missing_input_aborts_before_any_tool_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "changing")
    source.unlink()

    report = execute(_plan(source), tmp_path)

    assert report.status == "missing_input"
    assert report.runs == 0
    assert not (tmp_path / "engine.count").exists()


def test_strict_unknown_and_amplifying_refusal_do_not_execute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "stable")

    unknown = execute(_plan(source, classification="UNKNOWN"), tmp_path, strict=True)
    refused = execute(BuildPlan("AMPLIFYING", None, [], 6, "cap", [], {}, "arg-0.1"), tmp_path)

    assert unknown.status == "opaque_abort"
    assert refused.status == "amplifying_refused"
    assert unknown.exit_code == refused.exit_code == 1
    assert not (tmp_path / "engine.count").exists()


def test_bibliography_step_runs_between_engine_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _setup(tmp_path, monkeypatch, "stable")
    bibliography = tmp_path / "bibtex"
    bibliography.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        'Path("main.bbl").write_text("\\\\bibitem{k} A.\\n")\n'
        'print("bibliography pass")\n'
    )
    bibliography.chmod(0o755)
    steps = [
        Step("pdflatex", [str(source)], "main", "initial pass", False),
        Step("bibtex", [], "main", "citation and bibliography", False),
        Step("pdflatex", [str(source)], "main", "consume bibliography", False),
        Step("pdflatex", [str(source)], "main", "verify", True),
    ]
    plan = BuildPlan("CERTIFIED", 3, steps, 6, "planned_count", [], {}, "arg-0.1")

    report = execute(plan, tmp_path)

    assert report.status == "CONVERGED"
    assert report.stop_condition == "planned_count"
    assert report.runs == 3
    assert capfd.readouterr().out == (
        "engine pass 1\nbibliography pass\nengine pass 2\nengine pass 3\n"
    )


def test_final_engine_step_without_verification_is_rejected_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _setup(tmp_path, monkeypatch, "stable")
    unverified = BuildPlan(
        "CERTIFIED",
        1,
        [Step("pdflatex", [str(source)], "main", "run 1", False)],
        6,
        "planned_count",
        [],
        {},
        "arg-0.1",
    )

    report = execute(unverified, tmp_path)

    assert report.status == "tool_error"
    assert report.message == "final engine step must request verification"
    assert not (tmp_path / "engine.count").exists()
