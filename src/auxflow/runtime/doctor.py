"""Inspect the local environment: which TeX tools exist and how AuxFlow is installed."""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from importlib import metadata

from auxflow.runtime import update


@dataclass(frozen=True)
class ToolCheck:
    name: str
    required: bool
    purpose: str
    path: str | None

    @property
    def found(self) -> bool:
        return self.path is not None


_TOOLS = (
    ("pdflatex", True, "typesets the document"),
    ("bibtex", False, "builds bibliographies"),
    ("makeindex", False, "builds indexes"),
)


def check_tools() -> list[ToolCheck]:
    """Look each TeX tool up on PATH. This never starts a tool."""
    return [
        ToolCheck(name, required, purpose, shutil.which(name)) for name, required, purpose in _TOOLS
    ]


def install_kind() -> str:
    try:
        return "editable" if update.is_editable() else "regular"
    except metadata.PackageNotFoundError:
        return "unknown"


def collect(version: str) -> dict[str, object]:
    """Everything `auxflow doctor` reports, as JSON-ready data. `ok` means a build can run."""
    tools = check_tools()
    return {
        "ok": all(tool.found for tool in tools if tool.required),
        "version": version,
        "python": platform.python_version(),
        "install": install_kind(),
        "tools": [
            {
                "name": tool.name,
                "required": tool.required,
                "found": tool.found,
                "path": tool.path,
                "purpose": tool.purpose,
            }
            for tool in tools
        ],
        "updates": {
            "enabled": not os.environ.get("AUXFLOW_NO_UPDATE_CHECK"),
            "cached_latest": update.cached_latest(),
        },
    }
