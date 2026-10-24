# Licensed online LaTeX projects

These are five independent upstream projects, copied as local, self-contained entry files. The `.tex` contents and original filenames are retained without edits; the only additions are this catalog and local copies of the four MIT license notices. Source links point to the upstream default branch at the time of collection (2026-10-24); no immutable upstream commit was established. Each MIT notice is preserved in the corresponding project's `LICENSE` file. The CC0 license text and attribution for Adam Rumpf's example are linked below. Generated PDFs and upstream build scripts are not copied. No command here fetches or executes remote content.

| Local entry | Upstream repository | Exact upstream file | License evidence | Required TeX packages (`\usepackage` declarations) | Build from repository root |
| --- | --- | --- | --- | --- | --- |
| `packt-list/03_enumerate_list.tex` | [PacktPublishing/LaTeX-Beginner-s-Guide-Second-Edition](https://github.com/PacktPublishing/LaTeX-Beginner-s-Guide-Second-Edition) | [Chapter_04_-_Creating_Lists/03_enumerate_list.tex](https://github.com/PacktPublishing/LaTeX-Beginner-s-Guide-Second-Edition/blob/main/Chapter_04_-_Creating_Lists/03_enumerate_list.tex) | [MIT, © 2021 Packt](https://github.com/PacktPublishing/LaTeX-Beginner-s-Guide-Second-Edition/blob/main/LICENSE); [local notice](packt-list/LICENSE) | none (standard `article` class) | `pdflatex -output-directory=/tmp examples/online/packt-list/03_enumerate_list.tex` |
| `jdlee-crossref/structure-crossref.tex` | [jdleesmiller/latex-course](https://github.com/jdleesmiller/latex-course) | [en/structure-crossref.tex](https://github.com/jdleesmiller/latex-course/blob/master/en/structure-crossref.tex) | [MIT, © 2013–2018 John Lees-Miller](https://github.com/jdleesmiller/latex-course/blob/master/LICENSE); [local notice](jdlee-crossref/LICENSE) | `amsmath` | `pdflatex -output-directory=/tmp examples/online/jdlee-crossref/structure-crossref.tex` |
| `adam-paper/main.tex` | [adam-rumpf/latex-examples-sp24](https://github.com/adam-rumpf/latex-examples-sp24) | [mwe_complete/main.tex](https://github.com/adam-rumpf/latex-examples-sp24/blob/main/mwe_complete/main.tex) | [CC0 1.0 Universal](https://github.com/adam-rumpf/latex-examples-sp24/blob/main/LICENSE), Adam Rumpf | `geometry` (`margin=1.0in`), `setspace`, `amsmath` | `pdflatex -output-directory=/tmp examples/online/adam-paper/main.tex` |
| `mislav-columns/MultipleColumns.tex` | [MislavJaksic/Latex-Overleaf](https://github.com/MislavJaksic/Latex-Overleaf) | [MultipleColumns/MultipleColumns.tex](https://github.com/MislavJaksic/Latex-Overleaf/blob/master/MultipleColumns/MultipleColumns.tex) | [MIT, © 2019 MislavJaksic](https://github.com/MislavJaksic/Latex-Overleaf/blob/master/LICENSE); [local notice](mislav-columns/LICENSE) | `inputenc` (`utf8`), `multicol` | `pdflatex -output-directory=/tmp examples/online/mislav-columns/MultipleColumns.tex` |
| `mhyee-colours/colours.tex` | [mhyee/latex-examples](https://github.com/mhyee/latex-examples) | [colours.tex](https://github.com/mhyee/latex-examples/blob/master/colours.tex) | [MIT, © 2012–present Ming-Ho Yee](https://github.com/mhyee/latex-examples/blob/master/LICENSE); [local notice](mhyee-colours/LICENSE) | `fontenc` (`T1`), `ae`, `aecompl`, `inputenc` (`utf8`), `lmodern`, `xcolor` (`x11names`), `parskip` | `pdflatex -output-directory=/tmp examples/online/mhyee-colours/colours.tex` |

The table is also the **package matrix**: no two projects have identical declared package sets, and declarations have not been removed or treated as automatically supported by AuxFlow. The `article` class comes with a standard LaTeX installation; install the listed packages in the TeX distribution before compiling. Run `pdflatex` a second time for resolved references in `jdlee-crossref` and `adam-paper`. The filenames in `/tmp` can collide with unrelated local jobs; use a dedicated temporary output directory if running concurrently.

## Tested classifications

Measured on 2026-10-24 with `auxflow classify`, `plan --explain`, and `run` (TeX Live 2026 container, no network, copied sources).

| Project | Classification | Run result |
| --- | --- | --- |
| `packt-list` | CERTIFIED, 1 run | CONVERGED at run 2 (recorded prediction miss: pdfTeX writes `\@abspage@last` on every run) |
| `jdlee-crossref` | CERTIFIED, 2 runs | CONVERGED at run 2 |
| `adam-paper` | CERTIFIED, 2 runs | CONVERGED at run 2 |
| `mislav-columns` | CERTIFIED, 1 run | CONVERGED at run 2 (same prediction miss) |
| `mhyee-colours` | CERTIFIED, 1 run | CONVERGED at run 2 (same prediction miss) |

These results rest on a narrow allowlist (`_MODELLED_PACKAGES` in `src/auxflow/semantic/resolve.py` and `_INERT_COMMANDS` in `src/auxflow/ir/graph.py`). It covers packages and commands that write no auxiliary state. Their effect on pagination is not modelled. This is not support for arbitrary packages: any package or command outside the list still makes a document UNKNOWN.
