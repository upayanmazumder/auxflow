r"""Phase 5 CLI: deterministic dump of all six symbol tables."""

from __future__ import annotations

from pathlib import Path

import pytest

from auxflow import cli


def test_symbols_command_prints_every_table_and_cross_file_entries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main = tmp_path / "main.tex"
    child = tmp_path / "child.tex"
    main.write_text("\\usepackage{graphicx}\\ref{sec:child}\\cite{paper}\\input{child}")
    child.write_text("\\section{Child}\\label{sec:child}\\newcounter{demo}")

    assert cli.main(["symbols", str(main)]) == 0
    first = capsys.readouterr().out

    assert cli.main(["symbols", str(main)]) == 0
    assert capsys.readouterr().out == first
    for name in (
        "LabelTable",
        "RefTable",
        "CiteTable",
        "PackageTable",
        "FileTable",
        "CounterTable",
    ):
        assert f"{name}:\n" in first
    assert "sec:child:" in first
    assert "paper: present=False" in first
    assert "graphicx: modelled=True" in first
    assert "demo: definitions=" in first
    assert f"includer={main}" in first
    assert "UNRESOLVED" not in first
