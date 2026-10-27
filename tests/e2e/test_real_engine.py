"""Run the CLI against a real TeX installation. Skipped when `pdflatex` is not on PATH.

Marked `engine`, so `make test-fast` and CI exclude it. These tests check that the static
prediction matches what the real engine does, which the fake-engine tests cannot show.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from auxflow import cli

pytestmark = [
    pytest.mark.engine,
    pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex is not installed"),
]

_REFERENCE = (
    "\\documentclass{article}\\begin{document}\n"
    "See Section~\\ref{sec:a}.\\section{A}\\label{sec:a}\n"
    "\\end{document}\n"
)
_CONTENTS = (
    "\\documentclass{article}\\begin{document}\n"
    "\\tableofcontents\\section{One}Text.\\section{Two}More.\n"
    "\\end{document}\n"
)


def _run(tmp_path: Path, source: str, capfd: pytest.CaptureFixture[str]) -> tuple[int, dict]:
    doc = tmp_path / "main.tex"
    doc.write_text(source)
    code = cli.main(["--quiet", "run", str(doc)])
    report = json.loads(capfd.readouterr().out.splitlines()[-1])
    return code, report


def test_forward_reference_settles_in_the_predicted_number_of_runs(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    code, report = _run(tmp_path, _REFERENCE, capfd)

    assert code == 0
    assert report["status"] == "CONVERGED"
    assert report["prediction_miss"] is None
    assert report["runs"] == 2
    assert (tmp_path / "main.pdf").is_file()


def test_table_of_contents_document_converges_without_a_prediction_miss(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    code, report = _run(tmp_path, _CONTENTS, capfd)

    assert code == 0
    assert report["status"] == "CONVERGED"
    assert report["prediction_miss"] is None
    assert (tmp_path / "main.pdf").is_file()


def test_a_tex_error_points_at_the_log_file(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    code, report = _run(
        tmp_path, "\\documentclass{article}\\begin{document}\\undefinedmacro\\end{document}", capfd
    )

    assert code == 1
    assert report["status"] == "tool_error"
    assert "See main.log for the error." in report["message"]
    assert (tmp_path / "main.log").is_file()
