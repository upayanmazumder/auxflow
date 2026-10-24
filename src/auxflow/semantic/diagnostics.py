"""Semantic diagnostics from symbol tables and package declarations."""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import Forest, walk
from auxflow.parser.diagnostics import Diagnostic
from auxflow.parser.nodes import DocumentClass, MacroCall, UsePackage
from auxflow.semantic.package_inventory import local_file, requirements
from auxflow.semantic.resolve import SymbolTables, _argument_text

# Avoid a warning on every ordinary document with a system-supplied base class.
# This does not model or inspect their effects; a local override is still reported.
_STANDARD_CLASSES = frozenset({"article", "report", "book"})


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
    """Warn about unmodelled direct packages and literal local class requirements."""
    diagnostics: list[Diagnostic] = []
    seen_requirements: set[str] = set()
    scanned_files: set[Path] = set()

    def scan_requirements(path: Path, root: Path, provenance: tuple[str, ...]) -> None:
        if path in scanned_files:
            return
        scanned_files.add(path)
        for name, span in requirements(path):
            if name not in seen_requirements:
                seen_requirements.add(name)
                chain = " -> ".join(repr(part) for part in provenance)
                diagnostics.append(
                    Diagnostic(
                        span,
                        f"unmodelled package: {name!r} (required by {chain})",
                        severity="warning",
                    )
                )
            style = local_file(name, ".sty", path, root)
            if style is not None:
                scan_requirements(style, root, (*provenance, style.name))

    for file_id, document in forest.documents.items():
        root = Path(file_id)
        for node in walk(document):
            if isinstance(node, DocumentClass):
                class_name = node.name
            elif isinstance(node, MacroCall) and node.name == "\\documentclass":
                class_name = _argument_text(node) or ""
            else:
                continue
            if not class_name or not class_name.strip():
                continue
            class_name = class_name.strip()
            class_file = local_file(class_name, ".cls", root, root)
            if class_file is None and class_name in _STANDARD_CLASSES:
                continue
            provenance = (
                f"local file: {str(class_file)!r}"
                if class_file is not None
                else "no local .cls file found; external class not inspected"
            )
            diagnostics.append(
                Diagnostic(
                    node.span,
                    f"unmodelled class: {class_name!r} ({provenance})",
                    severity="warning",
                )
            )
            if class_file is not None:
                scan_requirements(class_file, root, (class_file.name,))
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
