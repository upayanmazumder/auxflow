"""Deterministic pretty printer for the AST, built on the visitor traversal.

Every line is `<indent><ClassName>(<identifying fields>) [file:start-end]`.
Output depends only on the tree's contents (no object ids, no dict/set
iteration order), so it is stable across runs -- required for the
golden-style test in sub-issue #27's acceptance.
"""

from __future__ import annotations

from auxflow.ast.visitor import NodeVisitor
from auxflow.parser.nodes import (
    Comment,
    ControlConstruct,
    CounterOp,
    DocumentClass,
    Environment,
    Include,
    MacroCall,
    MacroDef,
    Node,
    Opaque,
    Sectioning,
    Text,
    UsePackage,
    VerbatimBlock,
)


def _span_str(node: Node) -> str:
    return f"[{node.span.file_id}:{node.span.start}-{node.span.end}]"


def _label(node: Node) -> str:
    cls = type(node).__name__
    if isinstance(node, (DocumentClass, UsePackage)):
        return f"{cls}({node.name})"
    if isinstance(node, Include):
        return f"{cls}({node.kind}, {node.target})"
    if isinstance(node, Sectioning):
        return f"{cls}({node.level})"
    if isinstance(node, Environment):
        return f"{cls}({node.name})"
    if isinstance(node, MacroCall):
        return f"{cls}({node.name})"
    if isinstance(node, (Text, Comment, VerbatimBlock)):
        return f"{cls}({node.text!r})"
    if isinstance(node, MacroDef):
        return f"{cls}({node.name}, arity={node.arity}, opaque={node.opaque})"
    if isinstance(node, CounterOp):
        return f"{cls}({node.op}, {node.counter})"
    if isinstance(node, ControlConstruct):
        return f"{cls}({node.kind})"
    if isinstance(node, Opaque):
        return f"{cls}({node.reason!r})"
    return cls  # Document, Preamble, Group, Argument-bearing content: class name alone


class _Printer(NodeVisitor):
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.depth = 0

    def visit(self, node: Node) -> None:
        self.lines.append("  " * self.depth + _label(node) + " " + _span_str(node))
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1


def print_tree(node: Node) -> str:
    printer = _Printer()
    printer.visit(node)
    return "\n".join(printer.lines)
