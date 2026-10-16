r"""Syntax-directed lowering from a document forest into instance-level facts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field, replace

from auxflow.ast import Forest
from auxflow.ir.model import Component, DepEdge, DepType, Fact, FactKind
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
from auxflow.parser.spans import Span
from auxflow.semantic.resolve import SymbolTables

_SAFE_BARE = {
    "\\tableofcontents",
    "\\listoffigures",
    "\\listoftables",
    "\\newpage",
    "\\clearpage",
    "\\%",
    "\\Huge",
    "\\small",
}
_KNOWN_CALLS = {
    "\\equal",
    "\\documentclass",
    "\\usepackage",
    "\\pagenumbering",
    "\\input",
    "\\include",
    "\\label",
    "\\ref",
    "\\pageref",
    "\\vref",
    "\\vpageref",
    "\\cite",
    "\\bibliography",
    "\\bibliographystyle",
    "\\caption",
    "\\includegraphics",
    "\\vspace",
    "\\framebox",
    "\\rule",
    "\\newcounter",
    "\\stepcounter",
    "\\setcounter",
    "\\value",
}


@dataclass
class ARG:
    facts: dict[int, Fact] = field(default_factory=dict)
    edges: list[DepEdge] = field(default_factory=list)


class _Builder:
    def __init__(self) -> None:
        self.facts: list[Fact] = []
        self.edges: list[DepEdge] = []
        self.incoming: list[list[int]] = []

    def fact(
        self,
        kind: FactKind,
        key: str | None,
        component: Component,
        span: Span,
        *,
        producer: str = "engine",
        consumer: str | None = None,
        metadata: dict[str, str | int | bool] | None = None,
    ) -> int:
        fact_id = len(self.facts)
        self.facts.append(
            Fact(
                fact_id=fact_id,
                kind=kind,
                key=key,
                component=component,
                producer=producer,
                consumer=consumer,
                source_location=span,
                metadata=metadata or {},
            )
        )
        self.incoming.append([])
        return fact_id

    def edge(self, source: int, destination: int, lag: int, kind: DepType, reason: str) -> None:
        self.edges.append(DepEdge(source, destination, lag, kind, reason))
        self.incoming[destination].append(source)

    def finish(self, *, opaque: bool) -> ARG:
        return ARG(
            facts={
                fact.fact_id: replace(
                    fact, dependencies=tuple(self.incoming[fact.fact_id]), opaque=opaque
                )
                for fact in self.facts
            },
            edges=self.edges,
        )


def _argument_text(call: MacroCall) -> str | None:
    mandatory = next((arg for arg in call.args if arg.kind == "mandatory"), None)
    if mandatory is None or not mandatory.content:
        return None
    if not all(isinstance(node, Text) for node in mandatory.content):
        return None
    return "".join(node.text for node in mandatory.content if isinstance(node, Text))


def _nodes(document: Document) -> Iterator[tuple[Node, str | None, str | None]]:
    """One iterative traversal with environment and control-position context."""
    stack: list[tuple[Node, str | None, str | None]] = [(document, None, None)]
    while stack:
        node, environment, control_role = stack.pop()
        yield node, environment, control_role
        if isinstance(node, Environment):
            environment = node.name if node.name in {"figure", "table"} else environment
            children = node.children
        elif isinstance(node, (Document, Preamble, Group)):
            children = node.children
        elif isinstance(node, Sectioning):
            children = node.title
        elif isinstance(node, ControlConstruct):
            stack.extend((child, environment, "body") for child in reversed(node.else_body))
            stack.extend((child, environment, "body") for child in reversed(node.body))
            stack.extend((child, environment, "condition") for child in reversed(node.condition))
            continue
        elif isinstance(node, MacroCall):
            children = tuple(child for arg in node.args for child in arg.content)
        else:
            continue
        stack.extend((child, environment, control_role) for child in reversed(children))


def lower(forest: Forest, tables: SymbolTables) -> ARG:
    """Create distinct facts for each modelled construct and its dependencies.

    A generated list (`\\tableofcontents`/`\\listoffigures`/`\\listoftables`) or a
    page-emission primitive (`\\newpage`/`\\clearpage`) is what makes pagination
    sensitive to auxiliary state -- see docs/IR.md's "backward reference, no
    generated lists" example, which has neither of these and so has no
    CONTENT_VOLUME fact at all, versus the "amplifying cycle" example, which
    has `\\newpage` but no generated list and still requires CONTENT_VOLUME to
    exist (it is the fact that closes the cycle). Sectioning and `\\caption`
    always write a potential list entry (matching real LaTeX's unconditional
    `\\addcontentsline`), but that entry only affects CONTENT_VOLUME when the
    corresponding list-producing macro is actually present to typeset it.
    """
    builder = _Builder()
    label_numbers: dict[str, int] = {}
    label_pages: dict[str, int] = {}
    pending_refs: list[tuple[str, int, bool]] = []
    cite_uses: list[int] = []
    bibliography: list[int] = []
    list_extents: dict[str, int] = {}
    volume: int | None = None
    opaque = any(entry.opaque for entry in tables.files.entries.values())

    list_gates = {"toc": False, "lof": False, "lot": False}
    _GATE_MACRO = {
        "\\tableofcontents": "toc",
        "\\listoffigures": "lof",
        "\\listoftables": "lot",
    }
    _VOLUME_TRIGGERS = frozenset({*_GATE_MACRO, "\\newpage", "\\clearpage"})
    earliest_trigger_span: Span | None = None
    for document in forest.documents.values():
        for node, _environment, _control_role in _nodes(document):
            if isinstance(node, MacroCall) and node.name in _GATE_MACRO:
                list_gates[_GATE_MACRO[node.name]] = True
            if (
                isinstance(node, MacroCall)
                and node.name in _VOLUME_TRIGGERS
                and (earliest_trigger_span is None or node.span.start < earliest_trigger_span.start)
            ):
                earliest_trigger_span = node.span

    def content_volume(span: Span) -> int:
        nonlocal volume
        if volume is None:
            volume = builder.fact(FactKind.CONTENT_VOLUME, None, "value", span)
        return volume

    if earliest_trigger_span is not None:
        content_volume(earliest_trigger_span)

    def list_extent(kind: str, span: Span) -> int:
        extent = list_extents.get(kind)
        if extent is None:
            extent = builder.fact(FactKind.LIST_EXTENT, kind, "value", span)
            list_extents[kind] = extent
            builder.edge(
                extent,
                content_volume(span),
                1,
                DepType.LAYOUT,
                f"{kind} extent shifts pagination",
            )
        return extent

    def list_entry(
        kind: FactKind, list_kind: str, span: Span, *, source: int | None = None
    ) -> None:
        if not list_gates[list_kind]:
            return
        key = f"{span.file_id}:{span.start}"
        metadata: dict[str, str | int | bool] = {"list_kind": list_kind}
        if source is not None:
            metadata["origin"] = "bibliography"
        exists = builder.fact(kind, key, "exists", span, metadata=metadata)
        builder.edge(
            exists,
            list_extent(list_kind, span),
            0,
            DepType.LAYOUT,
            f"{list_kind} entry adds list content",
        )
        value = builder.fact(kind, key, "value", span, metadata=metadata)
        builder.edge(
            content_volume(span),
            value,
            0,
            DepType.LAYOUT,
            f"pagination sets {list_kind} entry page",
        )
        if source is not None:
            builder.edge(source, exists, 1, DepType.LAYOUT, "bibliography body adds a toc entry")

    for document in forest.documents.values():
        for node, environment, control_role in _nodes(document):
            if isinstance(node, Sectioning):
                list_entry(FactKind.TOC_ENTRY, "toc", node.span)
            elif isinstance(node, (Opaque, MacroDef)):
                if isinstance(node, Opaque) or node.opaque:
                    opaque = True
                    builder.fact(
                        FactKind.OPAQUE,
                        None,
                        "value",
                        node.span,
                        metadata={
                            "reason": (node.reason if isinstance(node, Opaque) else node.name)
                        },
                    )
            elif isinstance(node, UsePackage):
                for name in node.name.split(","):
                    package = tables.packages.lookup(name.strip())
                    if package is not None and not package.modelled:
                        opaque = True
                        builder.fact(
                            FactKind.OPAQUE,
                            name.strip(),
                            "value",
                            node.span,
                            metadata={"reason": "unmodelled package"},
                        )
            elif isinstance(node, CounterOp) and node.op == "value" and control_role:
                builder.fact(
                    FactKind.COUNTER_READ,
                    node.counter,
                    "value",
                    node.span,
                    metadata={"control_role": control_role},
                )
            elif isinstance(node, MacroCall):
                key = _argument_text(node)
                if node.name == "\\label" and key:
                    label = tables.labels.lookup(key)
                    number = builder.fact(
                        FactKind.LABEL_NUMBER,
                        key,
                        "value",
                        node.span,
                        metadata={
                            "counter_kind": (label.counter_kind if label is not None else "unknown")
                        },
                    )
                    page = builder.fact(FactKind.LABEL_PAGE, key, "value", node.span)
                    label_numbers.setdefault(key, number)
                    label_pages.setdefault(key, page)
                elif node.name in {"\\ref", "\\pageref", "\\vref", "\\vpageref"} and key:
                    is_page = node.name in {"\\pageref", "\\vref", "\\vpageref"}
                    use = builder.fact(
                        FactKind.PAGEREF_USE if is_page else FactKind.REF_USE,
                        key,
                        "value",
                        node.span,
                        metadata=({"control_role": control_role} if control_role else None),
                    )
                    pending_refs.append((key, use, is_page))
                elif node.name == "\\caption" and environment in {"figure", "table"}:
                    kind = FactKind.LOF_ENTRY if environment == "figure" else FactKind.LOT_ENTRY
                    list_entry(kind, "lof" if environment == "figure" else "lot", node.span)
                elif node.name == "\\cite" and key:
                    for cite_key in key.split(","):
                        cite_key = cite_key.strip()
                        if cite_key:
                            cite_uses.append(
                                builder.fact(FactKind.CITE_USE, cite_key, "value", node.span)
                            )
                elif node.name == "\\bibliography" and key:
                    exists = builder.fact(FactKind.BBL, key, "exists", node.span, producer="bibtex")
                    builder.fact(FactKind.BBL, key, "value", node.span, producer="bibtex")
                    bibliography.append(exists)
                    list_entry(FactKind.TOC_ENTRY, "toc", node.span, source=exists)
                elif node.name == "\\value" and key and control_role:
                    builder.fact(
                        FactKind.COUNTER_READ,
                        key,
                        "value",
                        node.span,
                        metadata={"control_role": control_role},
                    )
                elif node.name == "\\usepackage" and key:
                    for name in key.split(","):
                        package = tables.packages.lookup(name.strip())
                        if package is not None and not package.modelled:
                            opaque = True
                            builder.fact(
                                FactKind.OPAQUE,
                                name.strip(),
                                "value",
                                node.span,
                                metadata={"reason": "unmodelled package"},
                            )
                elif node.name not in _KNOWN_CALLS and node.name not in _SAFE_BARE:
                    opaque = True
                    builder.fact(
                        FactKind.OPAQUE,
                        node.name,
                        "value",
                        node.span,
                        metadata={"reason": "unsupported control sequence"},
                    )

    if volume is not None:
        # A generated list exists somewhere, so pagination is sensitive to
        # auxiliary state and every label's page component is affected.
        for key, page in label_pages.items():
            builder.edge(
                volume,
                page,
                0,
                DepType.LAYOUT,
                f"pagination sets page of label {key}",
            )
    for key, use, is_page in pending_refs:
        source = (label_pages if is_page else label_numbers).get(key)
        if source is not None:
            builder.edge(
                source,
                use,
                1,
                DepType.AUX_ROUNDTRIP,
                f"{('pageref' if is_page else 'ref')} reads label {key} from a prior run",
            )
    for cite in cite_uses:
        for bbl in bibliography:
            builder.edge(cite, bbl, 1, DepType.TOOL, "bibtex consumes citation keys")
    return builder.finish(opaque=opaque)
