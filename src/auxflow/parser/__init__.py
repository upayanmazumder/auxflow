"""Phase 3: syntax analysis.

Hand-written recursive descent, one token of lookahead, driven by an argument
signature table. Modules: recursive, nodes, spans, diagnostics, signatures.
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
from auxflow.parser.signatures import SIGNATURES, Signature
from auxflow.parser.spans import Span

__all__ = [
    "SIGNATURES",
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
    "Signature",
    "Span",
    "Text",
    "UsePackage",
    "VerbatimBlock",
    "parse",
]
