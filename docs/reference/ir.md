---
title: "Auxiliary Reference Graph"
parent: "Reference"
nav_order: 4
---

# The Auxiliary Reference Graph

The ARG is AuxFlow's intermediate representation. Nodes are **individual auxiliary fact
instances**; edges are dependencies carrying a **pass lag**.

## Why this is an intermediate representation

It satisfies the three properties that distinguish an IR from a data structure that happens to
be a graph:

1. **It is lowered to.** A syntax-directed translation maps AST constructs to facts and edges,
   one rule per modelled construct.
2. **It is analysed and transformed in its own terms.** Taint propagation, SCC detection,
   stable-pass numbering and the classifier all operate on the ARG and never consult the AST.
   This is enforced architecturally: `analysis/` may not import `ast/`.
3. **It is lowered from.** The build planner consumes the ARG and the analysis results and emits
   an executable plan.

It also abstracts: prose, formatting, macro bodies and everything else irrelevant to convergence
are discarded, while source spans are retained so that results can be explained.

Lowering assigns a separate ID to each modelled construct instance. It adds
incoming dependencies once when it completes the graph. Unsupported control
sequences and opaque macro bodies mark the document's facts opaque.

**A design failure to avoid.** An earlier version of this design used fact *kinds* as nodes —
one node for "labels", one for "table of contents entries". That graph is a fixed eight-node
lattice, identical for every document, and computing its height is a lookup table, not an
analysis. **Nodes are instances.** That single decision is what makes the analysis a genuine
dataflow problem.

## Fact

```python
class FactKind(Enum):
    LABEL_NUMBER   = auto()   # \label -> counter value component
    LABEL_PAGE     = auto()   # \label -> page component
    REF_USE        = auto()   # \ref consumer
    PAGEREF_USE    = auto()   # \pageref consumer
    TOC_ENTRY      = auto()
    LOF_ENTRY      = auto()
    LOT_ENTRY      = auto()
    LIST_EXTENT    = auto()   # page footprint of a generated list
    CITE_USE       = auto()
    BBL            = auto()   # bibliography body, produced by an external tool
    INDEX_ENTRY    = auto()   # optional
    IND            = auto()   # optional
    COUNTER_READ   = auto()   # \value{c} appearing in an expression
    CONTENT_VOLUME = auto()   # abstract: the quantity of generated content (pagination)
    OPAQUE         = auto()

Component = Literal["exists", "value"]

@dataclass(frozen=True)
class Fact:
    fact_id: int
    kind: FactKind
    key: str | None            # label or cite key; None for singletons such as CONTENT_VOLUME
    component: Component
    producer: str              # "engine" | "bibtex" | "makeindex"
    consumer: str | None       # tool that reads it, if any
    source_location: Span      # (file_id, start_offset, end_offset) -- mandatory
    stable_pass: int | None    # filled by the analysis; None means not bounded
    dependencies: tuple[int, ...]
    opaque: bool
    metadata: dict             # counter kind, list kind, originating package
```

`source_location` is mandatory on every fact, including synthetic ones such as
`CONTENT_VOLUME` (which points at the construct that established pagination sensitivity). The
diagnostics in [NON-CONVERGENCE.md](/reference/non-convergence.html) are the project's main user-visible
output and they are worthless without spans.

`Fact` rejects a missing or null `source_location`. Fact records and
dependency edges are frozen. Analysis stages keep mutable graph state
separate from these records.

The fact kind set is **open decision D4**. It will be revised once the corpus is authored, on
the principle that a fact kind must be justified by a document that needs it.

## Dependency edge

```python
class DepType(Enum):
    AUX_ROUNDTRIP = auto()  # written to an auxiliary file, read on a later run
    TOOL          = auto()  # mediated by an external program
    LAYOUT        = auto()  # mediated by pagination
    STRUCTURAL    = auto()  # the value influences the QUANTITY of generated content

@dataclass(frozen=True)
class DepEdge:
    source: int
    destination: int
    pass_lag: int          # runs that must elapse before the value is observable
    dependency_type: DepType
    reason: str            # kept in the ARG and plan JSON, described in plain words by reports
```

`reason` is not decoration. It is kept in the serialized graph and plan. Cycle reports and
`auxflow plan --explain` describe it in plain words. Writing it at edge-construction time is the only point where the justification
is actually known.

`STRUCTURAL` is the load-bearing edge type. It is never produced by the lowering rules directly;
it is added by the taint analysis (see [STATIC-ANALYSIS.md](/reference/static-analysis.html)).

## What `pass_lag` means

Let an execution be a sequence of engine runs *r₁, r₂, …*. Let *A_k* be the auxiliary state
after run *k*, with *A₀* empty. Run *k* reads *A_{k−1}* and writes *A_k*; it cannot read what it
is in the middle of writing.

For a fact *f*, write *valₖ(f)* for its value in *A_k*. Then

```
val_k(f) = F_f(A_{k-1})
```

for a function *F_f* determined by the document. An edge *g → f* with `pass_lag = 1` records
that *F_f* reads *val(g)*.

Define *f* to be **stable at pass p** when *valₖ(f) = val_p(f)* for every *k ≥ p*. Then

```
stable_pass(f) = 1                                    if f has no dependencies
stable_pass(f) = 1 + max over g in deps(f) of
                     ( stable_pass(g) + pass_lag(g -> f) - 1 )    otherwise
```

