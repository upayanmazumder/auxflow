---
title: "Review 3"
parent: "Reviews"
nav_order: 3
---

{: .note }
**Downloads:** [Document (PDF)](/reviews/downloads/review3-document.pdf) · [Document (DOCX)](/reviews/downloads/review3-document.docx) · [Slides (PDF)](/reviews/presentation/review3-auxflow.pdf) · [Research paper (PDF)](/paper/auxflow-paper.pdf)

# AuxFlow: Review 3 viva Q&A

Short answers for the viva, grouped by topic. Numbers come from `bench/results/2026-10-28/`.

**Facts to remember:** 15 documents, 7 baselines, 10 repetitions, 1,050 trials. Static baseline D uses no engine runs. The corpus has 7 certified and 6 unstable documents. Analysis took 1.3 ms at the median and 10.4 ms at most. The current non-engine test run passed 403 tests, skipped 1, and deselected 3.

---

## 1. Problem and motivation

**Q1. What problem does AuxFlow solve?**
A LaTeX document needs several engine runs, because each run reads the auxiliary files of the previous run. Tools find the count by running the engine. AuxFlow predicts it from the source, before the first run.

**Q2. Why does LaTeX need more than one run?**
`\label` writes a value to the `.aux` file. `\ref` reads it in the next run. A table of contents and a bibliography work the same way. The pass lag is exactly one run.

**Q3. How do existing tools decide when to stop?**
latexmk compares file checksums (limit 5). Tectonic compares files read then rewritten (limit 6). ConTeXt hashes the `.tuc` file (limit 9). Typst hashes layout iterations (limit 5). latexrun compares inputs and documents no limit.

**Q4. What is wrong with that?**
No tool derives the limit from the document. The limits are fixed numbers. Some documents never settle, and the tool learns that only at the limit. Three of five tools give no cause.

**Q5. Give an example of a document that never settles.**
Corpus member `b08_cycle` (Gaspar 2014). A loop runs while a counter is below the page of a label that sits after the loop. Each pass adds one page, so the label moves by one page every run.

---

## 2. Core concepts

**Q6. What is a fixpoint here?**
The auxiliary state that stops changing between runs. A run is correct when it reads that state.

**Q7. What is N\* and N?**
N\* is the measured run count within eight passes. N is the predicted run count. All 7 certified corpus documents have N ≥ N\*. This does not prove a universal bound.

**Q8. What is pass lag?**
The number of runs before a written value can be read. It is 1 for the `.aux` round trip. A BibTeX edge counts as 0 in the recurrence, because BibTeX runs between two engine runs.

**Q9. Why is this not just classical pass numbering?**
Classical theory (Bochmann, Alblas) assumes a fixed dependency graph. A document can change its own graph: a page reference changes the page count, and the page count decides how many page references exist. AuxFlow tests whether the classical theory applies.

---

## 3. Design and intermediate representation

**Q10. What are the main stages?**
Lexer, parser, syntax tree, symbol tables, semantic checks, ARG lowering, analysis (taint, SCC, stable pass), classifier, planner, runtime verifier. Only the verifier starts a TeX process.

**Q11. What is the ARG?**
The Auxiliary Reference Graph. One node per fact instance, one edge per dependency. A fact has a kind, key, component (`exists` or `value`), and a source span. An edge has a lag, a type, and a reason.

**Q12. Why instances and not kinds?**
A graph of fact kinds is the same small lattice for every document, so analysing it is a table lookup. Instances make it a real data-flow problem.

**Q13. What are the four edge types?**
`AUX_ROUNDTRIP` (written to a file, read later), `TOOL` (through BibTeX), `LAYOUT` (through pagination), `STRUCTURAL` (a value changes how much content is generated).

**Q14. What is the exists/value split?**
Each fact has an `exists` part and a `value` part. Without the split, every document with one `\ref` would form one big cycle and the analysis would say nothing. The split cuts the edge from a value to pagination. The cost is that some feedback is invisible (see Q51 and Q55).

