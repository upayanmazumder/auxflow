---
title: "Build planner"
parent: "Reference"
nav_order: 7
---

# Build planner

Converts an analysis result into an executable plan.

## Terminology

The planner produces a **statically derived execution plan**, also referred to as a
**dependency-aware build plan** or a **derived schedule**.

It does **not** produce a "minimum number of passes". Minimality is not established — see
non-guarantee N4 in [STATIC-ANALYSIS.md](/reference/static-analysis.html). Where a bound is derived it is
*model-minimal*: the shortest the model supports, which may exceed the true requirement. Use
that phrase, or none.

## Plan representation

```python
@dataclass(frozen=True)
class Step:
    tool: str                  # "pdflatex" | "bibtex" | "makeindex" | "spellcheck"
    args: list[str]
    jobname: str
    reason: str                # traceable to a fact or to the classification
    verify_after: bool

@dataclass(frozen=True)
class BuildPlan:
    classification: Literal["CERTIFIED", "BENIGN_CYCLIC", "AMPLIFYING", "UNKNOWN"]
    predicted_runs: int | None
    steps: list[Step]
    max_runs: int              # hard cap for the executor
    stop_condition: Literal["planned_count", "aux_fixpoint", "cap"]
    diagnostics: list[Diagnostic]
    arg_stats: dict            # |V|, |E|, SCC count, analysis_ms
    model_version: str
```

`BuildPlan` is the sole interface between the compiler and the runtime, and it is serialisable
JSON. Everything the executor needs is in it; the executor never re-runs the analysis.

`reason` on every step is required. A plan whose steps cannot be justified is not reviewable,
and `auxflow plan --explain` is one of the project's main demonstration artifacts.

## Lowering rules

Applied in order.

1. **Auxiliary per-file tooling** — emit spell-check or lint steps only over files marked
   reachable in the inclusion graph. Unreachable files cannot affect the output and need not be
   scanned. (Dead-file elimination.)
2. **Bibliography tool** — emit it if and only if citation facts exist *and* a bibliography
   command is present. Place it after the first engine run, which is when its input exists.
   (Dead-tool elimination.)
3. **Index tool** — emit if and only if index facts exist. Optional; only if the construct is
   implemented.
4. **Engine runs** — emit `predicted_runs` steps when the document is certified. Otherwise emit
   the conservative default.
5. **Verification** — set `verify_after` on the final engine step. Always, in every
   classification, including certified.
6. **Amplifying refusal** — emit no steps; emit the diagnosis; exit non-zero unless `--force`.

Spell-check is optional and disabled by default. When enabled, it scans only
files reachable from the entry file. A certified plan uses at least its
predicted count as `max_runs`; the default cap is six.

### Safety invariant

> The emitted plan is never shorter than the conservative default unless the classification is
> `CERTIFIED`.

Implemented as an assertion in the planner, written before any other planner code, and enforced
by a property test over randomly generated classifications. It is the reason an analysis bug
cannot silently corrupt a document: the worst outcome is a plan that is too long.

The conservative floor counts three engine runs. Spell-check, bibliography,
and index steps do not replace engine runs.

## Conservative default plan

```
[spellcheck over reachable files]
pdflatex
[bibtex]
pdflatex
pdflatex
verify; extend while the state is still changing, up to max_runs
```

Chosen to match conventional practice so that a non-certified document is never worse off than
it would have been without AuxFlow.

## Stages, ordering and dependencies

The plan is a linear sequence, not a DAG, for the ordinary single-document case. Ordering
constraints:

- The bibliography tool must follow the run that produced its input and precede the run that
  consumes its output.
- Every engine run depends on the auxiliary state left by the previous step.
- Per-file auxiliary tooling has no ordering constraint against engine runs and is placed first
  so that a failure surfaces before expensive work.

### Parallelism opportunities

Recorded for completeness; none are implemented in the MVP.

- Per-file auxiliary tooling is embarrassingly parallel across reachable files.
- Independent documents are trivially parallel; this is the basis of the stretch work in
  [FUTURE-INFRASTRUCTURE.md](https://github.com/upayanmazumder/auxflow/blob/main/docs/FUTURE-INFRASTRUCTURE.md).
- Engine runs of a single document are inherently sequential — each consumes the previous run's
  output. No amount of analysis changes this, and claiming otherwise would be wrong.

## Stopping conditions

| Condition | Trigger | Action |
|---|---|---|
| `planned_count` | planned runs completed and verification passes | success |
| `aux_fixpoint` | normalised auxiliary state unchanged between runs | success |
| `extend` | planned runs completed but state still changing | perform one more run, up to `max_runs`; **record a prediction miss** |
| `cap` | `max_runs` reached with state still changing | exit non-zero; report suspected non-convergence |

Prediction misses are logged rather than hidden. They are a headline evaluation metric and the
empirical test of assumption A2.

## Failure states

| State | Cause | Behaviour |
|---|---|---|
| `tool_error` | non-zero exit from an external tool | abort; surface the tool log unmodified |
| `missing_input` | a file named in the plan does not exist | abort before executing anything |
| `cap_exceeded` | see above | abort; emit the suspected-non-convergence report |
| `opaque_abort` | `--strict` and classification is `UNKNOWN` | refuse to execute |
| `amplifying_refused` | classification is amplifying, no `--force` | refuse; emit the diagnosis |

Engine logs are never rewritten or filtered. Reformatting an engine error is a good way to hide
the cause of a failure.

## Example

A certified document with a bibliography, derived bound 4:

```json
{
  "classification": "CERTIFIED",
  "predicted_runs": 4,
  "max_runs": 6,
  "stop_condition": "planned_count",
  "model_version": "arg-0.1",
  "arg_stats": { "V": 148, "E": 331, "sccs": 0, "analysis_ms": 41 },
  "steps": [
    { "tool": "pdflatex", "args": [], "jobname": "main",
      "reason": "run 1: emit LABEL_*, TOC_ENTRY, CITE_USE facts",
      "verify_after": false },
    { "tool": "bibtex", "args": [], "jobname": "main",
      "reason": "12 CITE_USE facts and \\bibliography at main.tex:214",
      "verify_after": false },
    { "tool": "pdflatex", "args": [], "jobname": "main",
      "reason": "run 2: BBL.exists (stable_pass 1) consumed",
      "verify_after": false },
    { "tool": "pdflatex", "args": [], "jobname": "main",
      "reason": "run 3: LIST_EXTENT(toc) (stable_pass 3) after the bibliography entry was added",
      "verify_after": false },
    { "tool": "pdflatex", "args": [], "jobname": "main",
      "reason": "run 4: PAGEREF_USE consumes LABEL_PAGE; P=3 so runs=P+1",
      "verify_after": true }
  ],
  "diagnostics": []
}
```

An amplifying document produces `"steps": []`, a populated `diagnostics` array, and a non-zero
exit.
