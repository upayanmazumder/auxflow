"""Command-line entry point.

Subcommand surface is fixed by docs/ARCHITECTURE.md. Every command up to and
including `plan` must run without a TeX engine installed; only `run` executes one.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import shlex
import sys
import textwrap
from dataclasses import asdict, replace
from importlib import metadata
from pathlib import Path
from time import perf_counter
from typing import NoReturn

from auxflow import completion, style
from auxflow.analysis.classify import Classification, State, classify
from auxflow.analysis.classify_cycles import classify_components
from auxflow.analysis.condensation import build_condensation
from auxflow.analysis.report import render
from auxflow.analysis.scc import tarjan
from auxflow.analysis.stable_pass import StablePass, compute_stable_pass
from auxflow.analysis.taint import insert_structural_edges, propagate_taint, seed_facts
from auxflow.ast import Forest, build_forest, print_tree
from auxflow.ast.forest import inclusion_edges
from auxflow.display import Locator, display_path
from auxflow.ir import ARG, lower, to_dot
from auxflow.ir.model import Fact
from auxflow.lexer import tokenize
from auxflow.parser import Diagnostic, Document, parse
from auxflow.planner.lower import build_plan
from auxflow.planner.model import BuildPlan
from auxflow.planner.serialize import to_json
from auxflow.runtime import doctor, update
from auxflow.runtime.execute import DEFAULT_TOOL_TIMEOUT, ExecReport, execute
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
    "completion": "print a tab-completion script for bash, zsh, or fish",
    "info": "print version, platform, installation, and project links",
    "update": "check for a newer release or upgrade this installation",
    "doctor": "check that TeX tools are installed and show how AuxFlow is set up",
}

_COMPLETION_INSTALL = """install:
  bash   eval "$(auxflow completion bash)"
  zsh    eval "$(auxflow completion zsh)"
  fish   auxflow completion fish | source

