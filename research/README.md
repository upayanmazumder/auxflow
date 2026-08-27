# Research notes

Raw evidence and working notes, kept deliberately separate from `docs/`.

- **`docs/`** holds the specification: what the system is, stated once, consistently, and
  written to be implemented against.
- **`research/`** holds the evidence behind it: measurements, source excerpts, search records,
  discarded options and the reasoning that produced the specification.

The separation exists so that the specification stays readable and so that evidence stays
auditable. A claim in `docs/` should be traceable to something here or to a cited primary
source.

## Contents

| File | Purpose |
|---|---|
| `preliminary-measurements.md` | Observations from project scoping. Unpinned environment; must be reproduced before use |
| `prior-art-log.md` | Search records: queries run, sources opened, negative results |
| `decisions/` | One file per resolved open decision, recording what was chosen and why |

Files are added as work proceeds. Nothing here is authoritative.

## Conventions

**Label every claim.** Four categories, used consistently:

- `MEASURED` — observed directly, with the command that produced it recorded.
- `SOURCED` — from a primary source, with a URL and a verbatim quote.
- `REPORTED` — obtained second-hand and not yet confirmed against the primary source.
- `INFERENCE` — analysis, clearly marked as such.

A `REPORTED` item must not be promoted into `docs/` without being verified first.

**Record negative results.** A search that found nothing is evidence, provided the query is
written down. An unrecorded negative result is worthless because it cannot be re-run.

**Keep discarded options.** Knowing why an approach was rejected is more useful six weeks later
than knowing that it was.

**Never delete a measurement because it is inconvenient.** A measurement that contradicts the
design is the most valuable thing in this directory.
