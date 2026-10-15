"""Command-line entry point.

Subcommand surface is fixed by docs/ARCHITECTURE.md. Every command up to and
including `plan` must run without a TeX engine installed; only `run` executes one.

`tokens`, `ast`, `symbols`, `check`, and `graph` are implemented. Other
subcommands are not yet implemented; see docs/IMPLEMENTATION-PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from auxflow.ast import Forest, build_forest, print_tree
from auxflow.ast.forest import inclusion_edges
from auxflow.ir import lower, to_dot
from auxflow.lexer import tokenize
from auxflow.parser import Diagnostic, Document, Span, parse
from auxflow.semantic.diagnostics import check_packages, check_symbols
from auxflow.semantic.inclusion import check_inclusions
from auxflow.semantic.resolve import declare, resolve

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
    """Build one subcommand per compiler phase with its documented arguments."""
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


def _load_forest(path: str) -> tuple[Forest, list[Diagnostic]]:
    root = str(Path(path).absolute())
    documents: dict[str, Document] = {}
    diagnostics: list[Diagnostic] = []
    pending = [root]
    while pending:
        file_id = pending.pop()
        if file_id in documents:
            continue
        with open(file_id, encoding="utf-8") as f:
            source = f.read()
        result = parse(tokenize(source, file_id=file_id), file_id=file_id)
        documents[file_id] = result.document
        diagnostics.extend(result.diagnostics)
        for edge in inclusion_edges(file_id, result.document):
            if edge.target not in documents and Path(edge.target).is_file():
                pending.append(edge.target)
    return build_forest(documents), diagnostics


def _print_parse_diagnostics(diagnostics: list[Diagnostic]) -> None:
    for diagnostic in diagnostics:
        span = diagnostic.span
        print(f"warning: {diagnostic.message} ({span.file_id}:{span.start}-{span.end})")


def _run_ast(path: str) -> int:
    forest, diagnostics = _load_forest(path)
    _print_parse_diagnostics(diagnostics)
    for file_id, document in forest.documents.items():
        print(f"=== {file_id} ===")
        print(print_tree(document))
    for cycle in forest.cycles:
        print(f"warning: inclusion cycle: {' -> '.join(cycle)}")
    return 0


def _span(span: Span) -> str:
    return f"{span.file_id}:{span.start}-{span.end}"


def _run_symbols(path: str) -> int:
    forest, diagnostics = _load_forest(path)
    _print_parse_diagnostics(diagnostics)
    tables = resolve(forest, declare(forest))

    print("LabelTable:")
    for key, entry in sorted(tables.labels.entries.items()):
        print(
            f"  {key}: {_span(entry.span)} counter={entry.counter_kind} duplicate={entry.duplicate}"
        )

    print("RefTable:")
    for key, uses in sorted(tables.refs.entries.items()):
        for use in uses:
            definition = _span(use.definition.span) if use.definition else "UNRESOLVED"
            print(f"  {key}: {use.kind} {_span(use.span)} -> {definition}")

    print("CiteTable:")
    for key, citation in sorted(tables.cites.entries.items()):
        spans = ", ".join(_span(span) for span in citation.spans)
        print(f"  {key}: present={citation.present} spans={spans}")

    print("PackageTable:")
    for name, package in sorted(tables.packages.entries.items()):
        facts = ", ".join(sorted(package.fact_kinds)) or "-"
        print(f"  {name}: modelled={package.modelled} facts={facts} tool={package.tool or '-'}")

    print("FileTable:")
    for file_id, file_entry in sorted(tables.files.entries.items()):
        print(
            f"  {file_id}: path={file_entry.path} includer={file_entry.includer or '-'}"
            f" reachable={file_entry.reachable} opaque={file_entry.opaque}"
        )

    print("CounterTable:")
    for name, counter in sorted(tables.counters.entries.items()):
        definitions = ", ".join(_span(span) for span in counter.definitions) or "-"
        reads = ", ".join(_span(span) for span in counter.reads) or "-"
        writes = ", ".join(_span(span) for span in counter.writes) or "-"
        print(f"  {name}: definitions={definitions} reads={reads} writes={writes}")
    return 0


def _run_check(path: str) -> int:
    forest, parse_diagnostics = _load_forest(path)
    tables = resolve(forest, declare(forest))
    diagnostics = [
        *parse_diagnostics,
        *check_symbols(tables),
        *check_inclusions(forest),
        *check_packages(forest, tables),
    ]
    diagnostics.sort(
        key=lambda diagnostic: (
            diagnostic.span.file_id,
            diagnostic.span.start,
            diagnostic.span.end,
            diagnostic.message,
        )
    )
    for diagnostic in diagnostics:
        print(f"{_span(diagnostic.span)}: {diagnostic.severity}: {diagnostic.message}")
    return int(any(diagnostic.severity == "error" for diagnostic in diagnostics))


def _run_graph(path: str, output: str | None) -> int:
    forest, parse_diagnostics = _load_forest(path)
    _print_parse_diagnostics(parse_diagnostics)
    dot = to_dot(lower(forest, resolve(forest, declare(forest))))
    if output:
        Path(output).write_text(dot, encoding="utf-8")
    else:
        print(dot, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "tokens":
        return _run_tokens(args.file)

    if args.command == "ast":
        return _run_ast(args.file)
    if args.command == "symbols":
        return _run_symbols(args.file)
    if args.command == "check":
        return _run_check(args.file)
    if args.command == "graph":
        return _run_graph(args.file, args.output)

    raise NotImplementedError(
        f"auxflow {args.command}: bootstrap phase, see docs/IMPLEMENTATION-PLAN.md"
    )


if __name__ == "__main__":
    sys.exit(main())
