# Prior-art search log

Record of what was searched, where, and what was found — including nothing. A negative result is
evidence only if the query is written down and can be re-run.

Labels follow [README.md](README.md): `MEASURED`, `SOURCED`, `REPORTED`, `INFERENCE`.

## Format

Each entry records the date, the source searched, the exact query, the number of results
examined, and the outcome. Entries are appended, never edited; a superseded finding gets a new
entry that references the old one.

```
### YYYY-MM-DD  <source>
query    : <exact query string>
examined : <n> results
outcome  : <finding, or NOTHING RELEVANT>
status   : SOURCED | REPORTED
```

## Established findings

Summarised in [../docs/RELATED-WORK.md](../docs/RELATED-WORK.md) with verification status per
item. Items marked `reported` there are listed below as outstanding.

## Outstanding verification

Must be confirmed against primary sources before appearing in a report:

- The two patents on statically bounding fixpoint iterations — confirm numbers, assignees,
  filing and grant dates, current legal status, and the exact wording of the independent claims.
- Räihä and Ukkonen (ICALP 1980) — currently known only through a citation in another paper's
  reference list.
- The complexity result on deciding pure multipass membership.
- The documented iteration cap and checksum mechanism in the established build tool — quote the
  manual directly.
- The three negative results recorded in `docs/RELATED-WORK.md`. Each needs a reproducible query
  before it can be asserted in writing.

## Searches worth repeating before publication

The prior-art landscape moves. Re-run before submission:

- Static determination of build or pass schedules for document compilation.
- Cross-reference dependency extraction from markup languages.
- Detection of non-convergent or oscillating layout fixpoints.
- Classification of feedback in incremental or fixpoint-based build systems.
