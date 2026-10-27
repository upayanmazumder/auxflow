"""Manual update checks and upgrades never depend on the normal command path."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from auxflow import cli
from auxflow.runtime import update


class _Response(io.BytesIO):
    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def test_manual_check_reports_a_newer_stable_release_without_installing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")
    monkeypatch.setattr(
        update,
        "urlopen",
        lambda *_args, **_kwargs: _Response(json.dumps({"info": {"version": "0.3.0"}}).encode()),
    )

    assert cli.main(["update", "--check"]) == 0
    assert "0.3.0" in capsys.readouterr().out


def test_manual_check_reports_network_failure_without_installing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")

    def unavailable(*_args: object, **_kwargs: object) -> None:
        raise OSError("offline")

    monkeypatch.setattr(update, "urlopen", unavailable)

    assert cli.main(["update", "--check"]) == 1
    assert "offline" in capsys.readouterr().err


def test_update_installs_only_the_published_release_in_the_active_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    installed = tmp_path / "install-args.txt"
    python = tmp_path / "python"
    python.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$@\" > '{installed}'\n")
    python.chmod(0o755)
    monkeypatch.setattr(update.sys, "executable", str(python))
    monkeypatch.setattr(update, "is_editable", lambda: False)
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")
    monkeypatch.setattr(
        update,
        "urlopen",
        lambda *_args, **_kwargs: _Response(json.dumps({"info": {"version": "0.3.0"}}).encode()),
    )

    assert cli.main(["update"]) == 0
    assert installed.read_text().splitlines() == [
        "-m",
        "pip",
        "install",
        "--upgrade",
        "auxflow==0.3.0",
    ]
    assert "0.3.0 installed" in capsys.readouterr().out


def test_editable_installation_is_not_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    installed = tmp_path / "install-args.txt"
    python = tmp_path / "python"
    python.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$@\" > '{installed}'\n")
    python.chmod(0o755)
    monkeypatch.setattr(update.sys, "executable", str(python))
    monkeypatch.setattr(update, "is_editable", lambda: True)
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")
    monkeypatch.setattr(
        update,
        "urlopen",
        lambda *_args, **_kwargs: _Response(json.dumps({"info": {"version": "0.3.0"}}).encode()),
    )

    assert cli.main(["update"]) == 1
    assert "editable installation" in capsys.readouterr().err
    assert not installed.exists()


@pytest.mark.parametrize(
    ("installed", "expected"),
    [
        ("0.1.dev115+gb2928a275.d20261027", True),
        ("0.3.0.dev2+gdeadbeef", True),
        ("0.3.0", False),
        ("0.4.0", False),
    ],
)
def test_version_comparison_accepts_hatch_vcs_versions(installed: str, expected: bool) -> None:
    assert update.is_newer("0.3.0", installed) is expected
