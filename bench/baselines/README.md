# Baselines

Convergence-detection mechanisms under comparison. Specified in
[../../docs/EVALUATION.md](../../docs/EVALUATION.md).

| Script | Baseline | Mechanism |
|---|---|---|
| `fixed.sh` | A | Conventional fixed schedule; no source analysis, no detection |
| `warning.sh` | B | Stops when the engine stops emitting rerun warnings |
| `checksum.sh` | C | Stops when the normalised auxiliary state is unchanged between runs |

Baselines D (static analysis) and E (static analysis with runtime verification) are driven
through the harness rather than through shell scripts, because they need the compiler.

## Why these are shell scripts

So that a reviewer can read in a few lines exactly what was executed. A baseline implemented
inside the harness is harder to audit, and the credibility of the comparison rests entirely on
the baselines being obviously fair.

## Why B is included even though it is unsound

Engine-warning detection misses changes to generated state such as a table of contents. It is
measured precisely so that the gap against ground truth can be quantified. Demonstrating the
unsoundness is a result, not a preliminary.

## Why C is reimplemented rather than delegated

Delegating to an existing build tool would introduce differences in file handling, iteration
caps and normalisation that confound the comparison. Reimplementing means baseline C and
AuxFlow's verifier share identical normalisation and differ only in whether a static prediction
was available.

An existing tool should still be run as an external cross-check, to confirm the reimplementation
behaves as the established one does.

## Requirements

Every script must:

- set deterministic timestamp variables;
- disable shell escape;
- record every command it executes;
- report the number of engine invocations it performed;
- never modify the corpus source directory in place.
