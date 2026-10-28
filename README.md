# AuxFlow

A compiler and static analyzer for LaTeX documents.

[![PyPI](https://img.shields.io/pypi/v/auxflow)](https://pypi.org/project/auxflow/) [![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://pypi.org/project/auxflow/) [![Docs](https://img.shields.io/badge/docs-auxflow.upayan.dev-blue)](https://auxflow.upayan.dev)

AuxFlow checks LaTeX cross-references and citations before TeX runs.
It models a declared subset, reports reference cycles, and calculates a conservative
pass bound for documents it can certify. `auxflow run` verifies the plan against
auxiliary files written by the engine.

The [documentation website](https://auxflow.upayan.dev) includes the
[package and class list](https://auxflow.upayan.dev/reference/package-support.html)
and the [evaluation limits](https://auxflow.upayan.dev/evaluation/benchmarks.html).

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

## Package and class support

AuxFlow recognizes `graphicx`, `varioref`, and `ifthen` for limited constructs.
It treats `inputenc`, `fontenc`, `ae`, `aecompl`, `lmodern`, `xcolor`,
`parskip`, `geometry`, `setspace`, `multicol`, and `amsmath` as inert for
auxiliary-state analysis. These package names do not imply support for every
command or for their effects on layout. Every other direct package name is
unmodelled and makes classification `UNKNOWN`.

Package names in `\usepackage{geometry,xcolor}` are checked separately. AuxFlow
does not certify TeX Live bundles as a unit. A local class makes classification
`UNKNOWN`. An external class can produce a warning even when classification
does not change. See [Packages and classes](https://auxflow.upayan.dev/reference/package-support.html)
for limits and diagnosis commands.

## Try the tested documents

The [quickstart sources](examples/quickstart/) include a reference, a multi-file
document, an amplifying loop, and a local class. The
[15-document corpus](bench/corpus/) includes ordinary builds and deliberately
non-convergent cases. Keep each document with its related files.

```sh
auxflow classify examples/quickstart/simple.tex
auxflow plan --explain examples/quickstart/multifile/main.tex
auxflow classify bench/corpus/b08_cycle/main.tex
```

The last command reports `AMPLIFYING` and exits with status 1. Avoid `--force`
in a live demo. Three corpus documents (`b11_width`, `b12_float`,
`b13_varioref`) exposed false negatives before syntactic guards changed their
classifications to `UNKNOWN`. See the
[benchmark notes](https://auxflow.upayan.dev/evaluation/benchmarks.html).

---

## How It Works

LaTeX documents write labels, tables of contents, and citations to helper files (`.aux`, `.toc`, `.bbl`).
Standard build tools repeat the compile process until these files stop changing.

AuxFlow scans and parses LaTeX source, then builds a graph of reference,
list, and citation facts. Its analysis identifies cycles and calculates a
model-based pass bound. The planner uses that bound only for `CERTIFIED`.
Other executable plans start with at least three engine runs.

| State | Meaning |
|---|---|
| `CERTIFIED` | The model yields a conservative pass bound. Runtime still checks the files. |
| `BENIGN_CYCLIC` | The model finds a cycle without a structural edge. Convergence is not guaranteed. |
| `AMPLIFYING` | A value can change generated content. AuxFlow refuses the plan by default. |
| `UNKNOWN` | An unsupported construct prevents certification. It does not prove non-convergence. |

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
