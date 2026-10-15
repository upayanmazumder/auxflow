"""AST node kinds. docs/COMPILER-PIPELINE.md section 3.

Every node carries a mandatory `span`, enforced by the dataclass constructor
itself: `Node` and every subclass declare `span: Span` with no default, so
omitting it raises `TypeError` at construction. This is the complete
sixteen-kind list from COMPILER-PIPELINE.md section 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from auxflow.lexer.tokens import Token
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


@dataclass(frozen=True)
class MacroDef(Node):
    name: str
    arity: int
    body_tokens: tuple[Token, ...]
    opaque: bool


@dataclass(frozen=True)
class CounterOp(Node):
    op: Literal["newcounter", "setcounter", "value"]
    counter: str


@dataclass(frozen=True)
class ControlConstruct(Node):
    kind: Literal["forloop", "whiledo"]
    condition: tuple[Node, ...]
    body: tuple[Node, ...]


@dataclass(frozen=True)
class Opaque(Node):
    reason: str
