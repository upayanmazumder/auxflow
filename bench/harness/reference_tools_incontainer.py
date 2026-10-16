#!/usr/bin/env python3
r"""Run the shipping reference tools against one corpus document and record
their verdicts (docs/EVALUATION.md "Reference implementations to run
alongside"): these are a cross-check for RQ6, not baselines -- the harness
re-implements the oracles baselines C/C'/C'' stand for; this driver confirms
the real tools those oracles describe actually behave the documented way.

Runs **inside the pinned container**. For each of latexmk, latexrun and
Tectonic: compiles the document with that tool, records whether it reports
success and (for latexmk/latexrun, which rerun pdflatex internally) how
many pdflatex passes its own log shows. `labelschanged` is loaded for the
latexmk run specifically, via a throwaway sibling copy with its preamble
patched -- never the committed corpus source -- so its per-label change
report is captured without altering what every other tool compiles.

Usage: reference_tools_incontainer.py --jobname JOBNAME
Prints one JSON object to stdout.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

_PDFLATEX_PASS = re.compile(r"^This is pdfTeX", re.MULTILINE)
_LABEL_CHANGED = re.compile(r"Label.*changed", re.IGNORECASE)


def _run(cmd: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_latexmk(directory: Path, jobname: str) -> dict[str, object]:
    code, out, err = _run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-jobname={jobname}",
            "main.tex",
        ],
        directory,
    )
    # The .log file is overwritten by each internal pdflatex invocation;
    # latexmk's own stdout is the only place that accumulates one "Run
    # number k of rule 'pdflatex'" line per actual pass.
    passes = len(re.findall(r"Run number \d+ of rule 'pdflatex'", out))
    return {
        "tool": "latexmk",
        "converged": code == 0,
        "returncode": code,
        "pdflatex_passes": passes,
        "stderr_tail": err[-500:],
    }


def run_latexmk_with_labelschanged(directory: Path, jobname: str) -> dict[str, object]:
    """A throwaway *sibling* copy (not a child, so its own "../shared"
    relative paths still resolve correctly) with \\usepackage{labelschanged}
    injected after \\documentclass."""
    work = directory.parent / f"{directory.name}_labelschanged_check"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(directory, work)
    source = (work / "main.tex").read_text(encoding="utf-8")
    patched = re.sub(
        r"(\\documentclass(\[[^\]]*\])?\{[^}]*\})",
        r"\1\n\\usepackage{labelschanged}",
        source,
        count=1,
    )
    (work / "main.tex").write_text(patched, encoding="utf-8")
    job = f"{jobname}_lc"
    code, _out, _err = _run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", f"-jobname={job}", "main.tex"],
        work,
    )
    log_path = work / f"{job}.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    changed_labels = _LABEL_CHANGED.findall(log)
    return {
        "tool": "latexmk+labelschanged",
        "converged": code == 0,
        "returncode": code,
        "label_changed_reports": len(changed_labels),
    }


def run_latexrun(directory: Path, jobname: str) -> dict[str, object]:
    # -O . keeps intermediate files beside main.tex rather than latexrun's
    # default latex.out/ sandbox, whose extra directory level breaks this
    # corpus's "../shared/..." relative bibliography paths.
    code, out, err = _run(
        ["latexrun", "-O", ".", f"--latex-args=-jobname={jobname}", "main.tex"], directory
    )
    passes = out.count("Running pdflatex") + err.count("Running pdflatex")
    return {
        "tool": "latexrun",
        "converged": code == 0,
        "returncode": code,
        "pdflatex_passes": passes,
        "stderr_tail": err[-500:],
    }


def run_tectonic(directory: Path, jobname: str) -> dict[str, object]:
    code, _out, err = _run(
        ["tectonic", "--outfmt", "pdf", "-o", ".", "main.tex"], directory, timeout=180
    )
    return {
        "tool": "tectonic",
        "converged": code == 0,
        "returncode": code,
        "stderr_tail": err[-500:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobname", default="main")
    args = parser.parse_args()
    directory = Path.cwd()

    results = [
        run_latexmk(directory, args.jobname),
        run_latexmk_with_labelschanged(directory, args.jobname),
        run_latexrun(directory, args.jobname),
        run_tectonic(directory, args.jobname),
    ]
    print(json.dumps({"results": results}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
