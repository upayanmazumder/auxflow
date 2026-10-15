r"""Strongly connected components of the ARG via iterative Tarjan.

docs/STATIC-ANALYSIS.md section 3: a recursive implementation exhausts the
interpreter stack on the realistic corpus member, so this uses an explicit
work stack instead of the interpreter's call stack.

Output order is Tarjan's natural emission order: when a component's root
fact closes, every fact reachable from it (via an ARG edge) has already had
its own component emitted. For an edge `u -> v`, this means `v`'s component
is emitted before `u`'s -- the reverse of topological order. This is the
order docs/STATIC-ANALYSIS.md section 3 calls "reverse topological order".
"""

from __future__ import annotations

from collections.abc import Iterator

from auxflow.ir.graph import ARG


def tarjan(arg: ARG) -> list[tuple[int, ...]]:
    """Strongly connected components of `arg`, in reverse topological order.

    Iterative: an explicit work stack simulates the DFS call stack, so a
    long chain of facts (e.g. a corpus document's reference chain) cannot
    raise RecursionError regardless of its length.
    """
    adjacency: dict[int, list[int]] = {fact_id: [] for fact_id in arg.facts}
    for edge in arg.edges:
        adjacency[edge.source].append(edge.destination)

    index_counter = 0
    indices: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    on_tarjan_stack: dict[int, bool] = {}
    tarjan_stack: list[int] = []
    components: list[tuple[int, ...]] = []

    for start in arg.facts:
        if start in indices:
            continue

        # Each work-stack frame is (node, iterator over its unexplored
        # out-edges). Pushing a frame is "entering" a node in the DFS;
        # popping it is "returning" from it.
        work_stack: list[tuple[int, Iterator[int]]] = [(start, iter(adjacency[start]))]
        indices[start] = lowlink[start] = index_counter
        index_counter += 1
        tarjan_stack.append(start)
        on_tarjan_stack[start] = True

        while work_stack:
            node, neighbours = work_stack[-1]
            advanced = False
            for neighbour in neighbours:
                if neighbour not in indices:
                    indices[neighbour] = lowlink[neighbour] = index_counter
                    index_counter += 1
                    tarjan_stack.append(neighbour)
                    on_tarjan_stack[neighbour] = True
                    work_stack.append((neighbour, iter(adjacency[neighbour])))
                    advanced = True
                    break
                if on_tarjan_stack.get(neighbour, False):
                    lowlink[node] = min(lowlink[node], indices[neighbour])
            if advanced:
                continue

            work_stack.pop()
            if lowlink[node] == indices[node]:
                component: list[int] = []
                while True:
                    member = tarjan_stack.pop()
                    on_tarjan_stack[member] = False
                    component.append(member)
                    if member == node:
                        break
                components.append(tuple(component))
            if work_stack:
                parent, _ = work_stack[-1]
                lowlink[parent] = min(lowlink[parent], lowlink[node])

    return components
