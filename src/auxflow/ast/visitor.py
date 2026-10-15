"""Visitor-pattern traversal over the AST.

Mirrors Python's own `ast.NodeVisitor`: `visit(node)` dispatches to
`visit_<ClassName>(node)` if the subclass defines one, else `generic_visit`,
which recurses into every `Node`-valued field, every `Node` in a
tuple-valued field, and every `Node` inside a `MacroCall` argument's
content (`Argument` itself is not a `Node`, so it needs explicit handling).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator

from auxflow.parser.nodes import Argument, Node


class NodeVisitor:
    def visit(self, node: Node) -> None:
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        method(node)

    def generic_visit(self, node: Node) -> None:
        for field in dataclasses.fields(node):
            value = getattr(node, field.name)
            if isinstance(value, Node):
                self.visit(value)
            elif isinstance(value, tuple):
                for item in value:
                    if isinstance(item, Node):
                        self.visit(item)
                    elif isinstance(item, Argument):
                        for content_node in item.content:
                            self.visit(content_node)


def walk(node: Node) -> Iterator[Node]:
    """Pre-order DFS over every node reachable from `node`, itself included."""
    yield node
    for field in dataclasses.fields(node):
        value = getattr(node, field.name)
        if isinstance(value, Node):
            yield from walk(value)
        elif isinstance(value, tuple):
            for item in value:
                if isinstance(item, Node):
                    yield from walk(item)
                elif isinstance(item, Argument):
                    for content_node in item.content:
                        yield from walk(content_node)
