#!/usr/bin/env python3
r"""Generate every table, number, and chart in the paper from committed result files.

No number in main.tex is typed by hand. This script reads

    bench/results/2026-10-28/{results.jsonl,groundtruth.json,reference_tools.json}
    bench/results/published/results.jsonl   (historical run, before the width guard)

and writes

    paper/generated/macros.tex          \newcommand values used in the text
    paper/generated/table_corpus.tex    corpus, ground truth, classification
    paper/generated/table_exec.tex      engine runs per document and baseline
    paper/generated/table_verdicts.tex  verdict tallies per baseline
    paper/generated/table_external.tex  verdicts of latexmk, latexrun, Tectonic
    paper/figures/executions.pdf        grouped bar chart of the execution table

Run from the repository root:  python paper/make_results.py
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CURRENT = ROOT / "bench" / "results" / "2026-10-28"
HISTORIC = ROOT / "bench" / "results" / "published"
GENERATED = ROOT / "paper" / "generated"
FIGURES = ROOT / "paper" / "figures"

DYNAMIC = ("A", "B", "C", "C'", "C''")
BASELINES = (*DYNAMIC, "E")
LABEL = {"A": "A", "B": "B", "C": "C", "C'": r"C$'$", "C''": r"C$''$", "E": "E"}

MECHANISM = {
    "b01_plain": "no auxiliary facts",
    "b02_backref": "backward \\texttt{\\char92 ref}",
    "b03_fwdref": "forward \\texttt{\\char92 ref}",
    "b04_chain": "TOC, then \\texttt{\\char92 pageref}",
    "b05_toc": "table of contents",
    "b06_bib": "TOC, BibTeX, \\texttt{\\char92 pageref}",
    "b07_footnote": "M7 footnote feedback",
    "b08_cycle": "M1 page-bounded loop",
    "b09_thesis": "multi-chapter thesis",
    "b10_random": "M8 random auxiliary record",
    "b11_width": "M3 numeral width",
    "b12_float": "M4 float, Roman numerals",
    "b13_varioref": "M6 \\texttt{varioref} text",
    "b14_ifthen": "M2 page-conditioned size",
    "b15_ibid": "M5 \\texttt{ibid} citation style",
}
CLASS_SHORT = {
    "CERTIFIED": "CERT",
    "BENIGN_CYCLIC": "BENIGN",
    "AMPLIFYING": "AMPL",
    "UNKNOWN": "UNK",
}


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def short_id(document: str) -> str:
    return document.split("_")[0]


def write_rows(name: str, lines: list[str]) -> None:
    """Write table rows joined by row ends. The last row has no end: main.tex adds it.

    A row end at the very end of an \\input file makes booktabs fail to find the next rule.
    """
    rows = [line.removesuffix("\\\\").rstrip() for line in lines]
    (GENERATED / name).write_text(" \\\\\n".join(rows) + "%\n", encoding="utf-8")


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)

    rows = load_jsonl(CURRENT / "results.jsonl")
    old_rows = load_jsonl(HISTORIC / "results.jsonl")
    truth = {
        item["document"]: item
        for item in json.loads((CURRENT / "groundtruth.json").read_text())["results"]
    }
    external = {
        item["document"]: item
        for item in json.loads((CURRENT / "reference_tools.json").read_text())["results"]
    }
    documents = sorted(truth)

    by: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by[(str(row["document"]), str(row["baseline"]))].append(row)
    old_class = {
        str(r["document"]): str(r["classification"]) for r in old_rows if r["baseline"] == "D"
    }

    def nstar(document: str) -> int | None:
        value = truth[document]["n_star"]
        return value if isinstance(value, int) else None

    def nstar_text(document: str) -> str:
        value = nstar(document)
        if value is not None:
            return str(value)
        return "osc." if truth[document]["oscillating"] else "div."

    def median_runs(document: str, baseline: str) -> int:
        runs = [int(r["executions_to_certify"] or 0) for r in by[(document, baseline)]]
        return int(statistics.median(runs))

    def status(document: str, baseline: str) -> str:
        return Counter(str(r["status"]) for r in by[(document, baseline)]).most_common(1)[0][0]

    def verdict(document: str, baseline: str) -> str:
        """One of: ok, premature, missed, capped, refused."""
        state = status(document, baseline)
        if state == "CONVERGED":
            target = nstar(document)
            return (
                "ok"
                if target is not None and median_runs(document, baseline) >= target
                else ("premature" if target is not None else "missed")
            )
        if state == "CAP_EXCEEDED":
            return "capped" if nstar(document) is None else "premature"
        return "refused"

    dclass = {d: str(by[(d, "D")][0]["classification"]) for d in documents}
    # Baseline D reports UNKNOWN as external UNKNOWN; AMPLIFYING and CERTIFIED stay as they are.
    predicted = {d: by[(d, "D")][0]["predicted_runs"] for d in documents}
    finite = [d for d in documents if nstar(d) is not None]
    nonconv = [d for d in documents if nstar(d) is None]
    certified = [d for d in documents if dclass[d] == "CERTIFIED"]

    # ---- corpus table -------------------------------------------------------------------
    lines = []
    for d in documents:
        old = CLASS_SHORT.get(old_class[d], old_class[d])
        now = CLASS_SHORT.get(dclass[d], dclass[d])
        changed = "\\textbf{" + now + "}" if old != now else now
        pred = "--" if predicted[d] is None else str(predicted[d])
        lines.append(
            f"{short_id(d)} & {MECHANISM[d]} & {nstar_text(d)} & {old} & {changed} & {pred} \\\\"
        )
    write_rows("table_corpus.tex", lines)

    # ---- execution table -----------------------------------------------------------------
    lines = []
    cells_for_chart: dict[str, list[tuple[int, str]]] = {}
    for d in documents:
        cells = []
        chart = []
        for b in BASELINES:
            v = verdict(d, b)
            runs = median_runs(d, b)
            if v == "ok":
                cells.append(str(runs))
            elif v == "premature" or v == "missed":
                cells.append(f"{runs}$^\\dagger$")
            elif v == "capped":
                cells.append("cap")
            else:
                cells.append("ref.")
            chart.append((runs, v))
        cells_for_chart[d] = chart
        lines.append(f"{short_id(d)} & {nstar_text(d)} & " + " & ".join(cells) + " \\\\")
    write_rows("table_exec.tex", lines)

    # ---- verdict tallies ------------------------------------------------------------------
    tally: dict[str, dict[str, int]] = {}
    for b in (*BASELINES, "D"):
        entry = Counter()
        for d in documents:
            if b == "D":
                static = dclass[d]
                if d in finite:
                    if static == "CERTIFIED":
                        bound, target = predicted[d], nstar(d)
                        ok = bound is not None and target is not None and bound >= target
                        entry["ok" if ok else "premature"] += 1
                    else:
                        entry["refused"] += 1
                else:
                    entry["caught" if static != "CERTIFIED" else "missed"] += 1
                continue
            v = verdict(d, b)
            if d in finite:
                entry[{"ok": "ok", "premature": "premature", "refused": "refused"}.get(v, v)] += 1
            else:
                entry["caught" if v in {"capped", "refused"} else "missed"] += 1
        spent = sum(median_runs(d, b) for d in finite) if b != "D" else 0
        entry["runs"] = spent
        tally[b] = dict(entry)
    order = (*BASELINES, "D")
    header = {
        "ok": f"Correct stop, of {len(finite)} convergent documents",
        "premature": "Premature stop (stale output accepted)",
        "refused": "Withheld by static refusal",
        "caught": f"Non-convergence flagged, of {len(nonconv)}",
        "missed": "Non-convergence accepted as converged",
        "runs": f"Engine runs spent on the {len(finite)} convergent documents",
    }
    lines = []
    for key, text in header.items():
        lines.append(text + " & " + " & ".join(str(tally[b].get(key, 0)) for b in order) + " \\\\")
    write_rows("table_verdicts.tex", lines)

    # ---- external tools --------------------------------------------------------------------
    def tick(flag: bool) -> str:
        return "yes" if flag else "no"

    lines = []
    for d in documents:
        verdicts = {t["tool"]: t for t in external[d]["tools"]}
        if verdicts["latexmk"]["converged"] and verdicts["latexrun"]["converged"]:
            continue  # the text states that every other document converges under both tools
        cells = []
        for name in ("latexmk", "latexrun"):
            cells.append(tick(bool(verdicts[name]["converged"])))
        tectonic = verdicts["tectonic"]
        if tectonic["converged"] and "stopping at" in str(tectonic.get("stderr_tail", "")):
            cells.append("cap")
        elif tectonic["converged"]:
            cells.append("yes")
        else:
            cells.append("n/a")
        lines.append(f"{short_id(d)} & " + " & ".join(cells) + " \\\\")
    write_rows("table_external.tex", lines)

    # ---- scalar macros -----------------------------------------------------------------------
    latency = [float(r["static_analysis_latency_ms"]) for r in rows if r["baseline"] == "D"]
    thesis = [
        float(r["static_analysis_latency_ms"])
        for r in rows
        if r["baseline"] == "D" and r["document"] == "b09_thesis"
    ]
    thesis_row = by[("b09_thesis", "D")][0]
    over = [int(predicted[d]) - int(nstar(d) or 0) for d in certified]
    sums = {b: sum(median_runs(d, b) for d in certified) for b in (*DYNAMIC, "E")}
    cap_docs = [d for d in documents if status(d, "C") == "CAP_EXCEEDED"]
    macros = {
        "NRecords": str(len(rows)),
        "NDocs": str(len(documents)),
        "NFinite": str(len(finite)),
        "NNonconv": str(len(nonconv)),
        "NCertified": str(len(certified)),
        "LatencyMedian": f"{statistics.median(latency):.1f}",
        "LatencyMax": f"{max(latency):.1f}",
        "ThesisLatency": f"{statistics.median(thesis):.1f}",
        "ThesisFacts": str(thesis_row["graph_facts"]),
        "ThesisEdges": str(thesis_row["graph_edges"]),
        "BoundTight": str(sum(1 for x in over if x == 0)),
        "BoundOverOne": str(sum(1 for x in over if x == 1)),
        "BoundUnder": str(sum(1 for x in over if x < 0)),
        "SumA": str(sums["A"]),
        "SumB": str(sums["B"]),
        "SumC": str(sums["C"]),
        "SumCprime": str(sums["C'"]),
        "SumCdprime": str(sums["C''"]),
        "SumE": str(sums["E"]),
        "NCapC": str(len(cap_docs)),
        "ImageDigest": str(rows[0]["image_digest"]).removeprefix("sha256:")[:12],
    }
    text = "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items())
    (GENERATED / "macros.tex").write_text(text, encoding="utf-8")

    # ---- chart -----------------------------------------------------------------------------
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7,
            "pdf.fonttype": 42,
            "axes.linewidth": 0.6,
        }
    )
    colors = {
        "A": "#8A99AD",
        "B": "#E0A030",
        "C": "#4B6FA5",
        "C'": "#2F8F9D",
        "C''": "#2E6B2E",
        "E": "#A71D2A",
    }
    figure, axis = plt.subplots(figsize=(7.1, 2.3))
    width = 0.13
    for index, b in enumerate(BASELINES):
        xs, hs, hatches = [], [], []
        for position, d in enumerate(documents):
            runs, v = cells_for_chart[d][index]
            xs.append(position + (index - 2.5) * width)
            hs.append(runs)
            hatches.append("////" if v in {"premature", "missed"} else "")
        bars = axis.bar(
            xs, hs, width=width, color=colors[b], edgecolor="black", linewidth=0.3, label=b
        )
        for bar, hatch in zip(bars, hatches, strict=True):
            bar.set_hatch(hatch)
    for position, d in enumerate(documents):
        target = nstar(d)
        if target is not None:
            axis.plot(
                [position - 0.46, position + 0.46],
                [target, target],
                color="black",
                linewidth=1.1,
                linestyle=(0, (3, 1)),
                zorder=5,
            )
    axis.axhline(8, color="#A71D2A", linewidth=0.5, linestyle=":")
    axis.set_xticks(range(len(documents)))
    axis.set_xticklabels([short_id(d) for d in documents])
    axis.set_ylim(0, 9)
    axis.set_yticks(range(0, 9))
    axis.set_ylabel("engine runs until verdict")
    axis.spines[["top", "right"]].set_visible(False)
    handles, labels = axis.get_legend_handles_labels()
    axis.legend(
        handles,
        labels,
        ncol=6,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.2),
        handlelength=1.2,
        columnspacing=1.2,
    )
    figure.tight_layout()
    figure.savefig(FIGURES / "executions.pdf")
    print("wrote", GENERATED, FIGURES / "executions.pdf")


if __name__ == "__main__":
    main()
