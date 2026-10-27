"""Query the published AuxFlow release and upgrade the current Python environment."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import suppress
from importlib import metadata
from pathlib import Path
from urllib.request import Request, urlopen

PYPI_URL = "https://pypi.org/pypi/auxflow/json"
_RELEASE = re.compile(r"(\d+)\.(\d+)\.(\d+)\Z")
_CHECK_INTERVAL = 24 * 60 * 60
_INSTALLED = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?((?:\.dev\d+|rc\d+)?(?:\+[\w.]+)?)\Z")


def latest_version() -> str:
    """Fetch the current published version over HTTPS, not a cached value."""
    request = Request(PYPI_URL, headers={"Accept": "application/json"})
    with urlopen(request, timeout=4) as response:
        version = json.load(response)["info"]["version"]
    if not isinstance(version, str) or not _RELEASE.fullmatch(version):
        raise ValueError("PyPI returned an invalid stable release version")
    return version


def is_newer(latest: str, installed: str) -> bool:
    """Compare the project's stable three-part releases without another dependency."""
    published = _RELEASE.fullmatch(latest)
    current = _INSTALLED.fullmatch(installed)
    if published is None or current is None:
        raise ValueError(f"cannot compare installed version {installed!r} with PyPI")
    published_parts = tuple(int(part) for part in published.groups())
    current_parts = (int(current.group(1)), int(current.group(2)), int(current.group(3) or 0))
    return published_parts > current_parts or (
        published_parts == current_parts and current.group(4).startswith((".dev", "rc"))
    )


def is_editable() -> bool:
    """Never replace an editable checkout through the application itself."""
    direct_url = metadata.distribution("auxflow").read_text("direct_url.json")
    if direct_url is None:
        return False
    return json.loads(direct_url).get("dir_info", {}).get("editable") is True


def install(version: str) -> int:
    """Upgrade only AuxFlow in the interpreter that launched this command."""
    if not _RELEASE.fullmatch(version):
        raise ValueError("invalid release version")
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", f"auxflow=={version}"],
        check=False,
    ).returncode


def _cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME")
    return (Path(base) if base else Path.home() / ".cache") / "auxflow" / "updates.json"


def _read_cache(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_cache(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".updates-", delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _refresh(path: Path) -> None:
    try:
        latest = latest_version()
    except (OSError, ValueError, KeyError, TypeError):
        latest = None
    data = _read_cache(path)
    data["checked_at"] = time.time()
    if latest is not None:
        data["latest"] = latest
    with suppress(OSError):
        _write_cache(path, data)


def notify_and_check(installed: str) -> threading.Thread | None:
    """Show a cached notice and start a best-effort check without waiting for the network."""
    if os.environ.get("AUXFLOW_NO_UPDATE_CHECK") or _INSTALLED.fullmatch(installed) is None:
        return None
    path = _cache_path()
    data = _read_cache(path)
    latest = data.get("latest")
    if (
        isinstance(latest, str)
        and _RELEASE.fullmatch(latest)
        and is_newer(latest, installed)
        and data.get("notified") != latest
    ):
        print(
            f"AuxFlow {latest} is available (installed: {installed}). Run 'auxflow update'.",
            file=sys.stderr,
        )
        data["notified"] = latest
        with suppress(OSError):
            _write_cache(path, data)
    checked = data.get("checked_at")
    if isinstance(checked, (int, float)) and 0 <= time.time() - checked < _CHECK_INTERVAL:
        return None
    worker = threading.Thread(
        target=_refresh, args=(path,), name="auxflow-update-check", daemon=True
    )
    worker.start()
    return worker


def cached_latest() -> str | None:
    """The newest release seen by an earlier check, or `None`. This never uses the network."""
    latest = _read_cache(_cache_path()).get("latest")
    return latest if isinstance(latest, str) and _RELEASE.fullmatch(latest) else None