to keep it, add that line to ~/.bashrc, ~/.zshrc, or ~/.config/fish/config.fish.
Or save the script where your shell loads completions, for example:
  auxflow completion fish > ~/.config/fish/completions/auxflow.fish"""

_EXAMPLES = {
    "check": "example:\n  auxflow check thesis.tex",
    "classify": "examples:\n  auxflow classify thesis.tex\n  auxflow classify -v thesis.tex",
    "plan": "examples:\n  auxflow plan --explain thesis.tex\n  auxflow plan thesis.tex > plan.json",
    "run": "examples:\n  auxflow run thesis.tex\n  auxflow run --strict thesis.tex",
    "graph": "example:\n  auxflow graph thesis.tex -o thesis.dot",
    "tokens": "example:\n  auxflow tokens thesis.tex",
    "ast": "example:\n  auxflow ast thesis.tex",
    "symbols": "example:\n  auxflow symbols thesis.tex",
    "info": "example:\n  auxflow info\n  auxflow info --json",
    "update": "examples:\n  auxflow update --check\n  auxflow update",
    "doctor": "example:\n  auxflow doctor\n  auxflow doctor --json",
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


def _positive_timeout(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a positive number of seconds") from error
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive number of seconds")
    return seconds


class _FriendlyParser(argparse.ArgumentParser):
    """An argument parser that suggests the nearest command for a mistyped one."""

    def error(self, message: str) -> NoReturn:
        match = re.search(r"argument COMMAND: invalid choice: '([^']*)'", message)
        if match is None:
            super().error(message)
        word = match.group(1)
        commands: list[str] = []
        for action in self._actions:
            if isinstance(action, argparse._SubParsersAction):
                commands.extend(action.choices)
        lines = [f"{self.prog}: error: unknown command {word!r}."]
        guess = difflib.get_close_matches(word, commands, n=1)
        if guess:
            lines[0] += f" Did you mean {guess[0]!r}?"
        lines.append(f"Run '{self.prog} help' to list the commands.")
        self.exit(2, "\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Build one subcommand per compiler phase with its documented arguments."""
    parser = _FriendlyParser(
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
        if name == "check":
            sub.add_argument("--json", action="store_true", help="print the result as JSON")
        if name == "classify":
            sub.add_argument(
                "-v", "--verbose", action="store_true", help="list every source location"
            )
            sub.add_argument(
                "--force", action="store_true", help="exit 0 even when the result is AMPLIFYING"
            )
            sub.add_argument("--json", action="store_true", help="print the result as JSON")
        if name == "plan":
            output = sub.add_mutually_exclusive_group()
            output.add_argument(
                "--explain", action="store_true", help="print a readable schedule, not JSON"
            )
            output.add_argument(
                "--json",
                action="store_true",
                help="always print the plan as JSON, even when the plan is refused",
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
            sub.add_argument(
                "--timeout",
                type=_positive_timeout,
                default=DEFAULT_TOOL_TIMEOUT,
                metavar="SECONDS",
                help="limit each TeX tool run (default: 600 seconds)",
            )
    helper = subparsers.add_parser(
        "help",
        help="show help for AuxFlow or for one command",
        description="Show an overview of AuxFlow, or the options of one command.",
    )
    helper.add_argument("topic", metavar="COMMAND", nargs="?")
    finisher = subparsers.add_parser(
        "completion",
        help=_SUMMARIES["completion"],
        description=_SUMMARIES["completion"],
        epilog=_COMPLETION_INSTALL,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    finisher.add_argument("shell", choices=completion.SHELLS, help="the shell to generate for")
    info_parser = subparsers.add_parser(
        "info",
        help=_SUMMARIES["info"],
        description="Show AuxFlow version, runtime environment, and project URLs.",
        epilog=_EXAMPLES["info"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    info_parser.add_argument("--json", action="store_true", help="output machine-readable JSON")
    update_parser = subparsers.add_parser(
        "update",
        help=_SUMMARIES["update"],
        description="Check PyPI for a release and optionally upgrade this installation.",
        epilog=_EXAMPLES["update"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    update_parser.add_argument(
        "--check", action="store_true", help="check for a newer version without installing"
    )
    doctor_parser = subparsers.add_parser(
        "doctor",
        help=_SUMMARIES["doctor"],
        description="Check for the TeX tools AuxFlow needs and show the installation.",
        epilog=_EXAMPLES["doctor"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    doctor_parser.add_argument("--json", action="store_true", help="output machine-readable JSON")
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="colour human-readable output (default: auto, honours NO_COLOR)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="hide progress, hints, and update notices (results and errors still print)",
    )
    return parser


_WORKFLOW = (
    "check",
    "classify",
    "plan",
    "run",
    "graph",
    "tokens",
    "ast",
    "symbols",
    "completion",
    "info",
    "update",
    "doctor",
)


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
            "  auxflow [--color auto|always|never] [--quiet] COMMAND [OPTIONS] FILE",
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
            "  auxflow doctor                       check that TeX is installed",
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
            heading("Quiet"),
            "  --quiet hides progress, next-step hints, and update notices. Results and",
            "  errors still print, so scripts can rely on the output and the exit status.",
            "",
            "Run 'auxflow help COMMAND' for the options of one command.",
            "Documentation: https://auxflow.upayan.dev",
            "Repository:    https://github.com/upayanmazumder/auxflow",
            "PyPI Package:  https://pypi.org/project/auxflow/",
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


def _run_info(*, as_json: bool = False) -> int:
    import platform

    version = _version()
    data = {
        "version": version,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "links": {
            "documentation": "https://auxflow.upayan.dev",
            "changelog": "https://auxflow.upayan.dev/changelog.html",
            "repository": "https://github.com/upayanmazumder/auxflow",
            "issues": "https://github.com/upayanmazumder/auxflow/issues",
            "pypi": "https://pypi.org/project/auxflow/",
        },
    }
    if as_json:
        print(json.dumps(data, indent=2))
        return 0

    def heading(text: str) -> str:
        return style.paint(text, "bold")

    lines = [
        f"{style.paint('AuxFlow', 'cyan', 'bold')} {version}",
        "",
        heading("Environment"),
        f"  Python:      {data['python']} ({data['platform']})",
        f"  Binary:      {data['executable']}",
        "",
        heading("Links"),
        "  Docs:        https://auxflow.upayan.dev",
        "  Changelog:   https://auxflow.upayan.dev/changelog.html",
        "  Repository:  https://github.com/upayanmazumder/auxflow",
        "  Issues:      https://github.com/upayanmazumder/auxflow/issues",
        "  PyPI:        https://pypi.org/project/auxflow/",
    ]
    print("\n".join(lines))
    return 0


def _run_update(*, check_only: bool) -> int:
    installed = _version()
    try:
        latest = update.latest_version()
        newer = update.is_newer(latest, installed)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"auxflow: update check failed: {error}", file=sys.stderr)
        return 1
    if not newer:
        print(f"AuxFlow {installed} is current (PyPI: {latest}).")
        return 0
    if check_only:
        print(f"AuxFlow {latest} is available (installed: {installed}).")
        return 0
    try:
        if update.is_editable():
            print(
                "auxflow: editable installation detected. Use your package manager to update.",
                file=sys.stderr,
            )
            return 1
        code = update.install(latest)
    except (OSError, ValueError) as error:
        print(f"auxflow: update failed: {error}", file=sys.stderr)
        return 1
    if code:
        print(f"auxflow: package installer exited with status {code}", file=sys.stderr)
        return 1
    print(f"AuxFlow {latest} installed. Restart AuxFlow to use it.")
    return 0


def _run_doctor(*, as_json: bool) -> int:
    report = doctor.collect(_version())
    if as_json:
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1
    tools = report["tools"]
    updates = report["updates"]
    assert isinstance(tools, list)
    assert isinstance(updates, dict)
    lines = [
        f"{style.paint('AuxFlow', 'cyan', 'bold')} {report['version']} on Python"
        f" {report['python']} ({report['install']} install)",
        "",
        style.paint("TeX tools", "bold"),
    ]
    for tool in tools:
        if tool["found"]:
            lines.append(
                f"  {style.paint('ok', 'green')}       {tool['name']:<10} {tool['path']}"
                f"  ({tool['purpose']})"
            )
        else:
            need = "required" if tool["required"] else "optional"
            colour = "red" if tool["required"] else "yellow"
            lines.append(
                f"  {style.paint('missing', colour)}  {tool['name']:<10} not found ({need},"
                f" {tool['purpose']})"
            )
    lines += ["", style.paint("Updates", "bold")]
    enabled = "on" if updates["enabled"] else "off (AUXFLOW_NO_UPDATE_CHECK is set)"
    lines.append(f"  Automatic checks: {enabled}")
    cached = updates["cached_latest"]
    lines.append(
        f"  Newest release seen: {cached}"
        if cached
        else "  Newest release seen: none yet. Run 'auxflow update --check'."
    )
    lines.append("")
    if report["ok"]:
        lines.append("Ready: AuxFlow can build documents here.")
    else:
        lines.append(
            "Not ready: install a TeX distribution (TeX Live or MiKTeX) to use 'auxflow run'."
            " Every other command works without TeX."
        )
    print("\n".join(lines))
    return 0 if report["ok"] else 1


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


def _print_parse_diagnostics(diagnostics: list[Diagnostic], locator: Locator) -> None:
    for diagnostic in diagnostics:
        print(f"warning: {diagnostic.message} ({locator.at(diagnostic.span)})")


def _run_ast(path: str) -> int:
    forest, diagnostics = _load_forest(path)
    _print_parse_diagnostics(diagnostics, Locator())
    for file_id, document in forest.documents.items():
        print(f"=== {display_path(file_id)} ===")
        print(print_tree(document))
    for cycle in forest.cycles:
        print(f"warning: inclusion cycle: {' -> '.join(display_path(item) for item in cycle)}")
    return 0


def _run_symbols(path: str) -> int:
    forest, diagnostics = _load_forest(path)
    locator = Locator()
    _span = locator.at
    _print_parse_diagnostics(diagnostics, locator)
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


def _run_check(path: str, *, as_json: bool, quiet: bool) -> int:
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
    locator = Locator()
    errors = sum(diagnostic.severity == "error" for diagnostic in diagnostics)
    warnings = len(diagnostics) - errors
    state = _analyze(forest)[2].state.name
    if as_json:
        entries = []
        for diagnostic in diagnostics:
            line, column = locator.line_col(diagnostic.span)
            entries.append(
                {
                    "file": diagnostic.span.file_id,
                    "line": line,
                    "column": column,
                    "severity": diagnostic.severity,
                    "message": diagnostic.message,
                }
            )
        report = {
            "file": str(Path(path).absolute()),
            "ok": errors == 0,
            "errors": errors,
            "warnings": warnings,
            "convergence": state,
            "diagnostics": entries,
        }
        print(json.dumps(report, indent=2))
        return int(errors > 0)
    for diagnostic in diagnostics:
        message = f"{locator.at(diagnostic.span)}: {diagnostic.severity}: {diagnostic.message}"
        print(style.style_report(message))
    if diagnostics:
        print(f"Found {errors} error(s) and {warnings} warning(s).", file=sys.stderr)
    elif not quiet:
        print(style.paint("No problems found.", "green", stream=sys.stderr), file=sys.stderr)
    if not quiet:
        hint = f"Convergence: {state}. Run 'auxflow classify {shlex.quote(path)}' for details."
        print(style.style_report(hint, sys.stderr), file=sys.stderr)
    return int(errors > 0)


def _run_graph(path: str, output: str | None) -> int:
    forest, parse_diagnostics = _load_forest(path)
    _print_parse_diagnostics(parse_diagnostics, Locator())
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


_NEXT_STEP = {
    State.CERTIFIED: "Next: 'auxflow run {file}' builds the document and verifies the result.",
    State.BENIGN_CYCLIC: "Next: 'auxflow run {file}' builds the document and verifies the result.",
    State.AMPLIFYING: (
        "Next: break the loop at the locations above."
        " 'auxflow plan --force {file}' shows the capped plan."
    ),
    State.UNKNOWN: (
        "Next: 'auxflow classify -v {file}' lists every location."
        " 'auxflow run --strict {file}' refuses documents like this."
    ),
}


def _fact_json(fact: Fact, locator: Locator) -> dict[str, object]:
    line, column = locator.line_col(fact.source_location)
    return {
        "kind": fact.kind.name,
        "key": fact.key,
        "file": fact.source_location.file_id,
        "line": line,
        "column": column,
    }


def _classification_json(
    path: str,
    graph: ARG,
    classification: Classification,
    parse_diagnostics: list[Diagnostic],
    locator: Locator,
) -> dict[str, object]:
    opaque = []
    for fact_id in sorted(classification.opaque_fact_ids):
        fact = graph.facts[fact_id]
        item = _fact_json(fact, locator)
        item["reason"] = str(fact.metadata.get("reason", "not modelled"))
        opaque.append(item)
    warnings = []
    for diagnostic in parse_diagnostics:
        line, column = locator.line_col(diagnostic.span)
        warnings.append(
            {
                "file": diagnostic.span.file_id,
                "line": line,
                "column": column,
                "message": diagnostic.message,
            }
        )
    return {
        "file": str(Path(path).absolute()),
        "state": classification.state.name,
        "predicted_runs": classification.predicted_runs,
        "cycle": [
            _fact_json(graph.facts[fact_id], locator)
            for component in classification.amplifying_components
            for fact_id in component
        ],
        "opaque": opaque,
        "parse_warnings": warnings,
    }


def _run_classify(path: str, *, verbose: bool, force: bool, as_json: bool, quiet: bool) -> int:
    forest, parse_diagnostics = _load_forest(path)
    sources = {file_id: Path(file_id).read_text(encoding="utf-8") for file_id in forest.documents}
    locator = Locator(sources)
    graph, _components, classification, stable_pass = _analyze(forest)
    exit_code = int(classification.state is State.AMPLIFYING and not force)
    if as_json:
        data = _classification_json(path, graph, classification, parse_diagnostics, locator)
        print(json.dumps(data, indent=2))
        return exit_code
    _print_parse_diagnostics(parse_diagnostics, locator)
    report = render(graph, sources, classification, stable_pass, verbose=verbose)
    if report is not None:
        print(style.style_report(report), end="")
    print(_meaning(classification))
    if not quiet:
        print(_NEXT_STEP[classification.state].format(file=shlex.quote(path)), file=sys.stderr)
    return exit_code


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


def _warn_if_forced(plan: BuildPlan, force: bool) -> None:
    if force and plan.classification == "AMPLIFYING":
        print(
            f"warning: --force runs an AMPLIFYING document under a cap of {plan.max_runs} passes."
            " The result may not settle.",
            file=sys.stderr,
        )


def _explain_lines(plan: BuildPlan, path: str) -> list[str]:
    engine_total = sum(step.tool == "pdflatex" for step in plan.steps)
    safe_default = {
        "UNKNOWN": "the document uses constructs AuxFlow does not model",
        "BENIGN_CYCLIC": "references feed each other",
        "AMPLIFYING": f"forced run, capped at {plan.max_runs} passes",
    }
    lines = []
    engine_index = 0
    for number, step in enumerate(plan.steps, 1):
        if step.tool == "pdflatex":
            engine_index += 1
            last = engine_index == engine_total
            if plan.classification == "CERTIFIED":
                why = (
                    "last pass. AuxFlow predicts the document settles here."
                    if last
                    else "writes the auxiliary files that later passes read."
                )
            else:
                why = f"safe default pass ({safe_default[plan.classification]})."
            if last:
                why += " Then AuxFlow checks that the auxiliary files stopped changing."
            lines.append(f"  {number}. pdflatex pass {engine_index} of {engine_total}: {why}")
        elif step.tool == "bibtex":
            lines.append(f"  {number}. bibtex: builds the bibliography from the citations.")
        elif step.tool == "makeindex":
            lines.append(f"  {number}. makeindex: builds the index.")
        else:
            lines.append(f"  {number}. {step.tool}: {step.reason}")
    noun = "pass" if engine_total == 1 else "passes"
    lines.append("")
    lines.append(
        f"{engine_total} TeX {noun} planned. Run 'auxflow run {shlex.quote(path)}' to execute it."
    )
    return lines


def _run_plan(path: str, *, explain: bool, force: bool, as_json: bool) -> int:
    plan, diagnosis = _cli_plan(path, force=force)
    _warn_if_forced(plan, force)
    if as_json:
        print(to_json(plan))
        return int(diagnosis is not None)
    if diagnosis is not None:
        print(style.style_report(diagnosis), end="")
        return 1
    if explain:
        print(style.style_report(f"auxflow: {plan.classification} plan"))
        print("\n".join(_explain_lines(plan, path)))
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


def _print_progress(message: str) -> None:
    print(f"auxflow: {message}", file=sys.stderr)


def _run_run(path: str, *, force: bool, strict: bool, timeout: float, quiet: bool) -> int:
    plan, diagnosis = _cli_plan(path, force=force)
    _warn_if_forced(plan, force)
    if diagnosis is not None:
        print(style.style_report(diagnosis), end="")
    report = execute(
        plan,
        Path(path).absolute().parent,
        strict=strict,
        timeout=timeout,
        progress=None if quiet else _print_progress,
    )
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
    if args.command == "completion":
        print(completion.generate(parser, args.shell), end="")
        return 0
    if args.command == "info":
        return _run_info(as_json=args.json)
    if args.command == "update":
        return _run_update(check_only=args.check)
    if args.command == "doctor":
        return _run_doctor(as_json=args.json)
    problem = _unreadable(args.file)
    if problem is not None:
        print(f"auxflow: {problem}", file=sys.stderr)
        return 2
    if argv is None and not args.quiet:
        update.notify_and_check(_version())
    try:
        if args.command == "tokens":
            return _run_tokens(args.file)
        if args.command == "ast":
            return _run_ast(args.file)
        if args.command == "symbols":
            return _run_symbols(args.file)
        if args.command == "check":
            return _run_check(args.file, as_json=args.json, quiet=args.quiet)
        if args.command == "graph":
            return _run_graph(args.file, args.output)
        if args.command == "classify":
            return _run_classify(
                args.file,
                verbose=args.verbose,
                force=args.force,
                as_json=args.json,
                quiet=args.quiet,
            )
        if args.command == "plan":
            return _run_plan(args.file, explain=args.explain, force=args.force, as_json=args.json)
        if args.command == "run":
            return _run_run(
                args.file,
                force=args.force,
                strict=args.strict,
                timeout=args.timeout,
                quiet=args.quiet,
            )
    except BrokenPipeError:
        return 0
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
