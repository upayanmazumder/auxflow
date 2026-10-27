"""Update notices use cached results without waiting for network access."""

from __future__ import annotations

import io
import json
import threading
import time
from pathlib import Path

import pytest

from auxflow.runtime import update


class _Response(io.BytesIO):
    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def test_new_release_is_cached_and_announced_on_next_command_without_network_delay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    entered = threading.Event()
    release = threading.Event()

    def delayed(*_args: object, **_kwargs: object) -> _Response:
        entered.set()
        assert release.wait(2)
        return _Response(json.dumps({"info": {"version": "0.3.0"}}).encode())

    monkeypatch.setattr(update, "urlopen", delayed)
    started = time.monotonic()
    worker = update.notify_and_check("0.2.0")
    elapsed = time.monotonic() - started
    assert elapsed < 0.5
    assert worker is not None
    assert entered.wait(1)
    assert capsys.readouterr().err == ""

    release.set()
    worker.join(timeout=2)
    assert not worker.is_alive()
    assert update.notify_and_check("0.2.0") is None
    assert "AuxFlow 0.3.0 is available" in capsys.readouterr().err
    assert update.notify_and_check("0.2.0") is None
    assert capsys.readouterr().err == ""


def test_offline_check_leaves_normal_command_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    def unavailable(*_args: object, **_kwargs: object) -> None:
        raise OSError("offline")

    monkeypatch.setattr(update, "urlopen", unavailable)
    worker = update.notify_and_check("0.2.0")
    assert worker is not None
    worker.join(timeout=2)
    assert not worker.is_alive()
    assert update.notify_and_check("0.2.0") is None
    assert capsys.readouterr().err == ""


def test_console_command_notifies_once_without_changing_command_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from auxflow import cli

    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache = tmp_path / "auxflow" / "updates.json"
    cache.parent.mkdir()
    cache.write_text(json.dumps({"latest": "0.3.0", "checked_at": time.time()}))
    monkeypatch.setattr(cli, "_version", lambda: "0.2.0")
    source = tmp_path / "main.tex"
    source.write_text(r"\label{x}\ref{x}")
    monkeypatch.setattr(update.sys, "argv", ["auxflow", "check", str(source)])

    assert cli.main() == 0
    first = capsys.readouterr()
    assert first.out == ""
    assert "AuxFlow 0.3.0 is available" in first.err
    assert cli.main() == 0
    assert "AuxFlow 0.3.0 is available" not in capsys.readouterr().err
