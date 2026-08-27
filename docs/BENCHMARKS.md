# Benchmark corpus

Ten documents. Each exists to exercise one mechanism; none is filler.

Every document must compile under a stock engine so that dynamic baselines run on identical
input. Documents are committed as sources only — build artifacts are never committed.

## Design rules

1. **One mechanism per document.** If two documents test the same dependency structure, one of
   them is redundant.
2. **Expectations are hand-derived and written before implementation.** `expected.json` is the
   test oracle. Back-filling it from program output would make every subsequent result
   circular.
3. **No performance figures in benchmark metadata.** `expected.json` records structure and
   expected behaviour, never timings.
4. **The realistic document must contain unreachable files**, otherwise dead-file elimination
   has nothing to eliminate and the corresponding claim cannot be tested.

## The corpus

| ID | Document | Purpose | Expected dependency structure | Expected classification |
|---|---|---|---|---|
| `b01_plain` | No labels, references, lists or citations | The simplest case, and the one where a state-comparison detector provably costs an extra run | no facts | CERTIFIED |
| `b02_backref` | A label, then a later reference to it | The minimal auxiliary round trip | one edge, acyclic | CERTIFIED |
| `b03_fwdref` | A reference, then a later label | Confirms direction does not affect the lag | one edge, acyclic | CERTIFIED |
| `b04_chain` | Chained dependencies without generated lists | Forces stable-pass to exceed two by chaining rather than by list feedback | a path of length 3 | CERTIFIED |
| `b05_toc` | Table of contents with many sections, no references | The generated-list path. **Also the document on which engine-warning detection is unsound.** | list extent feeding pagination | CERTIFIED, and explicitly **not** amplifying |
| `b06_bib` | Table of contents, bibliography, page references | The external-tool edge and the deepest ordinary cascade | tool edge then list edge then layout | CERTIFIED |
| `b07_mixed` | Contents, figure list, table list, bibliography | Several interacting list mechanisms at once | multiple list extents sharing one pagination fact | CERTIFIED or BENIGN_CYCLIC |
| `b08_cycle` | A loop bounded by a page reference to a label inside the generated material | **The headline case.** Structure known from the literature not to converge | a cycle containing a STRUCTURAL edge | **AMPLIFYING** |
| `b09_thesis` | Multi-chapter document with contents, lists, bibliography, cross-references, and **unreachable auxiliary files** | Realism; also the document where AuxFlow is expected to provide no saving | several hundred facts, acyclic after abstraction | CERTIFIED |
| `b10_opaque` | An unmodelled package and a non-analysable control sequence | The fallback must degrade rather than crash | facts marked unknown | **UNKNOWN** |

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
    b10_opaque/
    shared/
      refs.bib           shared bibliography database
      auditthesis.cls    minimal document class used by the larger documents
  baselines/
    fixed.sh             baseline A
    warning.sh           baseline B
    checksum.sh          baseline C
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
