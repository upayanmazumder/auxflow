"""Phase 1 acceptance (sub-issue #19): the planner safety invariant, written
before any other planner code.

docs/BUILD-PLANNER.md "Safety invariant": the emitted plan is never shorter
than the conservative default unless the classification is CERTIFIED. This is
the reason an analysis bug cannot silently corrupt a document -- the worst
outcome is a plan that is too long, never too short.

No real planner exists yet (that is phase 12). This test exercises
auxflow.planner.assert_safety_invariant directly against the stub
conservative-default step count, over randomly generated classifications and
plan lengths, per tests/README.md's "two tests that matter most".
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from auxflow.planner import CONSERVATIVE_DEFAULT_STEP_COUNT, assert_safety_invariant

NON_CERTIFIED = ("BENIGN_CYCLIC", "AMPLIFYING", "UNKNOWN")


@given(
    classification=st.sampled_from(NON_CERTIFIED),
    plan_step_count=st.integers(min_value=0, max_value=CONSERVATIVE_DEFAULT_STEP_COUNT - 1),
)
def test_non_certified_plan_shorter_than_conservative_default_is_rejected(
    classification: str, plan_step_count: int
) -> None:
    with pytest.raises(AssertionError):
        assert_safety_invariant(classification, plan_step_count)  # type: ignore[arg-type]


@given(
    classification=st.sampled_from(NON_CERTIFIED),
    plan_step_count=st.integers(min_value=CONSERVATIVE_DEFAULT_STEP_COUNT, max_value=50),
)
def test_non_certified_plan_at_or_above_conservative_default_is_accepted(
    classification: str, plan_step_count: int
) -> None:
    assert_safety_invariant(classification, plan_step_count)  # type: ignore[arg-type]


@given(plan_step_count=st.integers(min_value=0, max_value=50))
def test_certified_plan_is_never_rejected_regardless_of_length(plan_step_count: int) -> None:
    # CERTIFIED is the one classification allowed to emit a plan shorter than
    # the conservative default -- that is what "certified" means.
    assert_safety_invariant("CERTIFIED", plan_step_count)
