r"""Execute a BuildPlan and compare normalized state after each engine run."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from auxflow.planner.model import BuildPlan, Step
from auxflow.runtime.normalize import AuxState, normalize_aux_file, normalize_state

Outcome = Literal[
    "CONVERGED", "tool_error", "missing_input", "cap_exceeded", "opaque_abort", "amplifying_refused"
]
StopCondition = Literal["planned_count", "aux_fixpoint", "cap"]
_OBSERVED_SUFFIXES = (".aux", ".toc", ".lof", ".lot", ".bbl", ".ind")


@dataclass(frozen=True)
class ExecReport:
    status: Outcome
    stop_condition: StopCondition | None
    runs: int
    message: str

    @property
    def exit_code(self) -> int:
        return 0 if self.status == "CONVERGED" else 1


def _input_path(step: Step, directory: Path) -> Path | None:
    if step.tool not in {"pdflatex", "spellcheck"} or not step.args:
        return None
    path = Path(step.args[-1])
    return path if path.is_absolute() else directory / path


def _command(step: Step) -> list[str]:
    if step.tool == "pdflatex":
        return [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-jobname={step.jobname}",
            *step.args,
        ]
    if step.tool in {"bibtex", "makeindex"}:
        return [step.tool, step.jobname, *step.args]
    if step.tool == "spellcheck":
        return [step.tool, *step.args]
    raise ValueError(f"unsupported plan tool: {step.tool}")


def _execute_step(step: Step, directory: Path) -> int:
    # Inherit stdout/stderr: TeX's original log must remain unmodified.
    return subprocess.run(_command(step), cwd=directory, check=False).returncode


def _observed_state(directory: Path, jobname: str) -> AuxState:
    contents: dict[str, str] = {}
    root = directory.resolve()
    pending = [root / f"{jobname}.aux"]
    seen: set[Path] = set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        if not path.is_relative_to(root):
            raise ValueError(f"auxiliary include escapes work directory: {path}")
        if not path.exists():
            continue
        source = path.read_bytes().decode("utf-8", errors="surrogateescape")
        contents[str(path)] = source
        for record in normalize_aux_file(source, ".aux"):
            if len(record) == 3 and record[:2] == ("other", "@input"):
                argument = record[2]
                if argument.startswith("{") and argument.endswith("}"):
                    pending.append(path.parent / argument[1:-1])
    for suffix in _OBSERVED_SUFFIXES[1:]:
        path = root / f"{jobname}{suffix}"
        if path.exists():
            contents[str(path)] = path.read_bytes().decode("utf-8", errors="surrogateescape")
    return normalize_state(contents)


def execute(plan: BuildPlan, directory: Path, *, strict: bool = False) -> ExecReport:
    """Run planned steps, then extend only while auxiliary state changes.

    Observe each engine pass even when the plan's `verify_after` flag is false.
    The final flagged pass must confirm the state or trigger bounded extension.
    """
    if plan.classification == "AMPLIFYING" and not plan.steps:
        return ExecReport("amplifying_refused", None, 0, "amplifying plan refused without --force")
    if strict and plan.classification == "UNKNOWN":
        return ExecReport("opaque_abort", None, 0, "unknown plan refused under --strict")
    for step in plan.steps:
        input_path = _input_path(step, directory)
        if input_path is not None and not input_path.is_file():
            return ExecReport("missing_input", None, 0, f"missing input: {input_path}")

    engine_steps = [step for step in plan.steps if step.tool == "pdflatex"]
    if not engine_steps:
        return ExecReport("tool_error", None, 0, "plan has no engine steps")
    if not engine_steps[-1].verify_after:
        return ExecReport("tool_error", None, 0, "final engine step must request verification")
    previous: AuxState | None = None
    runs = 0
    for step in plan.steps:
        try:
            code = _execute_step(step, directory)
        except (OSError, ValueError) as error:
            return ExecReport("tool_error", None, runs, str(error))
        if code != 0:
            return ExecReport("tool_error", None, runs, f"{step.tool} exited with status {code}")
        if step.tool != "pdflatex":
            continue
        runs += 1
        try:
            current = _observed_state(directory, step.jobname)
        except (OSError, ValueError) as error:
            return ExecReport("tool_error", None, runs, str(error))
        if previous is not None and current == previous:
            condition: StopCondition = (
                "planned_count"
                if runs == len(engine_steps) and plan.stop_condition == "planned_count"
                else "aux_fixpoint"
            )
            return ExecReport("CONVERGED", condition, runs, f"auxiliary state stable at run {runs}")
        previous = current

    # With no observed facts, run one is sufficient: the empty state is fixed.
    if runs == 1 and previous == frozenset() and plan.stop_condition == "planned_count":
        return ExecReport("CONVERGED", "planned_count", 1, "auxiliary state empty after run 1")

    last_engine = engine_steps[-1]
    while runs < plan.max_runs:
        try:
            code = _execute_step(last_engine, directory)
        except (OSError, ValueError) as error:
            return ExecReport("tool_error", None, runs, str(error))
        if code != 0:
            return ExecReport("tool_error", None, runs, f"pdflatex exited with status {code}")
        runs += 1
        try:
            current = _observed_state(directory, last_engine.jobname)
        except (OSError, ValueError) as error:
            return ExecReport("tool_error", None, runs, str(error))
        if current == previous:
            return ExecReport(
                "CONVERGED", "aux_fixpoint", runs, f"auxiliary state stable at run {runs}"
            )
        previous = current
    return ExecReport(
        "cap_exceeded",
        "cap",
        runs,
        f"suspected non-convergence: auxiliary state changed through run {runs}",
    )
