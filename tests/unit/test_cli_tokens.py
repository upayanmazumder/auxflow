"""Phase 2 acceptance (sub-issue #22): `auxflow tokens FILE` runs and prints
the token stream."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli
from auxflow.lexer import tokenize

_SOURCE = "\\section{Intro}"


def test_tokens_command_prints_one_line_per_token(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "doc.tex"
    doc.write_text(_SOURCE)

    exit_code = cli.main(["tokens", str(doc)])

    assert exit_code == 0
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    expected = tokenize(_SOURCE, file_id=str(doc))
    assert len(lines) == len(expected)
    assert lines[0] == "1:1 CONTROL_SEQUENCE '\\\\section'"
    assert lines[1] == "1:9 BEGIN_GROUP '{'"
