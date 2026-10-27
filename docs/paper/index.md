---
title: "Paper"
nav_order: 5
---

# Research paper

**AuxFlow: A Static Applicability Test for Fixpoint Convergence in Multi-Pass LaTeX Builds**

Upayan Mazumder and Banupriya R. School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Vellore.

[Download the paper (PDF)](/paper/auxflow-paper.pdf)

The paper describes the Auxiliary Reference Graph, the influence analysis, the classifier, and the runtime verifier.
It reports a measurement of 15 documents, 7 stopping strategies, and 10 repetitions (1,050 records).
It also reports a guard that the author added after the first measurement.

## Source and reproduction

- LaTeX source, figures, and build notes: [`paper/`](https://github.com/upayanmazumder/auxflow/tree/main/paper)
- Result files that the tables use: [`bench/results/2026-10-28/`](https://github.com/upayanmazumder/auxflow/tree/main/bench/results/2026-10-28)
- Run `make results` in `paper/` to regenerate every table and number from the result files.

For the supporting detail, see the [specification](/project/specification.html), the [evaluation methodology](/evaluation/methodology.html), and the [benchmark corpus](/evaluation/benchmarks.html).
