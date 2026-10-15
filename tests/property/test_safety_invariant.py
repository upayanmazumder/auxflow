"""The planner safety invariant, installed before other planner code.

Only engine runs count toward the conservative floor. Extra tool steps cannot
mask a plan with too few engine runs.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from auxflow.planner import CONSERVATIVE_DEFAULT_ENGINE_RUNS, assert_safety_invariant

NON_CERTIFIED = ("BENIGN_CYCLIC", "AMPLIFYING", "UNKNOWN")
OTHER_TOOLS = st.lists(st.sampled_from(("bibtex", "spellcheck", "makeindex")), max_size=10)


@given(
    classification=st.sampled_from(NON_CERTIFIED),
    engine_runs=st.integers(min_value=0, max_value=CONSERVATIVE_DEFAULT_ENGINE_RUNS - 1),
    other_tools=OTHER_TOOLS,
)
def test_non_certified_plan_with_fewer_engine_runs_is_rejected(
    classification: str, engine_runs: int, other_tools: list[str]
) -> None:
    # Even ten auxiliary steps cannot conceal one missing engine run.
    tools = other_tools + ["pdflatex"] * engine_runs
    with pytest.raises(AssertionError):
        assert_safety_invariant(classification, tools)  # type: ignore[arg-type]


@given(
    classification=st.sampled_from(NON_CERTIFIED),
    engine_runs=st.integers(min_value=CONSERVATIVE_DEFAULT_ENGINE_RUNS, max_value=50),
    other_tools=OTHER_TOOLS,
)
def test_non_certified_plan_with_at_least_three_engine_runs_is_accepted(
    classification: str, engine_runs: int, other_tools: list[str]
) -> None:
    assert_safety_invariant(
        classification,
        other_tools + ["pdflatex"] * engine_runs,  # type: ignore[arg-type]
    )


@given(engine_runs=st.integers(min_value=0, max_value=50), other_tools=OTHER_TOOLS)
def test_certified_plan_may_have_fewer_engine_runs(
    engine_runs: int, other_tools: list[str]
) -> None:
    assert_safety_invariant("CERTIFIED", other_tools + ["pdflatex"] * engine_runs)
