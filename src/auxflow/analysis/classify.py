r"""The four-state document classifier. docs/NON-CONVERGENCE.md.

Turns SCC analysis (phase 8), taint (phase 9), and stable-pass numbering
(phase 10) into one of CERTIFIED / BENIGN_CYCLIC / AMPLIFYING / UNKNOWN,
with the exact conditions from the "The four states" table.

Required wording: AuxFlow must never claim a document "cannot converge"
or "will not terminate" -- only that it "may not converge". A false
positive here costs the user one flag; a false negative costs a silently
wrong document. This module and its callers must preserve that asymmetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from auxflow.analysis.classify_cycles import Label
from auxflow.analysis.stable_pass import StablePass, predicted_runs
from auxflow.ir.graph import ARG


class State(Enum):
    CERTIFIED = auto()
    BENIGN_CYCLIC = auto()
    AMPLIFYING = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class Classification:
    state: State
    predicted_runs: int | None
    """`N`: set for CERTIFIED and BENIGN_CYCLIC (this implementation's
    BENIGN heuristic always yields a bounded value); None for AMPLIFYING
    and UNKNOWN, which never claim a run count."""
    amplifying_components: tuple[tuple[int, ...], ...]
    """Fact ids of every AMPLIFYING-labelled component; empty unless
    `state is State.AMPLIFYING`."""
    opaque_fact_ids: tuple[int, ...]
    """Every opaque fact's id; empty unless `state is State.UNKNOWN`."""


def classify(
    arg: ARG,
    components: list[tuple[int, ...]],
    labels: dict[int, Label],
    stable_pass: StablePass,
) -> Classification:
    """Classify a document from its ARG and the phase 8/9/10 analysis results.

    Precedence matches `auxflow.analysis.classify_cycles.classify_components`
    at the per-cycle level: an AMPLIFYING cycle takes precedence over an
    opaque fact, so a document containing both is reported as AMPLIFYING,
    not UNKNOWN -- the more severe, more actionable signal.
    """
    amplifying = tuple(
        component
        for component in components
        if component and labels.get(component[0]) is Label.AMPLIFYING
    )
    if amplifying:
        return Classification(State.AMPLIFYING, None, amplifying, ())

    opaque_fact_ids = tuple(fact_id for fact_id, fact in arg.facts.items() if fact.opaque)
    if opaque_fact_ids:
        return Classification(State.UNKNOWN, None, (), opaque_fact_ids)

    has_cycle = any(len(component) > 1 for component in components) or any(
        labels.get(component[0]) is not None for component in components if len(component) == 1
    )
    state = State.BENIGN_CYCLIC if has_cycle else State.CERTIFIED
    return Classification(state, predicted_runs(arg, stable_pass), (), ())
