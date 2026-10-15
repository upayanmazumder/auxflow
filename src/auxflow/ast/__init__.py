"""Phase 4: multi-file forest assembly, traversal, printing, inclusion graph.

Node class definitions live in auxflow.parser.nodes (phase 3 had to define
them to produce its own "one AST per file" output; phase 4 cannot
retroactively supply a phase-3 prerequisite). This package assembles
per-file ASTs into a forest, builds the \\input/\\include dependency graph
with cycle detection, and provides a visitor-pattern traversal and a
deterministic pretty printer over the tree. Modules: visitor, printer.
"""

from __future__ import annotations

from auxflow.ast.printer import print_tree
from auxflow.ast.visitor import NodeVisitor, walk

__all__ = ["NodeVisitor", "print_tree", "walk"]
