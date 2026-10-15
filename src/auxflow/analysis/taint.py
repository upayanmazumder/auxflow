r"""Content-quantity taint propagation. docs/STATIC-ANALYSIS.md section 2.

The step that separates benign feedback from amplifying feedback: which
fact values can influence how much content the document generates.
"""

from __future__ import annotations

from auxflow.ir.graph import ARG


def seed_facts(arg: ARG) -> set[int]:
    """Facts whose value is read in a ControlConstruct's condition or bound.

    docs/STATIC-ANALYSIS.md section 2 names two further seed sources: a
    `\\setcounter` argument that writes a counter bounding such a construct,
    and a page-emitting construct (`\\newpage`/`\\clearpage`) under such
    control. Neither currently has a corresponding ARG fact to seed:
    lowering (phase 7) only records a fact for `\\value` when it already
    appears inside a ControlConstruct (so a `\\setcounter{n}{\\value{m}}`
    outside any loop produces no fact at all), and `\\newpage`/`\\clearpage`
    are bare, fact-free macros by design. No acceptance criterion or
    documented corpus mechanism (b08, b05, b11-b13) exercises either case,
    so only the condition/bound case is implemented here. This is a
    documented limitation, not a silent omission.

    The seed rule is where the taint analysis is deliberately unsound (see
    docs/STATIC-ANALYSIS.md: "the unsoundness is in the seeds, not the
    propagation"); widening it is open decision D13 in docs/PROJECT.md.
    """
    return {
        fact_id
        for fact_id, fact in arg.facts.items()
        if fact.metadata.get("control_role") == "condition"
    }
