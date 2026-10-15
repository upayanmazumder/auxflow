"""Phase 3: syntax analysis.

Hand-written recursive descent, one token of lookahead, driven by an argument
signature table. Modules: recursive, nodes, spans, diagnostics.
"""

from __future__ import annotations

from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.nodes import (
    Argument,
    Comment,
    Document,
    DocumentClass,
    Environment,
    Group,
    Include,
    MacroCall,
    Node,
    Preamble,
    Sectioning,
    Text,
    UsePackage,
    VerbatimBlock,
)
from auxflow.parser.recursive import ParseResult, parse
from auxflow.parser.spans import Span

__all__ = [
    "Argument",
    "Comment",
    "Diagnostic",
    "Document",
    "DocumentClass",
    "Environment",
    "Group",
    "Include",
    "MacroCall",
    "Node",
    "ParseResult",
    "Preamble",
    "Sectioning",
    "Span",
    "Text",
    "UsePackage",
    "VerbatimBlock",
    "parse",
]
