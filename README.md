# AuxFlow

A compiler and static analyzer for LaTeX documents.

[![PyPI](https://img.shields.io/pypi/v/auxflow)](https://pypi.org/project/auxflow/) [![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://pypi.org/project/auxflow/) [![Docs](https://img.shields.io/badge/docs-auxflow.upayan.dev-blue)](https://auxflow.upayan.dev)

AuxFlow checks LaTeX cross-references and citations before the typesetting engine runs.
It builds a dependency graph of all labels and references, detects cyclic loops, and calculates the exact compile passes the document needs.

For complete technical specifications, compiler architecture, and evaluation reports, visit the **[Documentation Website](https://auxflow.upayan.dev)**.

---

## Installation

Install with `pipx` (recommended for command-line tools):

```bash
pipx install auxflow
pipx ensurepath
```

Or install with `pip`:

```bash
pip install --user auxflow
```

The optional [installer script](install.sh) installs the published package and may edit your shell profiles. Inspect it before running it. Do not pipe a network download into a shell.

AuxFlow requires Python 3.12 or newer.

---

## Quick Start

Check a LaTeX document:

```bash
auxflow check document.tex
```

Find the number of required compilation passes:

```bash
auxflow classify document.tex
```

Build the document with automatic runtime checks:

```bash
auxflow run document.tex
```

`auxflow run` starts local TeX tools. Run only documents and packages you trust. It is not a sandbox. Each tool has a 600-second limit by default. Use `auxflow run --timeout 30 document.tex` to change that limit.

Check for a published update without installing it:

```bash
auxflow update --check
```

Run `auxflow update` to install a newer release into the current Python environment.
Editable installations require a manual package-manager update.
Normal commands can show a cached update notice on stderr.
AuxFlow checks PyPI at most daily while a command runs, without waiting for the network.
Short commands may finish before that check completes. No background service remains running.
Set `AUXFLOW_NO_UPDATE_CHECK=1` to disable automatic checks.

Show all commands and options:

```bash
auxflow help
```

Show installation environment and project links:

```bash
auxflow info
```

Check that TeX is installed and see how AuxFlow is set up:

```bash
auxflow doctor
```

`auxflow check`, `auxflow classify`, and `auxflow plan` accept `--json` for editors and CI.
Locations print as `file:line:column`. Paths under the current directory print relative to it.
`auxflow --quiet COMMAND` hides progress, next-step hints, and update notices.
Results and errors still print, so scripts can rely on the output and the exit status.

---

## How It Works

LaTeX documents write labels, tables of contents, and citations to helper files (`.aux`, `.toc`, `.bbl`).
Standard build tools repeat the compile process until these files stop changing.

AuxFlow analyzes your source code directly:

1. **Scans and parses** your LaTeX files into an Abstract Syntax Tree.
2. **Builds a dependency graph** of all references, lists, and citations.
3. **Finds feedback cycles** and calculates whether values affect document length.
4. **Assigns a convergence state**:
   - `CERTIFIED`: Clean document with a fixed pass count.
   - `BENIGN_CYCLIC`: Safe cycles that settle without changing length.
   - `AMPLIFYING`: Loops that cause endless page expansion. Refused by default.
   - `UNKNOWN`: Unrecognized packages or commands. Uses safe default runs.
5. **Creates an optimized build plan** that skips redundant runs and unnecessary tool calls.

---

## Documentation

Full documentation is available at **[auxflow.upayan.dev](https://auxflow.upayan.dev)**:

- **[Technical Reference](https://auxflow.upayan.dev/reference/)**: Architecture, Compiler Pipeline, Intermediate Representation, and Static Analysis.
- **[Project Details](https://auxflow.upayan.dev/project/)**: Formal Specifications, Research Questions, and Literature Review.
- **[Evaluation & Benchmarks](https://auxflow.upayan.dev/evaluation/)**: 15-document Benchmark Corpus, Methodology, and Verification Reports.
- **[Research Paper](https://auxflow.upayan.dev/paper/)**: The paper (PDF). Source and build notes are in [`paper/`](paper/).
- **[Course Reviews](https://auxflow.upayan.dev/reviews/)**: Review Notes, Presentations, and Downloadable Documents.

---

## License

MIT License. See [LICENSE](LICENSE).
