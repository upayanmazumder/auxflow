"""Instance-level facts and lagged dependency edges of the ARG."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Literal

from auxflow.parser.spans import Span


class FactKind(Enum):
    LABEL_NUMBER = auto()
    LABEL_PAGE = auto()
    REF_USE = auto()
    PAGEREF_USE = auto()
    TOC_ENTRY = auto()
    LOF_ENTRY = auto()
    LOT_ENTRY = auto()
    LIST_EXTENT = auto()
    CITE_USE = auto()
    BBL = auto()
    INDEX_ENTRY = auto()
    IND = auto()
    COUNTER_READ = auto()
    CONTENT_VOLUME = auto()
    OPAQUE = auto()


Component = Literal["exists", "value"]


@dataclass(frozen=True)
class Fact:
    fact_id: int
    kind: FactKind
    key: str | None
    component: Component
    producer: str
    consumer: str | None
    source_location: Span
    stable_pass: int | None = None
    dependencies: tuple[int, ...] = ()
    opaque: bool = False
    metadata: dict[str, str | int | bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source_location, Span):
            raise TypeError("Fact.source_location must be a Span")


class DepType(Enum):
    AUX_ROUNDTRIP = auto()
    TOOL = auto()
    LAYOUT = auto()
    STRUCTURAL = auto()


@dataclass(frozen=True)
class DepEdge:
    source: int
    destination: int
    pass_lag: int
    dependency_type: DepType
    reason: str
