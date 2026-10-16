#!/usr/bin/env python3
r"""Print a fingerprint of one document's normalised auxiliary state.

Runs **inside the pinned container** (auxflow is pip-installed there) so the
baseline shell scripts in bench/baselines/ compare exactly the canonical
records auxflow.runtime.normalize defines -- the "share identical
normalisation" requirement in docs/EVALUATION.md. Reuses
auxflow.runtime.execute._observed_state verbatim rather than re-deriving the
aux-include-following logic, so this is never a second implementation to
drift out of sync with the one AuxFlow's own runtime verifier (baseline E)
uses.

Usage: normstate.py DIR JOBNAME
Prints one line: a sha256 hex digest of the sorted canonical-record set.
An absent auxiliary file contributes no records (empty state is a valid,
stable fingerprint), matching docs/RUNTIME-VERIFICATION.md's definition.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from auxflow.runtime.execute import _observed_state


def fingerprint(directory: Path, jobname: str) -> str:
    state = _observed_state(directory, jobname)
    canonical = "\n".join(sorted("\x1f".join(record) for record in state))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: normstate.py DIR JOBNAME", file=sys.stderr)
        return 2
    directory = Path(sys.argv[1])
    jobname = sys.argv[2]
    print(fingerprint(directory, jobname))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
