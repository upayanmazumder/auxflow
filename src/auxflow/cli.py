"""Command-line entry point.

Subcommand surface is fixed by docs/ARCHITECTURE.md. Every command up to and
including `plan` must run without a TeX engine installed; only `run` executes one.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import asdict, replace
from importlib import metadata
from pathlib import Path
from time import perf_counter

from auxflow import style
from auxflow.analysis.classify import Classification, State, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.report import render
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import StablePass, compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import Forest, build_forest, print_tree
from auxflow.ast.forest import inclusion_edges
from auxflow.ir import ARG, lower, to_dot
from auxflow.lexer import tokenize
from auxflow.parser import Diagnostic, Document, Span, parse
from auxflow.planner.lower import build_plan
from auxflow.planner.model import BuildPlan
from auxflow.planner.serialize import to_json
from auxflow.runtime.execute import ExecReport, execute
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
    "plan",  # phase 12 BuildPlan JSON and explained schedule
    "run",  # phase 13 execute the plan with verification
)


_SUMMARIES = {
    "check": "find undefined references, inclusion cycles, and unmodelled packages",
    "classify": "say whether the document settles, and explain why",
    "plan": "show the build plan (use --explain for a readable schedule)",
    "run": "run the plan with a TeX engine and verify the result",
    "graph": "export the dependency graph as Graphviz DOT",
    "tokens": "print the token stream with source positions",
    "ast": "print the syntax tree of every file",
    "symbols": "print the label, reference, citation, and package tables",
}

_EXAMPLES = {
    "check": "example:\n  auxflow check thesis.tex",
    "classify": "examples:\n  auxflow classify thesis.tex\n  auxflow classify -v thesis.tex",
    "plan": "examples:\n  auxflow plan --explain thesis.tex\n  auxflow plan thesis.tex > plan.json",
    "run": "examples:\n  auxflow run thesis.tex\n  auxflow run --strict thesis.tex",
    "graph": "example:\n  auxflow graph thesis.tex -o thesis.dot",
    "tokens": "example:\n  auxflow tokens thesis.tex",
    "ast": "example:\n  auxflow ast thesis.tex",
    "symbols": "example:\n  auxflow symbols thesis.tex",
}


def _version() -> str:
    try:
        return metadata.version("auxflow")
    except metadata.PackageNotFoundError:
        return "unknown"


def _unreadable(path: str) -> str | None:
    """Why `path` cannot be analysed, or `None` if it can be read as text."""
    target = Path(path)
    if not target.exists():
        return f"cannot read {path!r}: no such file. Check the path."
    if target.is_dir():
        return f"cannot read {path!r}: it is a directory. Give the main .tex file."
    try:
        with target.open(encoding="utf-8") as handle:
            handle.read(4096)
    except UnicodeDecodeError:
        return f"cannot read {path!r}: it is not UTF-8 text."
    except OSError as error:
        return f"cannot read {path!r}: {error.strerror or error}."
    return None


def build_parser() -> argparse.ArgumentParser:
    """Build one subcommand per compiler phase with its documented arguments."""
    parser = argparse.ArgumentParser(
        prog="auxflow",
        description="Static convergence classification for multi-pass document compilation.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    for name in COMMANDS:
        sub = subparsers.add_parser(
            name,
            help=_SUMMARIES[name],
            description=_SUMMARIES[name],
            epilog=_EXAMPLES[name],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        sub.add_argument("file", metavar="FILE", help="the main .tex file")
        if name == "graph":
            sub.add_argument(
                "-o", dest="output", metavar="G.dot", help="write DOT here instead of stdout"
            )
        if name == "classify":
            sub.add_argument(
                "-v", "--verbose", action="store_true", help="list every source location"
            )
            sub.add_argument(
                "--force", action="store_true", help="exit 0 even when the result is AMPLIFYING"
            )
        if name == "plan":
            sub.add_argument(
                "--explain", action="store_true", help="print a readable schedule, not JSON"
            )
        if name in {"plan", "run"}:
            sub.add_argument(
                "--force",
                action="store_true",
                help="plan an AMPLIFYING document anyway, capped at 6 runs",
            )
        if name == "run":
            sub.add_argument(
                "--strict", action="store_true", help="refuse to run UNKNOWN documents"
            )
    helper = subparsers.add_parser(
        "help",
        help="show help for AuxFlow or for one command",
        description="Show an overview of AuxFlow, or the options of one command.",
    )
    helper.add_argument("topic", metavar="COMMAND", nargs="?")
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="colour human-readable output (default: auto, honours NO_COLOR)",
    )
    return parser


_WORKFLOW = ("check", "classify", "plan", "run", "graph", "tokens", "ast", "symbols")


def _overview() -> str:
    """The text for `auxflow help` and for `auxflow` with no command."""

    def heading(text: str) -> str:
        return style.paint(text, "bold")

    width = max(len(name) for name in _WORKFLOW)
    commands = "\n".join(
        f"  {style.paint(name.ljust(width), 'cyan')}  {_SUMMARIES[name]}" for name in _WORKFLOW
    )
    return "\n".join(
        (
            "AuxFlow: static convergence analysis for multi-pass LaTeX builds.",
            "",
            heading("Usage"),
            "  auxflow [--color auto|always|never] COMMAND [OPTIONS] FILE",
            "  auxflow help [COMMAND]",
            "",
            heading("Commands"),
            commands,
            "",
            heading("Typical use"),
            "  auxflow check thesis.tex             look for problems first",
            "  auxflow classify thesis.tex          see whether it settles",
            "  auxflow plan --explain thesis.tex    read the build schedule",
            "  auxflow run thesis.tex               build and verify",
            "",
            heading("Exit status"),
            "  0  success",
            "  1  a problem was found: an error, an AMPLIFYING document without --force,",
            "     or a build that failed or did not settle",
            "  2  wrong command line, or a file that cannot be read",
            "",
            heading("Colour"),
            "  Colour is on for terminals only. Set NO_COLOR=1 or use --color never to turn",
            "  it off. JSON, DOT, token, and AST output is never coloured.",
            "",
            "Run 'auxflow help COMMAND' for the options of one command.",
        )
    )


def _run_help(parser: argparse.ArgumentParser, topic: str | None) -> int:
    if topic is None:
        print(_overview())
        return 0
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction) and topic in action.choices:
            print(action.choices[topic].format_help(), end="")
            return 0
    names = ", ".join((*_WORKFLOW, "help"))
    print(f"auxflow: no command named {topic!r}. Commands: {names}.", file=sys.stderr)
    return 2


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
        line = f"{_span(diagnostic.span)}: {diagnostic.severity}: {diagnostic.message}"
        print(style.style_report(line))
    errors = sum(diagnostic.severity == "error" for diagnostic in diagnostics)
    warnings = len(diagnostics) - errors
    if diagnostics:
        print(f"Found {errors} error(s) and {warnings} warning(s).", file=sys.stderr)
    else:
        print(style.paint("No problems found.", "green", stream=sys.stderr), file=sys.stderr)
    return int(errors > 0)


def _run_graph(path: str, output: str | None) -> int:
    forest, parse_diagnostics = _load_forest(path)
    _print_parse_diagnostics(parse_diagnostics)
    dot = to_dot(lower(forest, resolve(forest, declare(forest))))
    if output:
        Path(output).write_text(dot, encoding="utf-8")
    else:
        print(dot, end="")
    return 0


def _analyze(forest: Forest) -> tuple[ARG, list[tuple[int, ...]], Classification, StablePass]:
    """Run the shared classifier pipeline once for classify and plan."""
    graph = lower(forest, resolve(forest, declare(forest)))
    seeds = seed_facts(graph)
    taint, _ = propagate_taint(graph, seeds)
    graph = insert_structural_edges(graph, taint)
    components = tarjan(graph)
    labels = classify_components(graph, components)
    stable_pass = compute_stable_pass(graph, build_condensation(graph, components), labels)
    return graph, components, classify(graph, components, labels, stable_pass), stable_pass


_MEANING = {
    State.CERTIFIED: (
        "In plain terms: AuxFlow found no feedback loop in the parts of the document it "
        "models. LaTeX should settle after {runs} {noun}."
    ),
    State.BENIGN_CYCLIC: (
        "In plain terms: some references feed each other, but they do not change how much "
        "content the document makes. LaTeX should settle after {runs} {noun}."
    ),
    State.AMPLIFYING: (
        "In plain terms: a value from one pass changes how much content the next pass makes. "
        "The document may keep changing. Break the loop, or use --force to try it under a cap."
    ),
    State.UNKNOWN: (
        "In plain terms: the document uses commands or packages that AuxFlow does not model. "
        "This does not mean it is broken. AuxFlow uses a safe default of three runs and "
        "checks the result at run time. Use -v to list every location."
    ),
}


def _meaning(classification: Classification) -> str:
    runs = classification.predicted_runs
    text = _MEANING[classification.state].format(runs=runs, noun="run" if runs == 1 else "runs")
    return textwrap.fill(text, width=88)


def _run_classify(path: str, *, verbose: bool, force: bool) -> int:
    forest, parse_diagnostics = _load_forest(path)
    _print_parse_diagnostics(parse_diagnostics)
    sources = {file_id: Path(file_id).read_text(encoding="utf-8") for file_id in forest.documents}
    graph, _components, classification, stable_pass = _analyze(forest)
    report = render(graph, sources, classification, stable_pass, verbose=verbose)
    if report is not None:
        print(style.style_report(report), end="")
    print(_meaning(classification))
    return int(classification.state is State.AMPLIFYING and not force)


def _cli_plan(path: str, *, force: bool) -> tuple[BuildPlan, str | None]:
    started = perf_counter()
    forest, parse_diagnostics = _load_forest(path)
    graph, components, classification, stable_pass = _analyze(forest)
    plan = build_plan(
        forest,
        str(Path(path).absolute()),
        graph,
        components,
        classification,
        stable_pass,
        analysis_ms=(perf_counter() - started) * 1000,
        force=force,
    )
    if parse_diagnostics:
        plan = replace(plan, diagnostics=[*parse_diagnostics, *plan.diagnostics])
    diagnosis = None
    if classification.state is State.AMPLIFYING and not force:
        sources = {
            file_id: Path(file_id).read_text(encoding="utf-8") for file_id in forest.documents
        }
        diagnosis = render(graph, sources, classification, stable_pass)
        assert diagnosis is not None
    return plan, diagnosis


def _run_plan(path: str, *, explain: bool, force: bool) -> int:
    plan, diagnosis = _cli_plan(path, force=force)
    if diagnosis is not None:
        print(style.style_report(diagnosis), end="")
        return 1
    if explain:
        print(style.style_report(f"auxflow: {plan.classification} plan"))
        for index, step in enumerate(plan.steps, 1):
            print(f"  {index}. {step.tool} ({step.jobname}): {step.reason}")
    else:
        print(to_json(plan))
    return 0


def _run_summary(report: ExecReport) -> str:
    if report.status == "CONVERGED":
        noun = "run" if report.runs == 1 else "runs"
        text = style.paint(
            f"Done. The document settled after {report.runs} {noun}.", "green", stream=sys.stderr
        )
        if report.prediction_miss is not None:
            miss = report.prediction_miss
            text += (
                f"\nNote: AuxFlow predicted {miss.predicted} but needed {miss.observed}. "
                "This is recorded as a prediction miss."
            )
        return text
    if report.status == "cap_exceeded":
        return style.paint(
            f"Stopped. The document was still changing after {report.runs} runs. "
            "It may not converge.",
            "red",
            stream=sys.stderr,
        )
    return style.paint(f"Stopped. {report.message}", "red", stream=sys.stderr)


def _run_run(path: str, *, force: bool, strict: bool) -> int:
    plan, diagnosis = _cli_plan(path, force=force)
    if diagnosis is not None:
        print(style.style_report(diagnosis), end="")
    report = execute(plan, Path(path).absolute().parent, strict=strict)
    print(json.dumps(asdict(report), sort_keys=True))
    print(_run_summary(report), file=sys.stderr)
    return report.exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    style.configure(args.color)

    if args.command is None:
        print(_overview())
        return 1
    if args.command == "help":
        return _run_help(parser, args.topic)
    problem = _unreadable(args.file)
    if problem is not None:
        print(f"auxflow: {problem}", file=sys.stderr)
        return 2
    try:
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
        if args.command == "classify":
            return _run_classify(args.file, verbose=args.verbose, force=args.force)
        if args.command == "plan":
            return _run_plan(args.file, explain=args.explain, force=args.force)
        if args.command == "run":
            return _run_run(args.file, force=args.force, strict=args.strict)
    except BrokenPipeError:
        return 0
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
