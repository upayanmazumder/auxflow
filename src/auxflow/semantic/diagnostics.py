"""Semantic diagnostics from symbol tables and package declarations."""

from __future__ import annotations

from auxflow.ast import Forest, walk
from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.nodes import MacroCall, UsePackage
from auxflow.semantic.resolve import SymbolTables, _argument_text


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


def check_packages(forest: Forest, tables: SymbolTables) -> list[Diagnostic]:
    """Warn at each unmodelled package declaration."""
    diagnostics: list[Diagnostic] = []
    for document in forest.documents.values():
        for node in walk(document):
            if isinstance(node, UsePackage):
                names = node.name
            elif isinstance(node, MacroCall) and node.name == "\\usepackage":
                names = _argument_text(node) or ""
            else:
                continue
            for name in names.split(","):
                name = name.strip()
                package = tables.packages.lookup(name)
                if package is not None and not package.modelled:
                    diagnostics.append(
                        Diagnostic(node.span, f"unmodelled package: {name!r}", severity="warning")
                    )
    return diagnostics
