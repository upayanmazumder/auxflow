r"""Declaration pass records definitions without resolving earlier uses."""

from __future__ import annotations

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare


def _document(source: str, file_id: str):
    return parse(tokenize(source, file_id=file_id), file_id=file_id).document


def test_forward_label_and_duplicate_are_registered_without_binding_references() -> None:
    forest = build_forest(
        {
            "main.tex": _document(
                "\\ref{fig:a}\\begin{figure}\\label{fig:a}\\end{figure}", "main.tex"
            ),
            "chapter.tex": _document("\\label{fig:a}", "chapter.tex"),
        }
    )

    tables = declare(forest)

    label = tables.labels.lookup("fig:a")
    assert label is not None
    assert label.file_id == "main.tex"
    assert label.counter_kind == "figure"
    assert label.duplicate
    assert [span.file_id for span in label.duplicate_spans] == ["chapter.tex"]
    assert tables.refs.entries == {}  # reference resolution is the second pass
    assert tables.files.lookup("main.tex") is not None
    assert tables.files.lookup("chapter.tex") is not None


def test_packages_files_counters_and_section_labels_are_declared() -> None:
    forest = build_forest(
        {
            "main.tex": _document(
                "\\usepackage{graphicx,exotic}\\newcounter{demo}"
                "\\section{Intro}\\label{sec:intro}\\setcounter{demo}{2}"
                "\\input{chapter.tex}",
                "main.tex",
            ),
            "chapter.tex": _document("\\value{demo}", "chapter.tex"),
        }
    )

    tables = declare(forest)

    section = tables.labels.lookup("sec:intro")
    assert section is not None
    assert section.counter_kind == "section"
    graphicx = tables.packages.lookup("graphicx")
    exotic = tables.packages.lookup("exotic")
    included = tables.files.lookup("chapter.tex")
    assert graphicx is not None and graphicx.modelled
    assert exotic is not None and not exotic.modelled
    assert included is not None and included.includer == "main.tex"
    counter = tables.counters.lookup("demo")
    assert counter is not None
    assert len(counter.definitions) == 1
    assert len(counter.writes) == 1
    assert len(counter.reads) == 1
