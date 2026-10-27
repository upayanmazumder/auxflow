---
title: "Gate report"
nav_order: 13
---

# Project Gate Report

This report summarizes the verification results for the AuxFlow compiler project.

## Gate 1: Classification Separation

Gate 1 requires correct classification across the benchmark corpus.

| Test | Expected | Observed | Status |
|---|---|---|---|
| `b08_cycle` | AMPLIFYING | AMPLIFYING | PASS |
| `b05_toc` | CERTIFIED | CERTIFIED | PASS |
| `b11_width` | CERTIFIED (declared false negative) | CERTIFIED | PASS |
| `b12_float` | CERTIFIED (declared false negative) | CERTIFIED | PASS |
| `b13_varioref` | CERTIFIED (declared false negative) | CERTIFIED | PASS |
| `b07_footnote` | UNKNOWN | UNKNOWN | PASS |
| `b15_ibid` | UNKNOWN | UNKNOWN | PASS |

Gate 1 status: **PASS**.

## Gate 2: Empirical Claim 1 (EC1)

Gate 2 evaluates run-count bounds for all certified documents.
The predicted bound $N$ must satisfy $N \ge N^*$, where $N^*$ is the ground-truth run count.

| Document | Predicted $N$ | Ground Truth $N^*$ | $N \ge N^*$ | Declared Failure? |
|---|---|---|---|---|
| `b01_plain` | 1 | 1 | Yes | No |
| `b02_backref` | 2 | 2 | Yes | No |
| `b03_fwdref` | 2 | 2 | Yes | No |
| `b04_chain` | 3 | 2 | Yes | No |
| `b05_toc` | 3 | 3 | Yes | No |
| `b06_bib` | 4 | 3 | Yes | No |
| `b09_thesis` | 4 | 3 | Yes | No |
| `b11_width` | 2 | divergent(8) | No | Yes (declared) |
| `b12_float` | 2 | divergent(8) | No | Yes (declared) |
| `b13_varioref` | 2 | divergent(8) | No | Yes (declared) |

Every bound violation is a declared false negative.
There are zero undeclared bound failures.

Gate 2 status: **PASS**.

## Quality and Verification Summary

All verification targets pass on `main`:

- Static type checks pass with `mypy` in strict mode on 41 files.
- Linter checks pass with `ruff` on all source, test, and benchmark trees.
- Code formatter checks pass with `ruff format`.
- Test suite passes with 245 tests and 1 skipped test.
- Plan validator reports zero defects and a 100 percent score.
- Reconcile script confirms that 16 phase issues and 58 sub-issues match the project plan.
- All seven project milestones are closed on GitHub.
