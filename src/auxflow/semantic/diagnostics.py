"""Name diagnostics from the resolved symbol tables."""

from __future__ import annotations

from auxflow.parser.diagnostics import Diagnostic
from auxflow.semantic.resolve import SymbolTables


def check_symbols(tables: SymbolTables) -> list[Diagnostic]:
    """Report unbound uses and duplicate label declarations with source spans."""
    diagnostics: list[Diagnostic] = []
    for key, uses in tables.refs.entries.items():
        for use in uses:
            if use.definition is None:
                diagnostics.append(Diagnostic(use.span, f"undefined reference: {key!r}"))
    for key, citation in tables.cites.entries.items():
        if not citation.present:
            for span in citation.spans:
                diagnostics.append(Diagnostic(span, f"undefined citation: {key!r}"))
    for key, label in tables.labels.entries.items():
        if label.duplicate:
            diagnostics.append(Diagnostic(label.duplicate_spans[0], f"duplicate label: {key!r}"))
    return diagnostics
