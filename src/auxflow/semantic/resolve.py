r"""Two-pass symbol resolution over the parsed document forest.

The declaration pass records definitions across all files. The second pass
binds references and citations after every declaration is available.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from auxflow.ast import Forest, walk
from auxflow.parser.nodes import (
    ControlConstruct,
    CounterOp,
    Document,
    Environment,
    Group,
    MacroCall,
    MacroDef,
    Node,
    Opaque,
    Preamble,
    Sectioning,
    Text,
    UsePackage,
)
from auxflow.semantic.tables import (
    CiteTable,
    CounterTable,
    FileTable,
    LabelTable,
    PackageTable,
    RefTable,
)

_COUNTER_KINDS: dict[str, Literal["definition", "read", "write"]] = {
    "newcounter": "definition",
    "setcounter": "write",
    "value": "read",
}

_BIB_ENTRY = re.compile(r"(?m)^[ \t]*@([A-Za-z]+)\s*[({]\s*([^,\s]+)\s*,")


@dataclass
class SymbolTables:
    labels: LabelTable = field(default_factory=LabelTable)
    refs: RefTable = field(default_factory=RefTable)
    cites: CiteTable = field(default_factory=CiteTable)
    packages: PackageTable = field(default_factory=PackageTable)
    files: FileTable = field(default_factory=FileTable)
    counters: CounterTable = field(default_factory=CounterTable)


def _argument_text(call: MacroCall, index: int = 0) -> str | None:
    mandatory = [arg for arg in call.args if arg.kind == "mandatory"]
    if len(mandatory) <= index:
        return None
    nodes = mandatory[index].content
    if not nodes or not all(isinstance(node, Text) for node in nodes):
        return None
    return "".join(node.text for node in nodes if isinstance(node, Text))


def _record_package(tables: SymbolTables, names: str) -> None:
    for name in names.split(","):
        name = name.strip()
        if name:
            # These package calls have narrowly modelled reference syntax.
            # Their effects on typeset extent remain outside the ARG.
            tables.packages.insert(
                name, frozenset(), None, modelled=name in {"graphicx", "varioref", "ifthen"}
            )


def _declare_node(node: Node, tables: SymbolTables, counter_kind: str) -> str:
    if isinstance(node, Sectioning):
        for child in node.title:
            _declare_node(child, tables, node.level)
        return node.level
    if isinstance(node, Environment):
        inner_kind = node.name if node.name in {"figure", "table"} else counter_kind
        _declare_children(node.children, tables, inner_kind)
        return counter_kind
    if isinstance(node, (Document, Preamble, Group)):
        return _declare_children(node.children, tables, counter_kind)
    if isinstance(node, ControlConstruct):
        _declare_children(node.condition, tables, counter_kind)
        _declare_children(node.body, tables, counter_kind)
        _declare_children(node.else_body, tables, counter_kind)
    if isinstance(node, UsePackage):
        _record_package(tables, node.name)
    if isinstance(node, CounterOp):
        tables.counters.insert(node.counter, _COUNTER_KINDS[node.op], node.span)
    if isinstance(node, MacroCall):
        key = _argument_text(node)
        if key:
            if node.name == "\\label":
                tables.labels.insert(key, node, counter_kind, node.span)
            elif node.name == "\\usepackage":
                _record_package(tables, key)
            elif node.name in {"\\newcounter", "\\setcounter", "\\value"}:
                tables.counters.insert(key, _COUNTER_KINDS[node.name[1:]], node.span)
        for arg in node.args:
            _declare_children(arg.content, tables, counter_kind)
    return counter_kind


def _declare_children(nodes: tuple[Node, ...], tables: SymbolTables, kind: str) -> str:
    for node in nodes:
        kind = _declare_node(node, tables, kind)
    return kind


def declare(forest: Forest) -> SymbolTables:
    """Record declarations across all files; do not bind uses yet."""
    tables = SymbolTables()
    for file_id, document in forest.documents.items():
        tables.files.insert(
            file_id,
            path=file_id,
            includer=forest.includer_of(file_id),
            reachable=True,
            opaque=any(
                isinstance(node, Opaque) or (isinstance(node, MacroDef) and node.opaque)
                for node in walk(document)
            ),
        )
        _declare_node(document, tables, "unknown")
    return tables


def resolve(forest: Forest, tables: SymbolTables) -> SymbolTables:
    """Bind uses across files and mark cited keys found in bibliography databases."""
    databases: set[Path] = set()
    for document in forest.documents.values():
        for node in walk(document):
            if not isinstance(node, MacroCall):
                continue
            key = _argument_text(node)
            if not key:
                continue
            if node.name in {"\\ref", "\\pageref", "\\vref", "\\vpageref"}:
                kind: Literal["ref", "pageref"] = (
                    "pageref" if node.name in {"\\pageref", "\\vref", "\\vpageref"} else "ref"
                )
                use = tables.refs.insert(key, kind, node.span)
                use.definition = tables.labels.lookup(key)
            elif node.name == "\\cite":
                for cite_key in key.split(","):
                    cite_key = cite_key.strip()
                    if cite_key:
                        tables.cites.insert(cite_key, node.span)
            elif node.name == "\\bibliography":
                for name in key.split(","):
                    name = name.strip()
                    if name:
                        filename = name if Path(name).suffix else f"{name}.bib"
                        databases.add(Path(node.span.file_id).parent / filename)
    if not tables.cites.entries:
        return tables
    for database in databases:
        if not database.is_file():
            continue
        for entry_type, key in _BIB_ENTRY.findall(database.read_text(encoding="utf-8")):
            if entry_type.lower() not in {"comment", "preamble", "string"}:
                citation = tables.cites.lookup(key)
                if citation is not None:
                    citation.present = True
    return tables
