# AuxFlow

A compiler and static analyzer for LaTeX documents.

[![PyPI](https://img.shields.io/pypi/v/auxflow)](https://pypi.org/project/auxflow/) [![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://pypi.org/project/auxflow/) [![Docs](https://img.shields.io/badge/docs-auxflow.upayan.dev-blue)](https://auxflow.upayan.dev)

AuxFlow checks LaTeX cross-references and citations before the typesetting engine runs.
It builds a dependency graph of all labels and references, detects cyclic loops, and calculates the exact compile passes the document needs.

For complete technical specifications, compiler architecture, and evaluation reports, visit the **[Documentation Website](https://auxflow.upayan.dev)**.

---

## Installation

Install using `pipx` (recommended):

```bash
pipx install auxflow
```

Or install with `pip`:

```bash
pip install auxflow
```

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

Show all commands and options:

```bash
auxflow help
```

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
- **[Course Reviews](https://auxflow.upayan.dev/reviews/)**: Review Notes, Presentations, and Downloadable Documents.

---

## License

MIT License. See [LICENSE](LICENSE).
