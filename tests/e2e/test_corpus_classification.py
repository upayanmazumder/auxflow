"""Exercise the command-line classifier on the table-of-contents corpus document."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli

_CORPUS = Path(__file__).resolve().parents[2] / "bench" / "corpus"


def test_table_of_contents_document_is_not_flagged_as_non_convergent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _CORPUS / "b05_toc" / "main.tex"

    assert cli.main(["classify", str(source)]) == 0
    assert capsys.readouterr().out.startswith("auxflow: CERTIFIED --")