which for the ordinary case `pass_lag = 1` reduces to `1 + max(stable_pass(g))`.

Let *P* be the maximum of `stable_pass` over all facts, and 0 when there are none. Then *A_P* is
the fixpoint, and since a run produces correct output exactly when it reads the fixpoint:

```
required runs = P + 1
```

### The `exists` / `value` split

Every list-producing fact is split into two nodes:

- **`exists`** — whether the fact is present, and its contribution to content volume. Determined
  by document *structure*, not by any fact value. A `\section` produces exactly one table-of-
  contents entry whatever the page numbers are.
- **`value`** — the page number or counter recorded.

`CONTENT_VOLUME` depends only on `exists` components. `LABEL_PAGE.value` depends on
`CONTENT_VOLUME`. `PAGEREF_USE` depends on `LABEL_PAGE.value`.

Lowering creates one `CONTENT_VOLUME` fact for the source document and links
each list entry's `exists` node to its list extent. The extent links to
`CONTENT_VOLUME`. `CONTENT_VOLUME` links to each entry's `value` node.
A bibliography adds a `BBL.exists` fact and a contents entry.

**Without this split the analysis is vacuous.** `TOC_ENTRY.value → CONTENT_VOLUME →
TOC_ENTRY.value` is a cycle, so every document containing a table of contents would be
classified cyclic and no bound could ever be computed. With the split, ordinary documents are
acyclic, while genuine amplifying feedback still forms a cycle because it passes through a
`STRUCTURAL` edge.

This is an abstraction, and it is not faithful — see limitation L2 in [PROJECT.md](/project/specification.html).
It is stated explicitly rather than buried because it is the assumption most likely to be
attacked.

## Examples

### Backward reference, no generated lists

```latex
\chapter{One}\label{c:one}
...
\chapter{Two} Refer to Chapter~\ref{c:one}.
```

| fact | deps | stable_pass |
|---|---|---|
| `LABEL_NUMBER(c:one).value` | none | 1 |
| `REF_USE(c:one)` | `LABEL_NUMBER(c:one)` via AUX_ROUNDTRIP lag 1 | 2 |

`REF_USE` is a consumer rendered into output, not a fact stored in the auxiliary file, so
*P* = 1 and the document needs **2** runs.

### Table of contents

```latex
\tableofcontents
\section{...} x 40
```

| fact | deps | stable_pass |
|---|---|---|
| `TOC_ENTRY(i).exists` | none (structural) | 1 |
| `LIST_EXTENT(toc)` | all `TOC_ENTRY(i).exists`, LAYOUT lag 0 | 1 |
| `CONTENT_VOLUME` | `LIST_EXTENT(toc)`, LAYOUT lag 1 | 2 |
| `LABEL_PAGE(*).value`, `TOC_ENTRY(i).value` | `CONTENT_VOLUME`, LAYOUT lag 0 | 2 |

*P* = 2, so **3** runs. Note the shape of the argument: the list is typeset in run 2 from the
file written in run 1, which shifts pagination, and the corrected pages are recorded in the same
run they are determined.

### Bibliography cascade

```latex
\tableofcontents
... \cite{k} ...
\bibliography{refs}
```

| fact | deps | stable_pass |
|---|---|---|
| `CITE_USE(k)` | none | 1 |
| `BBL.exists` | `CITE_USE(*)`, TOOL lag 1 | 1 (external tool runs after run 1) |
| `TOC_ENTRY(bib).exists` | `BBL.exists`, LAYOUT lag 1 | 2 |
| `LIST_EXTENT(toc)` | `TOC_ENTRY(*).exists` | 2 |
| `CONTENT_VOLUME` | `LIST_EXTENT(toc)`, lag 1 | 3 |
| `LABEL_PAGE(*).value` | `CONTENT_VOLUME` | 3 |
| `PAGEREF_USE(*)` | `LABEL_PAGE`, AUX_ROUNDTRIP lag 1 | 4 |

*P* = 3, so **4** runs — one more than the conventional fixed schedule performs. The chain is
three links deep and every link is document-dependent, which is the evidence that instance-level
facts carry information a fixed lattice could not.

The exact lag semantics for the `TOOL` edge is **open decision D5**.

### Amplifying cycle

```latex
\newcounter{n}
\forloop{n}{0}{\value{n} < \pageref{l}}{~\newpage}
Last page label here\label{l}.
```

| edge | type |
|---|---|
| `LABEL_PAGE(l) → PAGEREF_USE(l)` | AUX_ROUNDTRIP lag 1 |
| `PAGEREF_USE(l) → CONTENT_VOLUME` | **STRUCTURAL** (added by taint: the value bounds a loop that emits pages) |
| `CONTENT_VOLUME → LABEL_PAGE(l)` | LAYOUT |

A cycle containing a `STRUCTURAL` edge. `stable_pass` is undefined for all three facts and the
document is classified amplifying. Contrast the table-of-contents example, which is also
feedback but contains no `STRUCTURAL` edge and receives a bound.

## Serialisation

The ARG serialises to JSON for tests and to Graphviz DOT for inspection (`auxflow graph`). DOT
output colours nodes by component and edges by dependency type, so that a benign cycle and an
amplifying one are visually distinct — this is the single most useful debugging artifact in the
project and is worth building early.
