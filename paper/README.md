# Paper

`main.tex` is the conference paper in IEEEtran format. It reports the evaluation in
`bench/results/2026-10-28/`.

## Build

```bash
make            # compile main.pdf
make results    # regenerate tables, numbers, and the chart from bench/results
make figures    # render the Mermaid sources in figures/src to vector PDF
make shots      # render the terminal screenshots from live auxflow output
```

`make figures` needs Node.js and Chrome. `make shots` needs `auxflow` on `PATH`.

## Rules

- No number in `main.tex` is typed by hand. `make_results.py` writes `generated/` and
  `figures/executions.pdf` from the result files.
- Every diagram has a Mermaid source in `figures/src/`. Edit the source, not the PDF.
- Every screenshot is real `auxflow` output. `scripts/render_terminal_screenshots.py` runs
  the commands on corpus documents in a temporary directory.
- Run the benchmark from a clean checkout. A leftover `.aux` file in a corpus directory
  makes the baselines stop early.

## Fonts

IEEEtran uses Times. If the Times metrics are missing, `Makefile` adds `fallback-fonts/`
to `TEXINPUTS`. That directory maps Times to Computer Modern. Final submission needs the
real Times fonts.

`IEEEtran.cls` and `IEEEtran.bst` are copies from CTAN (LPPL).
