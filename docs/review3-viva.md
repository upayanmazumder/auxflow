# AuxFlow — Review 3 Viva Preparation

Static Analysis for Multi-Pass Document Compilation · Upayan Mazumder (24BDS0367) · Compiler Design Lab

Companion guide for Review 3: Analysis, Optimization, Verification, and Evaluation (Phases 8–16).
Framing remains conservative: AuxFlow provides static classification, safe build planning, and empirical verification.

---

### 1. How does the static analysis classify cycles?
- Computes strongly connected components (SCCs) via an iterative Tarjan algorithm (`auxflow.analysis.scc`).
- Classifies non-trivial components into `AMPLIFYING`, `BENIGN`, or `UNKNOWN_CYCLE`.
- Benign cycles (e.g. section lists) affect only values; amplifying cycles affect content generation.

### 2. How does taint analysis identify divergence risks?
- Seeds facts read inside loop bounds or conditional expressions (`ControlConstruct` nodes).
- Propagates taint forward along value-carrying edges using a monotonic worklist (`auxflow.analysis.taint`).
- Inserts `STRUCTURAL` edges from tainted facts to `CONTENT_VOLUME` with exact source span reasons.

### 3. What are the four document states?
1. `CERTIFIED`: provably acyclic after abstraction; bounded static run count $P + 1$.
2. `BENIGN_CYCLIC`: value-only cycles; non-amplifying; bounded by runtime verification.
3. `AMPLIFYING`: value influences content generation; may diverge; refused by default.
4. `UNKNOWN`: contains unmodelled constructs; falls back to conservative default execution.

### 4. What optimizations occur in the build planner?
- `auxflow.planner.lower` applies four linear passes:
  1. Dead-file elimination: limits per-file auxiliary tooling to reachable files in the inclusion graph.
  2. Dead-tool elimination: runs BibTeX only when citation facts and bibliography commands exist.
  3. Run-count derivation: derives the engine schedule from `stable_pass` ($P$).
  4. Non-convergence refusal: emits no plan for amplifying documents unless `--force` is set.
- Enforces safety invariant: non-certified plans always require at least 3 engine runs.

### 5. How does runtime verification differ from engine warnings?
- Engine warnings (`LaTeX Warning: Label(s) may have changed`) miss generated list changes and are unsound.
- AuxFlow normalizes auxiliary files into canonical order-independent record sets (`auxflow.runtime.normalize`).
- Computes a state fixpoint directly: compares normalized state $A_k$ with $A_{k-1}$.
- Logs explicit `PredictionMiss` records if actual runs exceed certified static predictions.

### 6. What was the evaluation setup and corpus design?
- 15-member benchmark corpus (`b01_plain` to `b15_ibid`) covering mechanisms M1–M8.
- 7 baselines tested: A (fixed), B (warnings), C (checksum), C′ (inputs), C″ (read/write), D (static), E (static+verify).
- 1050 containerized runs inside a pinned Docker container (`auxflow-bench:v1`).
- Independent ground truth $N^*$ computed via 8 unconditional passes with state and text equality.

### 7. What were the key gate results?
- **Gate 1 (Classification Separation): PASS.**
  - Identifies `b08_cycle` as `AMPLIFYING` with 3 named facts and spans.
  - Identifies `b05_toc` as `CERTIFIED` (no false positive).
  - Matches declared false negatives on `b11_width`, `b12_float`, and `b13_varioref`.
- **Gate 2 (EC1 Bound Bound): PASS.**
  - Predicted $N \ge N^*$ holds for all certified documents.
  - Zero undeclared bound failures across the entire corpus.

### 8. What do external shipping tools show on the same corpus?
- `latexmk` and `latexrun` fail to converge on `b11_width`, `b12_float`, and `b13_varioref`.
  - Confirms declared false negatives are real physical non-convergence, not benchmark artifacts.
- Typst compiler independently flags `b08_cycle` with `error: loop seems to be infinite`.
- Baseline D static analysis executes in under 10 ms for all documents.

---

## Quick Backups (Viva Questions)
- **How to demonstrate the compiler live?** Run `bash bench/demo.sh` to execute the full pipeline from tokens to verification on `b08_cycle` and `b11_width`.
- **Why did baseline B fail on b10_random?** Random state changes produce no cross-reference warning; baseline B declared convergence after 1 run while ground truth diverged.
- **Why did b01_plain require 2 runs under verification?** pdfTeX writes `\@abspage@last{1}` on every run; the verifier needs 2 runs to confirm this bookkeeping value is stable.
- **Where are all published results stored?** In `bench/results/published/results.jsonl`, `summary.md`, and `docs/EVALUATION-REPORT.md`.