**Q15. Why must every fact have a source span?**
The diagnostics print `file:line:column`. Without spans they cannot point at the cause.

**Q16. What is the declared subset?**
The constructs AuxFlow models: sectioning, labels, references, citations, captions, generated lists, counters, and loops and conditionals over counters. A list of inert packages and commands is allowed. Anything else becomes an opaque fact and the document is UNKNOWN.

**Q17. Why a subset and not all of LaTeX?**
Parsing arbitrary TeX is undecidable in general, and Erdweg et al. call detecting LaTeX dependencies soundly a lost cause. The subset is the answer: be exact inside it, and say UNKNOWN outside it.

---

## 4. Analysis

**Q18. How does taint analysis work?**
Seeds are facts whose value is read in a loop bound or condition. A worklist propagates taint along value edges. Each tainted fact gets a `STRUCTURAL` edge to the content-volume fact. Cost O(V + E).

**Q19. Why is it an over-approximation?**
Taint follows any value edge and does not check that the influence changes a quantity. A benign document can look amplifying (cost: one flag). A modelled amplifying cycle cannot be missed.

**Q20. How are cycles found?**
Iterative Tarjan SCC, O(V + E). It uses an explicit stack, because a recursive version overflows on larger documents.

**Q21. How is a component labelled?**
Internal `STRUCTURAL` edge: AMPLIFYING. Opaque fact: UNKNOWN_CYCLE. Otherwise BENIGN.

**Q22. How is the run count computed?**
s(f) = 1 if f has no dependencies, otherwise 1 + max over dependencies g of (s(g) + lag(g→f) − 1). P is the largest s(f) over facts stored in auxiliary files. N = P + 1.

**Q23. Why P + 1?**
P runs propagate the values and one more run confirms nothing changes. This is the same shape as the depth + 1 bound of Hecht and Ullman.

**Q24. Is N minimal?**
No, and we do not claim it. Minimum pass assignment is NP-complete (Räihä and Ukkonen). The bound was exact for 4 certified documents and one larger for 3.

---

## 5. Classification and planning

**Q25. What are the four states?**
CERTIFIED: no feedback in the modelled part, bounded run count. BENIGN_CYCLIC: cycles that change only values. AMPLIFYING: a value changes how much content is generated, so it may not converge. UNKNOWN: constructs outside the subset.

**Q26. Which state wins when several apply?**
AMPLIFYING, then UNKNOWN, then BENIGN_CYCLIC, then CERTIFIED. An amplifying cycle gives the user a more useful report than an opaque fact.

**Q27. What is the planner safety rule?**
Only a CERTIFIED plan uses the derived count. Every other executable plan has at least 3 engine runs. An assertion enforces it.

**Q28. What happens for an AMPLIFYING document?**
No plan, exit status 1. With `--force` it runs 3 passes and extends up to a cap of 6.

**Q29. What does the planner optimise?**
It scans only files reachable from the entry file. It runs BibTeX only if the document has both a citation and a bibliography command.

**Q30. Why do you say "may not converge" and never "will not"?**
A cycle is neither necessary nor sufficient for non-convergence. A false positive costs one flag. A false negative costs a wrong document, so the wording keeps the asymmetry.

---

## 6. Runtime verification

**Q31. Why not use LaTeX's rerun warning?**
It misses changes in generated lists (documented by `rerunfilecheck`) and gives false warnings for active characters in captions (`labelschanged`). Baseline B shows both problems in our data.

**Q32. How does the verifier decide to stop?**
After each run it parses the auxiliary files into a set of canonical records and compares it with the previous set. Equal sets mean the state is stable. If the plan ends and the state still changes, it repeats the last step until the cap.

**Q33. What does it exclude from comparison?**
Order, white space, and the argument-free `\relax`. Unrecognised records are kept, so a changing unknown record cannot look stable.

**Q34. What is a prediction miss?**
A certified document needed more runs than predicted. The verifier records it and logs a warning.

