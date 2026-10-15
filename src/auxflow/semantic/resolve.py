r"""Two-pass symbol resolution over the parsed document forest.

The declaration pass records definitions without inspecting references. The
resolution pass follows in phase 5's next sub-issue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
            # Only graphicx is known here to add no auxiliary facts. Unknown
            # packages stay unmodelled until a package model exists.
            tables.packages.insert(name, frozenset(), None, modelled=name == "graphicx")


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
