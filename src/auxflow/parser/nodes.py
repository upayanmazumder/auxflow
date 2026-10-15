"""AST node kinds. docs/COMPILER-PIPELINE.md section 3.

Every node carries a mandatory `span`. Node kinds beyond those phase 3's
three sub-issues require (`MacroDef`, `CounterOp`, `ControlConstruct`,
`Opaque`) are introduced by later phases when their own sub-issues need
them, not speculatively here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from auxflow.parser.spans import Span


@dataclass(frozen=True)
class Node:
    span: Span


@dataclass(frozen=True)
class Document(Node):
    children: tuple[Node, ...]


@dataclass(frozen=True)
class Preamble(Node):
    children: tuple[Node, ...]


@dataclass(frozen=True)
class DocumentClass(Node):
    name: str
    options: tuple[str, ...]


@dataclass(frozen=True)
class UsePackage(Node):
    name: str
    options: tuple[str, ...]


@dataclass(frozen=True)
class Include(Node):
    kind: Literal["input", "include"]
    target: str


@dataclass(frozen=True)
class Sectioning(Node):
    level: Literal["chapter", "section", "subsection"]
    title: tuple[Node, ...]


@dataclass(frozen=True)
class Environment(Node):
    name: str
    children: tuple[Node, ...]


@dataclass(frozen=True)
class Argument:
    kind: Literal["mandatory", "optional"]
    content: tuple[Node, ...]


@dataclass(frozen=True)
class MacroCall(Node):
    name: str
    args: tuple[Argument, ...]


@dataclass(frozen=True)
class Group(Node):
    children: tuple[Node, ...]


@dataclass(frozen=True)
class Text(Node):
    text: str


@dataclass(frozen=True)
class Comment(Node):
    text: str


@dataclass(frozen=True)
class VerbatimBlock(Node):
    text: str