**Q35. What safety limits does `auxflow run` have?**
600 seconds per tool call (`--timeout` changes it), `-no-shell-escape`, and rejection of auxiliary files outside the work directory. It is not a sandbox. Run only trusted documents.

**Q36. Is the verifier a contribution?**
No. It reimplements the checksum idea of latexmk, so that baselines B, C, and E share one normalisation.

---

## 7. Evaluation

**Q37. What is the corpus?**
15 documents, `b01_plain` to `b15_ibid`, one mechanism each (M1 to M9), plus a multi-chapter thesis. Expected classes were written before the analyzer.

**Q38. What are the seven baselines?**
A fixed 3 runs. B rerun warning. C output comparison (latexmk). C′ input comparison (latexrun). C″ read-then-written (Tectonic). D AuxFlow static only. E AuxFlow plus runtime verification, using `--strict` for UNKNOWN.

**Q39. How is ground truth defined?**
Eight unconditional engine passes. N\* is the smallest k below 8 such that the state and the text layer from run k to run 8 all equal run 8. Documents with no such k are divergent or oscillating.

**Q40. Why "every run from k to 8"?**
Without it, a document that alternates between two states matches at every even k and gets a false finite N\*. We found this in the first measurement and fixed the harness.

**Q41. How was the experiment controlled?**
Pinned Docker image, one container per repetition, 1 CPU, no network, fixed `SOURCE_DATE_EPOCH`, ten repetitions, medians, no corpus-wide mean.

**Q42. Why did you re-run the benchmark?**
The published results were measured before the width guard. I rebuilt the image and re-ran all 1,050 records. One document (b05) had leftover `.aux` files that made three baselines stop early. Those rows were removed and re-run.

---

## 8. Results

**Q43. What are the headline results?**
All 7 certified corpus documents have N ≥ N\* within eight passes. The strict benchmark refuses all 6 unstable documents before an engine run (2 AMPLIFYING, 4 UNKNOWN). Analysis took 1.3 ms at the median and 10.4 ms at most.

**Q44. What do the baselines get wrong?**
A accepts all 6 non-convergent documents after 3 runs. B accepts `b10_random` after 1 run and stops early on `b05` and `b15`. C, C′, C″ flag all 6 and give the same verdict everywhere.

**Q45. Did you find the expected one-run gap between C and C′?**
No. They agreed on every document. We expected a gap from the manuals, and a larger corpus might show it.

**Q46. How many runs does E need?**
E made 17 runs on the 7 documents it executed, against 21 for A. Under the benchmark's strict policy, it refused 8 documents before execution. Without `--strict`, UNKNOWN can run with verification. The saving is small on tiny documents.

**Q47. Why does `b01_plain` need 2 runs under E when N = 1?**
pdfTeX writes a page-count record to every `.aux` file. The state is never empty, so the verifier needs a second run to see two equal states. The prediction is right. The miss comes from the confirming run.

**Q48. What did the external tools show?**
latexmk and latexrun fail on all 6 non-convergent documents, so they are real non-convergence. Tectonic stops `b08` at its 6-pass limit. Typst rejects a hand port of `b08` with "loop seems to be infinite".

**Q49. Why is `b14_ifthen` AMPLIFYING?**
By over-approximation. Nothing changes the quantity of content, only its size. Typst compiles the ported document without error, so this is a conservative verdict.

**Q50. Why does `b05_toc` matter?**
It must not be AMPLIFYING. This guards against an analysis that flags everything. It passes.

---

## 9. Limitations and honesty

**Q51. What was the declared false negative?**
`b11_width`, `b12_float`, `b13_varioref`. Their feedback runs through typeset width or float placement, not through a loop, so no seed reaches them. The original expectation was CERTIFIED, which is wrong.

**Q52. What changed after the first measurement?**
A guard makes a page reference under roman, Roman, alph, or Alph numbering UNKNOWN, and `\vref` and `\vpageref` UNKNOWN. A list of inert packages was added. The three documents are now UNKNOWN.

**Q53. Is that a problem for the results?**
Yes, and the report says so. The guard was added after seeing the data, so the corpus no longer tests it independently. `report.py` shows Gate 1 as FAIL against the pre-registered expectation. Gate 2 passes.

