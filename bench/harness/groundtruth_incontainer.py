#!/usr/bin/env python3
r"""Unconditional MAX-run sweep for ground-truth computation (host side
groundtruth.py computes N* from this driver's output; see docs/EVALUATION.md
"Ground truth").

Runs **inside the pinned container**. Performs exactly MAX engine passes
with no early stopping -- ground truth must not share a stopping rule with
any baseline under test, or it would not be independent. bibtex/biber runs
once after pass 1 if the document asks for one (docs/PROJECT.md D5). After
every pass, records the normalised auxiliary-state fingerprint (reusing
auxflow.runtime.execute._observed_state, the same function baseline C's
normstate.py and AuxFlow's own runtime verifier use) and the extracted text
layer (via pdftotext), per docs/EVALUATION.md's adopted ground-truth
criterion: state equality plus text equality against the MAX-run reference.

Usage: groundtruth_incontainer.py --jobname JOBNAME --max-runs MAX
Prints one JSON object to stdout:
  {"runs": [{"k": 1, "state_hash": "...", "text_hash": "...", "pdflatex_rc": 0}, ...]}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from auxflow.runtime.execute import _observed_state


def _state_hash(directory: Path, jobname: str) -> str:
    state = _observed_state(directory, jobname)
    canonical = "\n".join(sorted("\x1f".join(record) for record in state))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _text_hash(directory: Path, jobname: str) -> str:
    pdf = directory / f"{jobname}.pdf"
    if not pdf.is_file():
        return hashlib.sha256(b"").hexdigest()
    proc = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=False
    )
    text = proc.stdout if proc.returncode == 0 else ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _maybe_run_bibtool(directory: Path, jobname: str) -> None:
    bcf = directory / f"{jobname}.bcf"
    aux = directory / f"{jobname}.aux"
    if bcf.is_file():
        subprocess.run(["biber", jobname], cwd=directory, capture_output=True, check=False)
    elif aux.is_file() and "\\bibdata" in aux.read_text(encoding="utf-8", errors="replace"):
        subprocess.run(["bibtex", jobname], cwd=directory, capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobname", default="main")
    parser.add_argument("--max-runs", type=int, default=8)
    args = parser.parse_args()
    directory = Path.cwd()

    records: list[dict[str, object]] = []
    for k in range(1, args.max_runs + 1):
        proc = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-no-shell-escape",
                f"-jobname={args.jobname}",
                "main.tex",
            ],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
        )
        if k == 1:
            _maybe_run_bibtool(directory, args.jobname)
        records.append(
            {
                "k": k,
                "pdflatex_rc": proc.returncode,
                "state_hash": _state_hash(directory, args.jobname),
                "text_hash": _text_hash(directory, args.jobname),
            }
        )
    print(json.dumps({"runs": records}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
