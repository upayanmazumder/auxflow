"""Build-plan safety: non-certified plans require three engine runs.

Auxiliary tool steps do not replace engine runs. See docs/BUILD-PLANNER.md.
"""

from __future__ import annotations

from typing import Literal

Classification = Literal["CERTIFIED", "BENIGN_CYCLIC", "AMPLIFYING", "UNKNOWN"]

# The conservative plan includes three engine runs. Optional tool steps
# cannot make a shorter engine schedule safe.
CONSERVATIVE_DEFAULT_ENGINE_RUNS = 3
MAX_RUNS_UNDER_FORCE = 6


def assert_safety_invariant(classification: Classification, tools: list[str]) -> None:
    """Reject a non-certified plan with fewer than three engine runs.

    A refused amplifying plan has no steps and must not call this function.
    """
    if classification == "CERTIFIED":
        return
    engine_runs = tools.count("pdflatex")
    if engine_runs < CONSERVATIVE_DEFAULT_ENGINE_RUNS:
        raise AssertionError(
            f"planner safety invariant violated: {classification} document emitted "
            f"{engine_runs} engine runs, fewer than the "
            f"{CONSERVATIVE_DEFAULT_ENGINE_RUNS}-run conservative default"
        )
