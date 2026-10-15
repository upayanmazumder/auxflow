r"""Resolve uses only after all file declarations are present."""

from __future__ import annotations

from pathlib import Path

from auxflow.ast import build_forest
from auxflow.lexer import tokenize
from auxflow.parser import parse
from auxflow.semantic.resolve import declare, resolve


def _document(source: str, file_id: str):
    return parse(tokenize(source, file_id=file_id), file_id=file_id).document


def test_cross_file_and_forward_references_bind_after_declaration_pass() -> None:
    forest = build_forest(
        {
            "main.tex": _document(
                "\\ref{sec:child}\\pageref{sec:later}\\input{child.tex}\\label{sec:later}",
                "main.tex",
            ),
            "child.tex": _document("\\section{Child}\\label{sec:child}", "child.tex"),
        }
    )

    tables = resolve(forest, declare(forest))

    cross_file = tables.refs.lookup("sec:child")
    forward = tables.refs.lookup("sec:later")
    assert len(cross_file) == len(forward) == 1
    assert cross_file[0].kind == "ref"
    assert cross_file[0].definition is tables.labels.lookup("sec:child")
    assert cross_file[0].definition is not None
    assert cross_file[0].definition.file_id == "child.tex"
    assert forward[0].kind == "pageref"
    assert forward[0].definition is tables.labels.lookup("sec:later")


def test_unresolved_reference_and_citation_keys_remain_visible() -> None:
    forest = build_forest({"main.tex": _document("\\ref{missing}\\cite{one,two}", "main.tex")})

    tables = resolve(forest, declare(forest))

    assert len(tables.refs.lookup("missing")) == 1
    assert tables.refs.lookup("missing")[0].definition is None
    one = tables.cites.lookup("one")
    two = tables.cites.lookup("two")
    assert one is not None and two is not None
    assert not one.present and not two.present
    assert one.spans[0].file_id == two.spans[0].file_id == "main.tex"


def test_bibliography_presence_is_marked_from_declared_database(tmp_path: Path) -> None:
    main = tmp_path / "main.tex"
    database = tmp_path / "refs.bib"
    database.write_text(
        "@article{found,\n  title={One}\n}\n@comment{not-a-citation,\n  text={Ignored}\n}\n"
    )
    forest = build_forest(
        {
            str(main): _document(
                "\\cite{found,missing,not-a-citation}\\bibliography{refs}", str(main)
            )
        }
    )

    tables = resolve(forest, declare(forest))

    found = tables.cites.lookup("found")
    missing = tables.cites.lookup("missing")
    comment = tables.cites.lookup("not-a-citation")
    assert found is not None and found.present
    assert missing is not None and not missing.present
    assert comment is not None and not comment.present
