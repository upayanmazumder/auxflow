"""Phase 5: typed inserts, lookups, and duplicate definition tracking."""

from __future__ import annotations

from auxflow.parser import Document, Span
from auxflow.semantic.tables import (
    CiteTable,
    CounterTable,
    FileTable,
    LabelTable,
    PackageTable,
    RefTable,
)


def test_six_tables_store_distinct_definitions_and_uses() -> None:
    span = Span("main.tex", 4, 16)
    second = Span("chapter.tex", 2, 12)
    node = Document(span=span, children=())

    labels = LabelTable()
    first = labels.insert("fig:one", node, "figure", span)
    assert labels.lookup("fig:one") is first
    assert first.node is node
    assert first.file_id == "main.tex"
    assert first.counter_kind == "figure"
    assert not first.duplicate
    labels.insert("fig:one", Document(span=second, children=()), "table", second)
    assert labels.lookup("fig:one") is first
    assert first.duplicate
    assert first.duplicate_spans == [second]
    assert labels.lookup("absent") is None

    refs = RefTable()
    ref = refs.insert("fig:one", "ref", span)
    page_ref = refs.insert("fig:one", "pageref", second)
    assert refs.lookup("fig:one") == [ref, page_ref]
    assert refs.lookup("absent") == []
    assert ref.definition is None

    cites = CiteTable()
    cites.insert("paper", span)
    cites.insert("paper", second, present=True)
    cited = cites.lookup("paper")
    assert cited is not None
    assert cited.present
    assert cited.spans == [span, second]
    assert cites.lookup("absent") is None

    packages = PackageTable()
    package = packages.insert("hyperref", frozenset({"anchor"}), None, modelled=True)
    assert packages.lookup("hyperref") == package
    assert packages.lookup("absent") is None

    files = FileTable()
    included = files.insert(
        "chapter.tex", "/work/chapter.tex", "main.tex", reachable=True, opaque=False
    )
    assert files.lookup("chapter.tex") == included
    assert files.lookup("absent") is None

    counters = CounterTable()
    counters.insert("figure", "definition", span)
    counters.insert("figure", "read", second)
    counters.insert("figure", "write", span)
    figure = counters.lookup("figure")
    assert figure is not None
    assert figure.definitions == [span]
    assert figure.reads == [second]
    assert figure.writes == [span]
    assert counters.lookup("absent") is None
