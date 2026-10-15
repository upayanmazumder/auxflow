r"""Render the four classification states as the diagnostic reports
specified in docs/NON-CONVERGENCE.md.

Every element is drawn from fields already in the IR: `Fact.source_location`,
`DepEdge.reason`, `DepEdge.dependency_type`, SCC membership, and per-fact
`stable_pass` (NON-CONVERGENCE.md "Diagnostic data requirements").

Required wording: AuxFlow never prints "cannot converge" or "will not
terminate" -- only "may not converge", with the structural evidence that
prompted it.
"""

from __future__ import annotations

from collections import deque

from auxflow.analysis.classify import Classification, State
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import StablePass
from auxflow.ir.graph import ARG
from auxflow.ir.model import DepEdge, DepType, Fact, FactKind

MAX_RUNS_UNDER_FORCE = 6
"""Matches the documented max_runs example in docs/BUILD-PLANNER.md; the
build planner (phase 12) owns this constant going forward."""


def offset_to_line_col(text: str, offset: int) -> tuple[int, int]:
    """1-indexed `(line, col)` of byte `offset` in `text`, matching the
    lexer's own `Token.line`/`Token.col` convention."""
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    return line, offset - line_start + 1


def _position(sources: dict[str, str], fact: Fact) -> str:
    span = fact.source_location
    line, col = offset_to_line_col(sources[span.file_id], span.start)
    return f"{span.file_id}:{line}:{col}"


def _fact_label(fact: Fact) -> str:
    return f"{fact.kind.name}({fact.key})" if fact.key is not None else fact.kind.name


def _cycle_path(arg: ARG, members: tuple[int, ...], *, prefer: DepType | None = None) -> list[int]:
    """A fact-id path `[f0, f1, ..., fn, f0]` forming a cycle through `members`.

    Starts from the `prefer`-typed edge when one exists (so an AMPLIFYING
    report centres on the STRUCTURAL edge), else any intra-component edge,
    then takes the shortest path back to the start.
    """
    member_set = set(members)
    intra = [e for e in arg.edges if e.source in member_set and e.destination in member_set]
    seed = next((e for e in intra if e.dependency_type is prefer), intra[0])
    if seed.source == seed.destination:
        return [seed.source, seed.source]

    adjacency: dict[int, list[int]] = {}
    for edge in intra:
        adjacency.setdefault(edge.source, []).append(edge.destination)

    queue: deque[list[int]] = deque([[seed.destination]])
    seen = {seed.destination}
    while queue:
        path = queue.popleft()
        for neighbour in adjacency.get(path[-1], ()):
            if neighbour == seed.source:
                return [seed.source, *path, seed.source]
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append([*path, neighbour])
    return [seed.source, seed.destination, seed.source]  # unreachable for a real SCC


def _edge_between(arg: ARG, source: int, destination: int) -> DepEdge | None:
    return next((e for e in arg.edges if e.source == source and e.destination == destination), None)


def render_amplifying(arg: ARG, sources: dict[str, str], classification: Classification) -> str:
    (component,) = classification.amplifying_components
    path = _cycle_path(arg, component, prefer=DepType.STRUCTURAL)
    path_edges = [_edge_between(arg, path[i], path[i + 1]) for i in range(len(path) - 1)]
    structural = next(
        e for e in path_edges if e is not None and e.dependency_type is DepType.STRUCTURAL
    )

    lines = [
        "auxflow: AMPLIFYING CYCLE -- this document may not converge.",
        "",
        "  A cross-reference value influences how much content the document generates,",
        "  which in turn changes that value.",
        "",
        f"  cycle ({len(component)} facts):",
    ]
    for i, fact_id in enumerate(path[:-1]):
        fact = arg.facts[fact_id]
        label = _fact_label(fact)
        position = _position(sources, fact)
        if i == 0:
            lines.append(f"    {label}  {position}")
        else:
            edge = _edge_between(arg, path[i - 1], fact_id)
            assert edge is not None
            reason = (
                f"{edge.dependency_type.name}: {edge.reason}"
                if edge.dependency_type is DepType.STRUCTURAL
                else edge.reason
            )
            lines.append(f"      -> {label}  {position}  {reason}")
    start_fact = arg.facts[path[0]]
    lines.append(f"      -> {_fact_label(start_fact)}  {_position(sources, start_fact)}")

    lines += [
        "",
        "  likely cause:",
        f"    {structural.reason}",
        "",
        "  Under the supported semantics no finite run count is guaranteed to stabilise",
        "  this structure.",
        "",
        f"  No build plan emitted. Use --force to execute under a cap of {MAX_RUNS_UNDER_FORCE}"
        " runs.",
    ]
    return "\n".join(lines) + "\n"


