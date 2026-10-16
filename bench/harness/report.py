#!/usr/bin/env python3
r"""Regenerate the mechanism-coverage and oracle-comparison tables from JSONL.

No figure or table in the evaluation report is produced by hand
(docs/BENCHMARKS.md, bench/README.md): this script is the only place either
table is assembled, and re-running it over the same bench/results/ directory
must reproduce byte-identical output.

Usage:
    python3 bench/harness/report.py bench/results/<dir> \
        --groundtruth bench/results/published/groundtruth.json \
        --corpus bench/corpus > bench/results/<dir>/summary.md
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))

BASELINE_ORDER = ["A", "B", "C", "C'", "C''", "D", "E"]


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_expected(corpus_dir: Path) -> dict[str, dict[str, object]]:
    expected = {}
    for doc_dir in sorted(corpus_dir.iterdir()):
        expected_path = doc_dir / "expected.json"
        if expected_path.is_file():
            expected[doc_dir.name] = json.loads(expected_path.read_text(encoding="utf-8"))
    return expected


def _dist(values: list[float]) -> str:
    if not values:
        return "n/a"
    values = sorted(values)
    median = statistics.median(values)
    p95_index = min(len(values) - 1, round(0.95 * (len(values) - 1)))
    p95 = values[p95_index]
    q1 = statistics.median(values[: len(values) // 2]) if len(values) > 1 else values[0]
    q3 = (
        statistics.median(values[(len(values) + 1) // 2 :]) if len(values) > 1 else values[0]
    )
    return f"median {median:.1f}, p95 {p95:.1f}, IQR [{q1:.1f}, {q3:.1f}]"


def mechanism_coverage_table(
    records: list[dict[str, object]], expected: dict[str, dict[str, object]]
) -> str:
    lines = [
        "| Document | Mechanism | Expected | Observed (D) | Declared? | Match |",
        "|---|---|---|---|---|---|",
    ]
    by_doc_d = {}
    for record in records:
        if record["baseline"] == "D":
            by_doc_d.setdefault(record["document"], []).append(record)

    for document in sorted(expected):
        exp = expected[document]
        exp_class = exp["expected_class"]
        declared = exp.get("declared_false_negative", False)
        mechanism = exp.get("mechanism") or exp.get("purpose", "")
        observed_records = by_doc_d.get(document, [])
        observed = observed_records[0]["classification"] if observed_records else "NOT RUN"
        consistent = all(r["classification"] == observed for r in observed_records)
        match = "yes" if observed == exp_class else "NO -- UNDECLARED MISS"
        if declared:
            miss = "NO -- declared case did not reproduce"
            match = "yes (declared)" if observed == exp_class else miss
        flag = "" if consistent else " [non-deterministic observation!]"
        lines.append(
            f"| `{document}` | {mechanism} | {exp_class} | {observed}{flag} | "
            f"{'yes' if declared else 'no'} | {match} |"
        )
    return "\n".join(lines)


def oracle_comparison_table(
    records: list[dict[str, object]], groundtruth: dict[str, object]
) -> str:
    gt_by_doc = {r["document"]: r for r in groundtruth.get("results", [])}
    by_doc_baseline: dict[tuple[str, str], list[dict[str, object]]] = {}
    for record in records:
        key = (record["document"], record["baseline"])
        by_doc_baseline.setdefault(key, []).append(record)

    documents = sorted({record["document"] for record in records})
    lines = [
        "| Document | N* | " + " | ".join(BASELINE_ORDER) + " |",
        "|---|---|" + "---|" * len(BASELINE_ORDER),
    ]
    for document in documents:
        gt = gt_by_doc.get(document, {})
        n_star = "oscillating" if gt.get("oscillating") else gt.get("n_star", "n/a")
        cells = []
        for baseline in BASELINE_ORDER:
            reps = by_doc_baseline.get((document, baseline), [])
            execs = [
                r["executions_to_certify"]
                for r in reps
                if r.get("executions_to_certify") is not None
            ]
            cells.append(_dist([float(e) for e in execs]))
        lines.append(f"| `{document}` | {n_star} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def gate_1(records: list[dict[str, object]], expected: dict[str, dict[str, object]]) -> str:
    by_doc_d = {}
    for record in records:
        if record["baseline"] == "D":
            by_doc_d.setdefault(record["document"], []).append(record["classification"])

    checks: list[tuple[str, bool, str]] = []

    def observed(doc: str) -> str | None:
        values = by_doc_d.get(doc, [])
        return values[0] if values else None

    checks.append(
        (
            "b08 observed AMPLIFYING",
            observed("b08_cycle") == "AMPLIFYING",
            str(observed("b08_cycle")),
        )
    )
    checks.append(
        ("b05 not AMPLIFYING", observed("b05_toc") != "AMPLIFYING", str(observed("b05_toc")))
    )
    for doc in ("b11_width", "b12_float", "b13_varioref"):
        exp = expected[doc]["expected_class"]
        name = f"{doc} matches declared false negative ({exp})"
        checks.append((name, observed(doc) == exp, str(observed(doc))))
    checks.append(
        (
            "b07_footnote UNKNOWN",
            observed("b07_footnote") == "UNKNOWN",
            str(observed("b07_footnote")),
        )
    )
    checks.append(
        ("b15_ibid UNKNOWN", observed("b15_ibid") == "UNKNOWN", str(observed("b15_ibid")))
    )

    lines = ["| Gate 1 check | Pass | Observed |", "|---|---|---|"]
    for name, ok, obs in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {obs} |")
    all_pass = all(ok for _, ok, _ in checks)
    lines.append("")
    lines.append(f"**Gate 1: {'PASS' if all_pass else 'FAIL'}**")
    return "\n".join(lines)


def gate_2_ec1(
    records: list[dict[str, object]],
    expected: dict[str, dict[str, object]],
    groundtruth: dict[str, object],
) -> str:
    """EC1 (docs/STATIC-ANALYSIS.md): for every document AuxFlow classifies
    CERTIFIED with predicted bound N, the ground-truth run count N* must
    satisfy N* <= N -- the prediction is never an under-estimate. Declared
    false negatives (b11-b13) are the documented, anticipated EC1 failures:
    AuxFlow predicts a finite N for a document that never actually
    stabilises, so N* has no finite value and the inequality cannot hold.
    """
    gt_by_doc = {r["document"]: r for r in groundtruth.get("results", [])}
    by_doc_d = {}
    for record in records:
        if record["baseline"] == "D":
            by_doc_d.setdefault(record["document"], []).append(record)

    header = "| Document | Predicted N | Ground truth N* | N* <= N | Declared failure? |"
    lines = [header, "|---|---|---|---|---|"]
    failures: list[str] = []
    undeclared_failures: list[str] = []
    for document in sorted(expected):
        d_records = by_doc_d.get(document, [])
        classification = d_records[0]["classification"] if d_records else None
        if classification != "CERTIFIED":
            continue
        predicted = d_records[0]["predicted_runs"]
        gt = gt_by_doc.get(document, {})
        n_star = gt.get("n_star")
        declared = bool(expected[document].get("declared_false_negative", False))
        if isinstance(n_star, int) and isinstance(predicted, int):
            holds = n_star <= predicted
        else:
            holds = False  # divergent/oscillating N*: no finite bound can satisfy EC1
        if not holds and not declared:
            undeclared_failures.append(document)
        if not holds:
            failures.append(document)
        lines.append(
            f"| `{document}` | {predicted} | {n_star} | {'yes' if holds else 'NO'} | "
            f"{'yes' if declared else 'no'} |"
        )
    lines.append("")
    if undeclared_failures:
        violations = ", ".join(undeclared_failures)
        lines.append(f"**Gate 2 (EC1): FAIL** -- undeclared EC1 violation(s): {violations}")
    else:
        lines.append(
            "**Gate 2 (EC1): PASS** -- every EC1 violation is a declared false negative "
            f"({', '.join(failures) if failures else 'none observed'})"
        )
    return "\n".join(lines)


def executions_figure(records: list[dict[str, object]], out_path: Path) -> None:
    """Bar chart: median executions-to-certify per baseline, per document.

    Regenerated from JSONL on every run -- bench/README.md rule "no figure
    in the report is produced by hand". Distributions have zero variance in
    this corpus (every baseline's stopping rule is a deterministic function
    of pinned-timestamp TeX output), so a median-only bar chart loses no
    information here; p95/IQR remain in the text table for documents where
    that stops being true.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_doc_baseline: dict[tuple[str, str], list[float]] = {}
    for record in records:
        execs = record.get("executions_to_certify")
        if execs is None:
            continue
        key = (record["document"], record["baseline"])
        by_doc_baseline.setdefault(key, []).append(float(execs))

    documents = sorted({doc for doc, _ in by_doc_baseline})
    fig, ax = plt.subplots(figsize=(13, 6))
    width = 0.11
    x = range(len(documents))
    for i, baseline in enumerate(BASELINE_ORDER):
        medians = [
            statistics.median(by_doc_baseline.get((doc, baseline), [0.0])) for doc in documents
        ]
        offsets = [xi + (i - len(BASELINE_ORDER) / 2) * width for xi in x]
        ax.bar(offsets, medians, width=width, label=baseline)
    ax.set_xticks(list(x))
    ax.set_xticklabels(documents, rotation=45, ha="right")
    ax.set_ylabel("executions to certify (median of 10 reps)")
    ax.set_title("Executions to certify, per document per baseline")
    ax.legend(ncol=7, loc="upper center", bbox_to_anchor=(0.5, -0.35))
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir")
    parser.add_argument("--groundtruth", required=True)
    parser.add_argument("--corpus", default=str(HARNESS_DIR.parent / "corpus"))
    parser.add_argument("--figure", default=None)
    args = parser.parse_args()

    results_path = Path(args.results_dir) / "results.jsonl"
    records = load_jsonl(results_path)
    expected = load_expected(Path(args.corpus))
    groundtruth = json.loads(Path(args.groundtruth).read_text(encoding="utf-8"))

    print("## Mechanism-coverage table\n")
    print(mechanism_coverage_table(records, expected))
    print("\n## Oracle-comparison table (executions to certify)\n")
    print(oracle_comparison_table(records, groundtruth))
    print("\n## Gate 1\n")
    print(gate_1(records, expected))
    print("\n## Gate 2 (EC1)\n")
    print(gate_2_ec1(records, expected, groundtruth))
    if args.figure:
        executions_figure(records, Path(args.figure))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