**Q54. Does the guard solve the problem?**
No. It matches syntax, not the mechanism. Width feedback under arabic numbering is not covered, and the analysis would probably certify such a document.

**Q55. What is assumption A2?**
Resolving a reference does not change pagination. It is false in general. Without it, every document with a reference is one component. With it, the analysis is unsound for the extent-driven class. We chose the second and measured it.

**Q56. List the other limits.**
Small, mostly synthetic corpus; one machine; one author for corpus and analyzer; benign-cycle bound is a heuristic with no corpus member; AMPLIFYING joins divergence and oscillation; TeX Live 2022 in the container.

---

## 10. Novelty and related work

**Q57. What is new?**
A static influence test from fact values to constructs that control content volume, which decides whether classical fixed-graph theory applies. Also a controlled comparison of five deployed stopping tests.

**Q58. What is not new?**
Pass numbering (Bochmann 1976, Alblas 1981), SCC plus condensation (Jones 1990), round bounds from graph structure (Hecht and Ullman 1975), and checksum verification (latexmk). The paper cites all of them.

**Q59. Nearest related work?**
Krishnan and Van Wyk 2012 analyse termination when evaluation generates new content. They reason over a fixed grammar with a term-ordering proof. AuxFlow reasons over one document's fact graph with reachability. Söderberg and Hedin 2013 was not read in full, so we make no claim against it.

**Q60. How does this relate to Pluto and Typst?**
Pluto builds LaTeX with a fixpoint cycle handler and does not classify cycles. Typst reports the unstable fact with spans, but only after running. AuxFlow reports a dependency chain before any run.

---

## 11. Implementation and quality

**Q61. Which language and why?**
Python 3.12 with no third-party runtime dependencies. The interesting logic is written by hand, and Python keeps the front end short.

**Q62. How big is the project?**
About 5,600 lines in 47 source modules, about 5,900 lines in 57 test files.

**Q63. How is quality checked?**
396 tests pass and 1 is skipped. `mypy --strict` and `ruff` are clean. Property tests keep the safety rule (non-certified plans keep at least 3 runs) and lexer round trips. Golden snapshots change only after review.

**Q64. How is it released?**
PyPI, versioned from git tags by hatch-vcs. Install with `pipx install auxflow`.

**Q65. What did you fix in `auxflow update`?**
In a pipx install the environment has no pip, so `python -m pip` failed. It now runs `pipx upgrade auxflow` there, and explains how to update in any other environment without pip.

**Q66. How do I reproduce the results?**
`python paper/make_results.py` regenerates every table and the chart from `bench/results/2026-10-28/`. `bash bench/demo.sh` runs the pipeline on `b08_cycle` and `b11_width`.

---

## 12. Future work

**Q67. What next?**
Test on real documents. Replace the syntactic width guard with a test that does not depend on syntax. Split AMPLIFYING into divergent and oscillating. Model more packages. Prove a bound for benign cycles.

**Q68. Why not model line breaking?**
It would need font metrics and the TeX line-breaking algorithm, which is out of scope. Modelling extent feedback also makes the graph one big cycle.

---

## Quick demo script

```bash
auxflow classify bench/corpus/b08_cycle/main.tex     # AMPLIFYING, with the 3-fact cycle
auxflow plan --explain bench/corpus/b06_bib/main.tex # CERTIFIED, 4 passes
auxflow classify bench/corpus/b11_width/main.tex     # UNKNOWN, width guard
auxflow run --force bench/corpus/b08_cycle/main.tex  # stops at the cap of 6 runs
```

Run `auxflow run` from a copy of the document. It writes `.aux` and `.log` files next to the source.

---

## Package availability

- Published on PyPI: <https://pypi.org/project/auxflow/>. Install with `pipx install auxflow`.
- Source: <https://github.com/upayanmazumder/auxflow>
- Research paper: [auxflow-paper.pdf](/paper/auxflow-paper.pdf)
