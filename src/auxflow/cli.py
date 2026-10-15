"""Command-line entry point.

Subcommand surface is fixed by docs/ARCHITECTURE.md. Every command up to and
including `plan` must run without a TeX engine installed; only `run` executes one.

Not yet implemented -- see docs/IMPLEMENTATION-PLAN.md.
"""

from __future__ import annotations

COMMANDS = (
    "tokens",  # phase 1  token stream
    "ast",  # phase 3  pretty-printed AST forest
    "symbols",  # phase 4  symbol table dump
    "check",  # phase 5  semantic diagnostics, non-zero exit on error
    "graph",  # phase 6  ARG as Graphviz DOT
    "classify",  # phase 10 convergence classification with diagnosis
    "plan",  # phase 12 BuildPlan as JSON
    "run",  # phase 13 execute the plan with verification
)


def main(argv: list[str] | None = None) -> int:
    raise NotImplementedError("bootstrap phase: see docs/IMPLEMENTATION-PLAN.md")
