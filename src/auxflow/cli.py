"""Command-line entry point.

Subcommand surface is fixed by docs/ARCHITECTURE.md. Every command up to and
including `plan` must run without a TeX engine installed; only `run` executes one.

`tokens` is implemented (phase 2). Every other subcommand is not yet
implemented -- see docs/IMPLEMENTATION-PLAN.md.
"""

from __future__ import annotations

import argparse
import sys

from auxflow.lexer import tokenize

COMMANDS = (
    "tokens",  # phase 2  token stream
    "ast",  # phase 4  pretty-printed AST forest
    "symbols",  # phase 5  symbol table dump
    "check",  # phase 6  semantic diagnostics, non-zero exit on error
    "graph",  # phase 7  ARG as Graphviz DOT
    "classify",  # phase 11 convergence classification with diagnosis
    "plan",  # phase 12 BuildPlan as JSON
    "run",  # phase 13 execute the plan with verification
)


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser and its subcommand stubs.

    Matches the command-line surface table in docs/ARCHITECTURE.md exactly:
    one subcommand per compiler phase, `FILE` positional on every command,
    plus `graph -o` and `plan --explain`. No handler executes real logic yet;
    that is phases 2-13, not phase 1.
    """
    parser = argparse.ArgumentParser(
        prog="auxflow",
        description="Static convergence classification for multi-pass document compilation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    for name in COMMANDS:
        sub = subparsers.add_parser(name)
        sub.add_argument("file", metavar="FILE")
        if name == "graph":
            sub.add_argument("-o", dest="output", metavar="G.dot")
        if name == "plan":
            sub.add_argument("--explain", action="store_true")

    return parser


def _run_tokens(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        source = f.read()
    for token in tokenize(source, file_id=path):
        print(f"{token.line}:{token.col} {token.catcode.name} {token.text!r}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "tokens":
        return _run_tokens(args.file)

    raise NotImplementedError(
        f"auxflow {args.command}: bootstrap phase, see docs/IMPLEMENTATION-PLAN.md"
    )


if __name__ == "__main__":
    sys.exit(main())
