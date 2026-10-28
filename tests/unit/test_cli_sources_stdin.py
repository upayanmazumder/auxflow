"""Editor source snapshots must override disk without changing normal checks."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from auxflow import cli


def _check(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    root: Path,
    sources: dict[str, str],
) -> dict[str, object]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"sources": sources})))
    assert cli.main(["check", "--json", "--sources-stdin", str(root)]) in (0, 1)
    return json.loads(capsys.readouterr().out)


def test_unsaved_root_replaces_disk_and_uses_buffer_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "main.tex"
    root.write_text("\\label{known}\\ref{known}")

    report = _check(monkeypatch, capsys, root, {str(root): "first line\n\\ref{missing}"})

    assert report["errors"] == 1
    assert report["diagnostics"] == [
        {
            "file": str(root),
            "line": 2,
            "column": 1,
            "end_line": 2,
            "end_column": 14,
            "severity": "error",
            "message": "undefined reference: 'missing'",
        }
    ]


def test_unsaved_included_file_replaces_disk_and_reports_its_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "main.tex"
    child = tmp_path / "chapter.tex"
    root.write_text("\\input{chapter}")
    child.write_text("\\label{known}")

    report = _check(monkeypatch, capsys, root, {str(child): "\\ref{missing}"})

    assert report["errors"] == 1
    assert report["diagnostics"][0]["file"] == str(child)
    assert report["diagnostics"][0]["message"] == "undefined reference: 'missing'"

    assert report["diagnostics"][0]["end_line"] == 1
    assert report["diagnostics"][0]["end_column"] == 14


def test_new_unsaved_root_and_child_can_be_analyzed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "main.tex"
    child = tmp_path / "chapter.tex"

    report = _check(
        monkeypatch,
        capsys,
        root,
        {str(root): "\\input{chapter}", str(child): "\\ref{missing}"},
    )

    assert report["errors"] == 1
    assert report["diagnostics"][0]["file"] == str(child)
    assert report["diagnostics"][0]["message"] == "undefined reference: 'missing'"
    assert report["diagnostics"][0]["end_line"] == 1
    assert report["diagnostics"][0]["end_column"] == 14


def test_invalid_source_snapshot_does_not_analyze_stale_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "main.tex"
    root.write_text("\\ref{missing}")
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"sources": {"relative.tex": 5}}'))

    assert cli.main(["check", "--json", "--sources-stdin", str(root)]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "sources" in output.err


@pytest.mark.parametrize(
    "snapshot",
    [
        "not json",
        "[]",
        '{"sources": []}',
        '{"sources": {"relative.tex": "text"}}',
        '{"sources": {"/absolute.tex": 5}}',
    ],
)
def test_invalid_snapshots_never_read_disk(
    snapshot: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "main.tex"
    root.write_text("\\ref{missing}")
    monkeypatch.setattr(sys, "stdin", io.StringIO(snapshot))

    assert cli.main(["check", "--json", "--sources-stdin", str(root)]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err
