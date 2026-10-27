---
title: Home
nav_order: 0
---

# AuxFlow

Static convergence classification for multi-pass document compilation.

[![PyPI](https://img.shields.io/pypi/v/auxflow)](https://pypi.org/project/auxflow/) [![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://pypi.org/project/auxflow/)

AuxFlow is a compiler and static analyzer for LaTeX documents. It builds an instance-level dependency graph of cross-references, detects feedback cycles, and predicts how many passes the document needs to stabilize — before the typesetting engine runs.

---

## Install

```bash
pipx install auxflow
```

Or with pip inside a virtual environment:

```bash
pip install auxflow
```

---

## How it works

1. Parses LaTeX source into an AST.
2. Resolves label, reference, and citation symbols across all files.
3. Constructs an **Auxiliary Reference Graph (ARG)**.
4. Detects cycles with Tarjan's SCC algorithm.
5. Tracks values that affect document length via forward taint analysis.
6. Classifies convergence and generates an optimized build plan.

Documents classify into one of four states:

| State | Meaning |
|---|---|
| `CERTIFIED` | Acyclic. Settles within a derived pass count. |
| `BENIGN_CYCLIC` | Value-only cycles. Settles safely. |
| `AMPLIFYING` | Reference values control content generation. May diverge. |
| `UNKNOWN` | Contains unmodelled packages or macros. Conservative schedule. |

---

## Quick start

```bash
# Classify a document
auxflow classify document.tex

# Inspect the ARG
auxflow graph document.tex

# Run with runtime verification
auxflow run document.tex
```

---

## Documentation

Use the sidebar to navigate the full documentation.
