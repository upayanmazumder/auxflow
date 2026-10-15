r"""Exercise classification, planning, and execution through the run CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from auxflow import cli

_ENGINE = r"""#!/usr/bin/env python3
from pathlib import Path
import sys

count = Path("engine.count")
run = int(count.read_text()) + 1 if count.exists() else 1
count.write_text(str(run))
mode = Path("mode.txt").read_text().strip()
value = 1 if mode == "stable" else min(run, 2) if mode == "one-extra" else run
jobname = next(arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("-jobname="))
Path(f"{jobname}.aux").write_text(f"\\newlabel{{x}}{{{{{value}}}{{1}}}}\n")
print(f"engine pass {run}")
"""
_AMPLIFYING = r"\newcounter{n}\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}\label{l}"


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, mode: str) -> Path:
    engine = tmp_path / "pdflatex"
    engine.write_text(_ENGINE)
    engine.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    (tmp_path / "mode.txt").write_text(mode)
    source = tmp_path / "main.tex"
    source.write_text(text)
    return source


def _report(capfd: pytest.CaptureFixture[str]) -> tuple[str, dict]:
    output = capfd.readouterr().out
    return output, json.loads(output.splitlines()[-1])


def test_certified_run_verifies_final_planned_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _fixture(tmp_path, monkeypatch, r"\label{x}", "stable")
    assert cli.main(["run", str(source)]) == 0
    output, report = _report(capfd)
    assert "engine pass 2" in output
    assert report == {
        "message": "auxiliary state stable at run 2",
        "prediction_miss": None,
        "runs": 2,
        "status": "CONVERGED",
        "stop_condition": "planned_count",
    }
    assert (tmp_path / "engine.count").read_text() == "2"


def test_run_reports_prediction_miss_after_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _fixture(tmp_path, monkeypatch, r"\label{x}", "one-extra")
    assert cli.main(["run", str(source)]) == 0
    _, report = _report(capfd)
    assert report["stop_condition"] == "aux_fixpoint"
    assert report["runs"] == 3
    assert report["prediction_miss"] == {
        "document": str(source),
        "predicted": 2,
        "observed": 3,
    }


def test_run_refuses_amplifying_and_strict_unknown_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _fixture(tmp_path, monkeypatch, _AMPLIFYING, "changing")
    assert cli.main(["run", str(source)]) == 1
    output, report = _report(capfd)
    assert "AMPLIFYING CYCLE" in output
    assert report["status"] == "amplifying_refused"
    assert not (tmp_path / "engine.count").exists()

    source.write_text(r"\usepackage{exotic}\label{x}")
    assert cli.main(["run", "--strict", str(source)]) == 1
    _, report = _report(capfd)
    assert report["status"] == "opaque_abort"
    assert not (tmp_path / "engine.count").exists()


def test_forced_amplifying_run_reaches_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    source = _fixture(tmp_path, monkeypatch, _AMPLIFYING, "changing")
    assert cli.main(["run", "--force", str(source)]) == 1
    _, report = _report(capfd)
    assert report["status"] == "cap_exceeded"
    assert report["stop_condition"] == "cap"
    assert report["runs"] == 6
    assert (tmp_path / "engine.count").read_text() == "6"
