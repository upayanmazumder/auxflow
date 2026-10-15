# Benchmark corpus

Fifteen documents. Each tests a distinct mechanism or a required realistic case.
Four documents are expected to be misclassified. See
[Declared false negatives](#declared-false-negatives).

Every document must compile under a stock engine so that dynamic baselines run on identical
input. Documents are committed as sources only — build artifacts are never committed.

## Design rules

1. **One mechanism per document.** If two documents test the same dependency structure, one of
   them is redundant.
2. **Expectations are hand-derived before the analyser runs on a corpus member.** `expected.json`
   is the test oracle. Back-filling it from program output makes results circular.
3. **No performance figures in benchmark metadata.** `expected.json` records structure and
   expected behaviour, never timings.
4. **The realistic document must contain unreachable files**, otherwise dead-file elimination
   has nothing to eliminate and the corresponding claim cannot be tested.
5. **Every non-convergence mechanism in [RELATED-WORK.md](RELATED-WORK.md) section 7.3 has a
   member, including the ones AuxFlow cannot detect.** A corpus containing only detectable
   mechanisms would produce a flattering and worthless coverage result.
6. **An expected misclassification is written into `expected.json` before implementation, exactly
   like any other expectation.** A false negative that was predicted is a result; a false negative
   that was discovered is a defect.

## The corpus

| ID | Document | Purpose | Expected dependency structure | Expected classification |
|---|---|---|---|---|
| `b01_plain` | No labels, references, lists or citations | The simplest case, and the one where a state-comparison detector provably costs an extra run | no facts | CERTIFIED |
| `b02_backref` | A label, then a later reference to it | The minimal auxiliary round trip | one edge, acyclic | CERTIFIED |
| `b03_fwdref` | A reference, then a later label | Confirms direction does not affect the lag | one edge, acyclic | CERTIFIED |
| `b04_chain` | Chained dependencies without generated lists | Forces stable-pass to exceed two by chaining rather than by list feedback | a path of length 3 | CERTIFIED |
| `b05_toc` | Table of contents with many sections, no references | The generated-list path. **Also the document on which engine-warning detection is unsound.** | list extent feeding pagination | CERTIFIED, and explicitly **not** amplifying |
| `b06_bib` | Table of contents, bibliography, page references | The external-tool edge and the deepest ordinary cascade | tool edge then list edge then layout | CERTIFIED |
| `b07_footnote` | A page reference in a footnote changes its own page placement | **Declared false negative.** Extent feedback in a footnote (M7) | acyclic in the ARG; no STRUCTURAL edge | **CERTIFIED — which is WRONG.** Expected misclassification |
| `b08_cycle` | A loop bounded by a page reference to a label inside the generated material | **The headline case.** Structure known from the literature not to converge | a cycle containing a STRUCTURAL edge | **AMPLIFYING** |
| `b09_thesis` | Multi-chapter document with contents, lists, bibliography, cross-references, **unreachable auxiliary files**, and an active-character caption | Realism and the engine-warning false positive (M9); also no expected saving | several hundred facts, acyclic after abstraction | CERTIFIED |
| `b10_random` | A generated auxiliary record contains a fresh pdfTeX random value each run | Out-of-model nondeterministic generated state (M8); the fallback must degrade rather than crash | opaque facts | **UNKNOWN** |
| `b11_width` | A `\pageref` whose resolved width changes a line break, hence a page break, hence the reference. No loop, no conditional | **Declared false negative.** Period-2 oscillation via typeset extent | acyclic in the ARG; no STRUCTURAL edge | **CERTIFIED — which is WRONG.** Expected misclassification |
| `b12_float` | A `[!t]` float taking most of a page, with roman page numbering | **Declared false negative.** Period-2 oscillation via float placement, which is not modelled at all | acyclic in the ARG | **CERTIFIED — which is WRONG.** Expected misclassification |
| `b13_varioref` | `varioref`-style dynamic textual references whose length moves the floats they refer to | **Declared false negative.** Narrow syntax recognition does not model typeset extent (M6) | acyclic in the ARG; no STRUCTURAL edge | **CERTIFIED — which is WRONG.** Expected misclassification |
| `b14_ifthen` | `\ifthenelse` selecting between differently sized content on a `\pageref` | Period-2 oscillation that the seed rule *does* catch, but for the wrong reason: nothing changes the *quantity* of content, only its size | a cycle containing a STRUCTURAL edge | **AMPLIFYING** — a true positive obtained by over-approximation |
| `b15_ibid` | Two consecutive citations of one source near a page break, in a citation style that selects a shorter form when the previous citation is on the same page | The mechanism only assumption A3 protects against. Confirms that the opaque-package rule is load-bearing and not decoration | opaque facts | **UNKNOWN** |

### Declared false negatives

`b07`, `b11`, `b12`, and `b13` are non-convergent documents that AuxFlow is expected to classify
as convergent. They are in the corpus **because** of that. Their `expected.json` files record
the wrong answer as the expected answer, with `"declared_false_negative": true` and a note
naming the mechanism.

The reason is structural and is not fixable by tuning: all four feed back through the *typeset
extent* of a resolved value, and [IR.md](IR.md)'s `exists`/`value` split severs that edge by
construction. Removing the split would make every document containing one `\ref` a single strongly
connected component and the analysis vacuous. See open decision D13 in [PROJECT.md](PROJECT.md) and
[RELATED-WORK.md](RELATED-WORK.md) section 7.4.

**If any of `b07` or `b11`–`b13` is classified `AMPLIFYING` or `UNKNOWN`, investigate it.**
An analysis that accidentally catches these has unexplained behaviour.

### The two highest-value tests remain unchanged

`b08` must be classified `AMPLIFYING` with all three facts named and correct spans. `b05` must
**not** be classified `AMPLIFYING`. `b07` and `b11`–`b13` form the third gate: their
misclassification must be predicted, not discovered.

Ground-truth run counts are deliberately absent from this table. They are produced by the
harness under the protocol in [EVALUATION.md](EVALUATION.md) and recorded in
`bench/results/`, not asserted in documentation.

## `expected.json`

One per document. Hand-written from analysis of the source, before the analyser exists.

```json
{
  "id": "b06_bib",
  "purpose": "external tool edge plus generated-list cascade",
  "expected_class": "CERTIFIED",
  "expected_structure": {
    "has_cycle": false,
    "has_structural_edge": false,
    "min_facts": 40,
    "longest_chain": ["CITE_USE", "BBL", "TOC_ENTRY", "CONTENT_VOLUME", "LABEL_PAGE"]
  },
  "must_not": ["AMPLIFYING"],
  "notes": "Chain depth is the point. Ground truth is measured, not asserted here."
}
```

`must_not` exists because negative expectations are the ones that catch a vacuous analyser.
`b05` carries `"must_not": ["AMPLIFYING"]`, and that single assertion guards against the most
likely way for the classifier to appear to work while being useless.

`b07`, `b11`, `b12`, and `b13` additionally carry `"declared_false_negative": true` with
`"mechanism"` naming the non-convergence mechanism and `"why_undetected"` giving one sentence. The
harness must report these separately from genuine misses, because a predicted misclassification and
an unpredicted one are different results and averaging them would hide the interesting one.

## Directory layout

```
bench/
  corpus/
    b01_plain/
      main.tex
      expected.json
      README.md          one paragraph: what this document tests and why
    b02_backref/
    ...
    b15_ibid/
    shared/
      refs.bib           shared bibliography database
      auditthesis.cls    minimal document class used by the larger documents
  baselines/
    fixed.sh             baseline A
    warning.sh           baseline B
    checksum.sh          baseline C   consecutive-output comparison
    inputs.sh            baseline C'  consecutive-input comparison
    readwrite.sh         baseline C"  same-run read-then-written comparison
    README.md            what each script does and what it deliberately does not do
  harness/
    run.py               executes a (document, baseline) pair, emits JSONL
    normalise.py         auxiliary state to canonical record set
    groundtruth.py       computes N* per the adopted criterion
    report.py            JSONL to tables
  results/
    .gitkeep             raw results are regenerated, not committed
    published/           result sets deliberately promoted for the report
  README.md
```

Baselines are shell scripts rather than Python so that a reviewer can read in ten lines exactly
what was executed. The harness is Python because it needs structured output.

## Reproducibility

- Documents are sources only; artifacts are gitignored.
- The container image is pinned by digest and recorded in every results file.
- The harness writes one JSONL record per repetition, including image digest, document
  identifier, baseline, repetition index, and every metric.
- `report.py` regenerates all tables from JSONL, so no figure is produced by hand.
- Deterministic timestamp variables are set by the harness, not left to the environment.

## Growth policy

The corpus grows only when a new *mechanism* needs coverage — a new external tool, a new
generated-state kind, a new way for content quantity to depend on a value. Adding more documents
that exercise existing mechanisms inflates the corpus without improving the evidence, and shifts
any aggregate statistic while doing so.
