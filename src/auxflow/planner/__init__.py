"""Phases 11-12: optimisation and build-plan generation.

Four optimisation passes and lowering to a BuildPlan. The safety invariant -- never
emit a plan shorter than the conservative default unless CERTIFIED -- is implemented
here and enforced by a property test. See docs/BUILD-PLANNER.md.
"""

from __future__ import annotations

from typing import Literal

Classification = Literal["CERTIFIED", "BENIGN_CYCLIC", "AMPLIFYING", "UNKNOWN"]

# docs/BUILD-PLANNER.md "Conservative default plan": the floor is the three
# pdflatex runs (bibtex/spellcheck/index steps are additive on top, never
# subtracted). This stub is replaced by the real lowering-rule step count in
# phase 12; the invariant and its test must not depend on that replacement.
CONSERVATIVE_DEFAULT_STEP_COUNT = 3


def assert_safety_invariant(classification: Classification, plan_step_count: int) -> None:
    """docs/BUILD-PLANNER.md "Safety invariant".

    The emitted plan is never shorter than the conservative default unless the
    classification is CERTIFIED. Written before any other planner code so that
    no later planner change can silently violate it: an analysis bug can at
    worst make a plan too long, never too short.
    """
    if classification == "CERTIFIED":
        return
    if plan_step_count < CONSERVATIVE_DEFAULT_STEP_COUNT:
        raise AssertionError(
            f"planner safety invariant violated: {classification} document emitted a "
            f"{plan_step_count}-step plan, shorter than the "
            f"{CONSERVATIVE_DEFAULT_STEP_COUNT}-step conservative default"
        )
