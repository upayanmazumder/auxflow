"""Stage a fresh, cold working copy of one corpus document for one repetition.

Cold per docs/EVALUATION.md: a fresh directory with no auxiliary files,
containing only the document's sources and the shared bibliography/class
files its relative paths expect.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"


def stage(document: str) -> Path:
    """Create a fresh /tmp root containing corpus/{document,shared}/."""
    root = Path(tempfile.mkdtemp(prefix="auxflow-bench-"))
    corpus_dir = root / "corpus"
    corpus_dir.mkdir()
    shutil.copytree(CORPUS_ROOT / document, corpus_dir / document)
    shutil.copytree(CORPUS_ROOT / "shared", corpus_dir / "shared")
    return root


def corpus_members() -> list[str]:
    return sorted(
        p.name
        for p in CORPUS_ROOT.iterdir()
        if p.is_dir() and p.name != "shared" and (p / "main.tex").is_file()
    )