def render_benign(
    arg: ARG, sources: dict[str, str], component: tuple[int, ...], stable_pass: StablePass
) -> str:
    path = _cycle_path(arg, component)
    lines = [f"auxflow: note: benign feedback cycle ({len(component)} facts)", ""]
    for i, fact_id in enumerate(path[:-1]):
        fact = arg.facts[fact_id]
        label = _fact_label(fact)
        position = _position(sources, fact)
        if i == 0:
            lines.append(f"    {label}  {position}")
        else:
            edge = _edge_between(arg, path[i - 1], fact_id)
            assert edge is not None
            lines.append(f"      -> {label}  {position}  {edge.dependency_type.name}")
    lines.append(f"      -> {_fact_label(arg.facts[path[0]])}")

    lines += [
        "",
        "  The number of entries is fixed by document structure, so this loop affects",
        "  recorded values only. Classified BENIGN_CYCLIC.",
    ]
    return "\n".join(lines) + "\n"


def render_unknown(arg: ARG, sources: dict[str, str], classification: Classification) -> str:
    lines = ["auxflow: UNKNOWN -- document contains constructs outside the analysable subset.", ""]
    for fact_id in sorted(classification.opaque_fact_ids):
        fact = arg.facts[fact_id]
        position = _position(sources, fact)
        reason = str(fact.metadata.get("reason", "not modelled"))
        lines.append(f"    {position}   {reason}")

    lines += [
        "",
        "  Facts originating in these files are treated as unknown. Emitting the",
        "  conservative default plan; correctness is delegated to runtime verification.",
    ]
    return "\n".join(lines) + "\n"


_CONSUMER_KINDS = frozenset({FactKind.REF_USE, FactKind.PAGEREF_USE})
"""Must match `auxflow.analysis.stable_pass`'s own consumer exclusion: these
facts are rendered as "consumed on run N", not counted toward P."""


def render_certified(
    arg: ARG, sources: dict[str, str], classification: Classification, stable_pass: StablePass
) -> str:
    n = classification.predicted_runs
    assert n is not None
    p = n - 1
    chain = sorted(
        ((fact_id, value) for fact_id, value in stable_pass.items() if value is not None),
        key=lambda pair: (pair[1], pair[0]),
    )

    lines = [
        f"auxflow: CERTIFIED -- {n} runs",
        "",
        f"  longest dependency chain (stable_pass {p}):",
    ]
    for fact_id, value in chain:
        fact = arg.facts[fact_id]
        label = f"{_fact_label(fact)}  {_position(sources, fact)}"
        if fact.kind in _CONSUMER_KINDS:
            lines.append(f"    {label}  consumed on run {value}")
        else:
            lines.append(f"    {label}  -> {value}")
    lines.append("")
    lines.append(f"  The facts above require all {n} runs to stabilise.")
    return "\n".join(lines) + "\n"


def render(
    arg: ARG,
    sources: dict[str, str],
    classification: Classification,
    stable_pass: StablePass,
    *,
    verbose: bool = False,
) -> str | None:
    """The report block for `classification`, or `None` when nothing should
    be printed at the current verbosity (a benign cycle outside `verbose`)."""
    if classification.state is State.AMPLIFYING:
        return render_amplifying(arg, sources, classification)
    if classification.state is State.UNKNOWN:
        return render_unknown(arg, sources, classification)
    if classification.state is State.BENIGN_CYCLIC:
        if not verbose:
            return None

        for component in tarjan(arg):
            if len(component) > 1:
                return render_benign(arg, sources, component, stable_pass)
        raise AssertionError("BENIGN_CYCLIC classification but no non-trivial component found")
    return render_certified(arg, sources, classification, stable_pass)
