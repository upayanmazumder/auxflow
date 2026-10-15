"""Symbol tables for the document forest.

Declarations and uses remain separate until the resolution pass. Each table
owns its entries and exposes typed insert and lookup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from auxflow.parser.nodes import Node
from auxflow.parser.spans import Span


@dataclass
class LabelEntry:
    node: Node
    counter_kind: str
    file_id: str
    span: Span
    duplicate: bool = False
    duplicate_spans: list[Span] = field(default_factory=list)


@dataclass
class LabelTable:
    entries: dict[str, LabelEntry] = field(default_factory=dict)

    def insert(self, key: str, node: Node, counter_kind: str, span: Span) -> LabelEntry:
        entry = self.entries.get(key)
        if entry is None:
            entry = LabelEntry(
                node=node, counter_kind=counter_kind, file_id=span.file_id, span=span
            )
            self.entries[key] = entry
        else:
            entry.duplicate = True
            entry.duplicate_spans.append(span)
        return entry

    def lookup(self, key: str) -> LabelEntry | None:
        return self.entries.get(key)


@dataclass
class RefUse:
    kind: Literal["ref", "pageref"]
    span: Span
    definition: LabelEntry | None = None


@dataclass
class RefTable:
    entries: dict[str, list[RefUse]] = field(default_factory=dict)

    def insert(self, key: str, kind: Literal["ref", "pageref"], span: Span) -> RefUse:
        use = RefUse(kind=kind, span=span)
        self.entries.setdefault(key, []).append(use)
        return use

    def lookup(self, key: str) -> list[RefUse]:
        return self.entries.get(key, [])


@dataclass
class CiteEntry:
    present: bool
    spans: list[Span] = field(default_factory=list)


@dataclass
class CiteTable:
    entries: dict[str, CiteEntry] = field(default_factory=dict)

    def insert(self, key: str, span: Span, *, present: bool = False) -> CiteEntry:
        entry = self.entries.setdefault(key, CiteEntry(present=present))
        entry.spans.append(span)
        entry.present |= present
        return entry

    def lookup(self, key: str) -> CiteEntry | None:
        return self.entries.get(key)


@dataclass
class PackageEntry:
    fact_kinds: frozenset[str]
    tool: str | None
    modelled: bool


@dataclass
class PackageTable:
    entries: dict[str, PackageEntry] = field(default_factory=dict)

    def insert(
        self, name: str, fact_kinds: frozenset[str], tool: str | None, *, modelled: bool
    ) -> PackageEntry:
        entry = PackageEntry(fact_kinds=fact_kinds, tool=tool, modelled=modelled)
        self.entries[name] = entry
        return entry

    def lookup(self, name: str) -> PackageEntry | None:
        return self.entries.get(name)


@dataclass
class FileEntry:
    path: str
    includer: str | None
    reachable: bool
    opaque: bool


@dataclass
class FileTable:
    entries: dict[str, FileEntry] = field(default_factory=dict)

    def insert(
        self, file_id: str, path: str, includer: str | None, *, reachable: bool, opaque: bool
    ) -> FileEntry:
        entry = FileEntry(path=path, includer=includer, reachable=reachable, opaque=opaque)
        self.entries[file_id] = entry
        return entry

    def lookup(self, file_id: str) -> FileEntry | None:
        return self.entries.get(file_id)


@dataclass
class CounterEntry:
    definitions: list[Span] = field(default_factory=list)
    reads: list[Span] = field(default_factory=list)
    writes: list[Span] = field(default_factory=list)


@dataclass
class CounterTable:
    entries: dict[str, CounterEntry] = field(default_factory=dict)

    def insert(
        self, name: str, kind: Literal["definition", "read", "write"], span: Span
    ) -> CounterEntry:
        entry = self.entries.setdefault(name, CounterEntry())
        if kind == "definition":
            entry.definitions.append(span)
        elif kind == "read":
            entry.reads.append(span)
        else:
            entry.writes.append(span)
        return entry

    def lookup(self, name: str) -> CounterEntry | None:
        return self.entries.get(name)
