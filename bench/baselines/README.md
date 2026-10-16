# Baselines

Convergence-detection mechanisms under comparison. Specified in
[../../docs/EVALUATION.md](../../docs/EVALUATION.md).

| Script | Baseline | Mechanism |
|---|---|---|
| `fixed.sh` | A | Conventional fixed schedule; no source analysis, no detection |
| `warning.sh` | B | Stops when the engine stops emitting rerun warnings |
| `checksum.sh` | C | Stops when the normalised auxiliary state is unchanged between runs |
| `inputs.sh` | C′ | Stops when the state fed into the next run equals the state fed into the current one, without performing that next run |
| `readwrite.sh` | C″ | Stops when one run's own read-then-written state is unchanged, without needing a further run to confirm it |

Baselines D (static analysis) and E (static analysis with runtime verification) are driven
through the harness rather than through shell scripts, because they need the compiler.

## Why these are shell scripts

So that a reviewer can read in a few lines exactly what was executed. A baseline implemented
inside the harness is harder to audit, and the credibility of the comparison rests entirely on
the baselines being obviously fair. `lib.sh` holds only the pdflatex/bibtex invocation mechanics
shared across baselines; it contains no stopping-condition logic, so it cannot be where a
baseline is accidentally made to look better or worse than it is.

## Why B is included even though it is unsound

Engine-warning detection misses changes to generated state such as a table of contents. It is
measured precisely so that the gap against ground truth can be quantified. Demonstrating the
unsoundness is a result, not a preliminary.

## Why C, C′ and C″ are reimplemented rather than delegated

Delegating to an existing build tool would introduce differences in file handling, iteration
caps and normalisation that confound the comparison. Reimplementing means every baseline and
AuxFlow's own runtime verifier share identical normalisation (`harness/normstate.py`, built on
`auxflow.runtime.normalize`) and differ only in which comparison each performs and when.

`latexmk`, `latexrun` and Tectonic are still run as external cross-checks (see
`harness/reference_tools.py`), to confirm the reimplementations behave as the established tools
do.

## Why C′ and C″ cost one fewer execution than C

C concludes stability by comparing run *k*'s output against run *k-1*'s, so the comparison
baseline starts only after run 1 has produced something to compare against — costing *N*+1 for
an *N*-run document. C′ instead compares what run *k* would read against what run *k-1* read,
with the empty pre-run-1 state as its own baseline, so the comparison starts one run earlier and
costs exactly *N*. C″ reaches the same count by comparing, within a single run, what that run
read at its start against what it wrote by its end — mathematically the same sequence of
comparisons as C′, but available during the run itself rather than only once a further run's
would-be input is known.

## Requirements

Every script must:

- set deterministic timestamp variables (`lib.sh` exports `SOURCE_DATE_EPOCH` and
  `FORCE_SOURCE_DATE`, with a fallback default so a script is self-sufficient even if its caller
  forgot);
- disable shell escape (`-no-shell-escape` on every pdflatex invocation);
- record every command it executes (one `run_<k>.log` per engine pass, `bibtool.log` for
  bibtex/biber);
- report the number of engine invocations it performed (the `runs` field in its one JSON output
  line);
- never modify the corpus source directory in place (the harness stages a fresh copy per
  repetition before mounting it into the container; baselines only ever see the staged copy).
