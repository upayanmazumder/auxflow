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


def propagate_taint(arg: ARG, seeds: set[int]) -> tuple[set[int], int]:
    """Forward reachability from `seeds` along value-carrying edges.

    docs/STATIC-ANALYSIS.md section 2: "for each edge (f -> g) in ARG with
    g.component == 'value': if g not in taint: taint.add(g); worklist.push(g)".
    `taint` only ever grows (each fact enters the worklist at most once),
    so it is monotonic over the finite powerset lattice of facts and the
    loop terminates even on a cyclic value-edge graph.

    Returns `(taint, push_count)`. `push_count` -- the number of times any
    fact was ever pushed onto the worklist, including the initial seeds --
    is exposed so callers (and tests) can directly verify the
    push-at-most-once invariant: `push_count <= len(arg.facts)`.
    """
    adjacency: dict[int, list[int]] = {fact_id: [] for fact_id in arg.facts}
    for edge in arg.edges:
        adjacency[edge.source].append(edge.destination)

    taint = set(seeds)
    worklist = list(seeds)
    push_count = len(seeds)

    while worklist:
        f = worklist.pop()
        for g in adjacency[f]:
            if arg.facts[g].component != "value":
                continue
            if g not in taint:
                taint.add(g)
                worklist.append(g)
                push_count += 1

    return taint, push_count
