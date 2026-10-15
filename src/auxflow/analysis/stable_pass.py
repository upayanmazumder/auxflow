r"""Stable-pass numbering. docs/STATIC-ANALYSIS.md section 4.

Computed on the condensation, which is why cycles cannot cause
non-termination: a longest path over a DAG in topological order.
"""

from __future__ import annotations

from auxflow.analysis.classify_cycles import Label
from auxflow.analysis.condensation import Condensation
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepType, FactKind

StablePass = dict[int, int | None]


def _direct_preds(arg: ARG, fact_id: int) -> list[tuple[int, int]]:
    """`(predecessor_fact_id, effective_lag)` for every ARG edge into `fact_id`.

    A `TOOL` edge's effective lag is 0, not its stored `pass_lag` (1): open
    decision D5 (the exact lag semantics for the TOOL edge) is unresolved
    in general, but docs/IR.md's bibliography-cascade worked example
    resolves it for stable-pass purposes specifically -- "BBL.exists ...
    1 (external tool runs after run 1)" only holds if bibtex's output is
    available within the same pass as its input, not one pass later. The
    stored `pass_lag=1` on the edge itself is unaffected; only this
    recurrence's local lag term is adjusted.
    """
    return [
        (edge.source, 0 if edge.dependency_type is DepType.TOOL else edge.pass_lag)
        for edge in arg.edges
        if edge.destination == fact_id
    ]


def compute_stable_pass(
    arg: ARG, condensation: Condensation, labels: dict[int, Label]
) -> StablePass:
    """Per-fact stable_pass, visiting `condensation.components` in order.

    `condensation.components` is already in forward topological order
    (predecessors before successors; see `auxflow.analysis.condensation`),
    so every predecessor's stable_pass is computed before it is needed.

    - A member of an `AMPLIFYING` or `UNKNOWN_CYCLE` component is `None`
      (not bounded).
    - A `BENIGN` cycle (`|C| > 1`) gets `base + |C|`, where `base` is
      `1 + max(stable_pass[g] for g in preds(C) if bounded, default 0)`.
      **This is a heuristic, not a proof** -- open decision D7 in
      docs/PROJECT.md -- plausible for the list-and-pagination feedback
      the project models, but not established in general. It must never
      be tuned to make a specific corpus document match; if measurement
      shows it mispredicting, the documented response is to reclassify
      benign cycles as unbounded, not to adjust this formula.
    - A trivial singleton (not classified by phase 8, so not present in
      `labels`) gets `1` if it has no predecessors, `None` if any
      predecessor is unbounded, else
      `1 + max(stable_pass[g] + lag(g, f) - 1 for g in preds(f))`.
    """
    stable_pass: StablePass = {}

    for component in condensation.components:
        label = labels.get(component[0])
        if label in (Label.AMPLIFYING, Label.UNKNOWN_CYCLE):
            for fact_id in component:
                stable_pass[fact_id] = None
        elif len(component) > 1:
            # BENIGN cycle: open-decision-D7 heuristic, see docstring above.
            members = set(component)
            bounded_pred_passes = [
                value
                for fact_id in component
                for edge_source, _lag in _direct_preds(arg, fact_id)
                if edge_source not in members
                and (value := stable_pass.get(edge_source)) is not None
            ]
            base = 1 + max(bounded_pred_passes, default=0)
            for fact_id in component:
                stable_pass[fact_id] = base + len(component)
        else:
            (fact_id,) = component
            preds = _direct_preds(arg, fact_id)
            pred_passes = [stable_pass[pred] for pred, _lag in preds]
            if not preds:
                stable_pass[fact_id] = 1
            elif any(value is None for value in pred_passes):
                stable_pass[fact_id] = None
            else:
                stable_pass[fact_id] = 1 + max(
                    value + lag - 1
                    for value, (_pred, lag) in zip(pred_passes, preds, strict=True)
                    if value is not None
                )

    return stable_pass


_CONSUMER_ONLY = frozenset({FactKind.REF_USE, FactKind.PAGEREF_USE})


def predicted_runs(arg: ARG, stable_pass: StablePass) -> int:
    r"""`P + 1`, where `P` is the maximum bounded stable_pass of facts
    actually stored in an auxiliary file (0 if none).

    `REF_USE`/`PAGEREF_USE` are excluded: `\ref`/`\pageref` are pure
    consumers rendered directly into output, never themselves written to
    any auxiliary file (see docs/IR.md's "backward reference" example:
    "REF_USE is a consumer rendered into output, not a fact stored in the
    auxiliary file, so P = 1" even though REF_USE's own stable_pass is 2).
    Including them would overcount P by one run whenever a `\ref`/
    `\pageref` has the longest dependency chain in the document, as the
    bibliography-cascade example demonstrates (`PAGEREF_USE`'s stable_pass
    of 4 must not raise P past 3).
    """
    bounded = [
        value
        for fact_id, value in stable_pass.items()
        if value is not None and arg.facts[fact_id].kind not in _CONSUMER_ONLY
    ]
    return max(bounded, default=0) + 1
