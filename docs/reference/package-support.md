---
title: "Packages and classes"
parent: "Reference"
nav_order: 4
---

# Packages and classes

AuxFlow analyzes a fixed set of LaTeX constructs. A package's presence in TeX Live does not mean AuxFlow models it. AuxFlow checks package names individually, including names in a comma-separated `\usepackage{geometry,xcolor}` declaration. It does not certify a TeX Live bundle or a collection of packages as a unit.

## Package names in the analysis

| Package names | What AuxFlow models | Limit |
|---|---|---|
| `graphicx` | The `\includegraphics` file reference | Graphic size and page layout are outside the model. |
| `varioref` | The `\vref` and `\vpageref` syntax | These calls make the document `UNKNOWN`. Their changing text width is outside the model. |
| `ifthen` | Counter conditions and the supported `\ifthenelse` and `\whiledo` forms | Other package commands do not gain support. |
| `inputenc`, `fontenc`, `ae`, `aecompl`, `lmodern` | Treated as inert for auxiliary-state analysis | Font and encoding effects on layout are outside the model. |
| `xcolor`, `parskip`, `geometry`, `setspace`, `multicol`, `amsmath` | Treated as inert for auxiliary-state analysis | Their effects on layout and pagination are outside the model. |

These are the names in `_MODELLED_PACKAGES` in `src/auxflow/semantic/resolve.py`. "Inert" means AuxFlow does not add an opaque fact for the package name alone. It does not grant support for every command. For example, `\eqref` resolves like `\ref`, but other commands still follow the [language subset](/reference/language-subset.html).

AuxFlow marks every other direct `\usepackage` name as unmodelled. Examples include `biblatex`, `tikz`, `fancyhdr`, and `tabularx`. An unmodelled direct package makes classification `UNKNOWN`. AuxFlow does not infer support from the package's version, installation, or TeX distribution.

## Classes and local package files

`article`, `report`, and `book` do not produce class warnings when no local file overrides them. AuxFlow does not inspect their installed class files. A local `.cls` file in the document directory produces an unmodelled-class warning and makes the document `UNKNOWN`.

`auxflow check` reads literal `\RequirePackage` names in a local class. It also follows local `.sty` files reached through those requirements. It reports unmodelled requirements with the file path. This inventory does not execute TeX. Conditional loads, generated names, and installed package files remain uninspected. A nonstandard external class produces a warning when no local `.cls` file exists. That warning alone does not guarantee an `UNKNOWN` classification, so do not treat a `CERTIFIED` result as proof about that class.

## Check a document

```sh
auxflow check main.tex
auxflow classify -v main.tex
auxflow plan --explain main.tex
```

`check` reports package and class warnings. `classify -v` shows unsupported constructs and their locations. `UNKNOWN` uses at least three engine runs unless strict mode refuses execution. AuxFlow refuses `AMPLIFYING` unless you use `--force`. Only `auxflow run` starts TeX tools, and it is not a sandbox.

The [VS Code extension](https://github.com/upayanmazumder/auxflow/blob/main/extension/README.md) uses the same static analyzer on open `.tex` documents, including unsaved edits. Download and install its VSIX from a [GitHub extension release](https://github.com/upayanmazumder/auxflow/releases); install a newer VSIX manually to update. Its diagnostics and classifications inherit these package, class, and language-subset limits. A configured workspace-relative main file sets the analysis root; otherwise the active file is the root. It reports warnings in Problems but never executes TeX. `UNKNOWN` reflects insufficient static knowledge, not proof of non-convergence.

See the [benchmark corpus](/evaluation/benchmarks.html) for tested cases. `b06_bib` uses ordinary BibTeX, while `b15_ibid` uses unmodelled `biblatex`. The original specification marked `b11_width`, `b12_float`, and `b13_varioref` as false negatives. Guards added after measurement classify them as `UNKNOWN`. This corpus cannot independently test those guards.
