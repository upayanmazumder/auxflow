# Scripts

Developer utilities. Nothing here is part of the compiler, and nothing here is required to
reproduce a result — reproduction goes through `bench/harness/`.

Intended contents as the project proceeds:

| Script | Purpose |
|---|---|
| `dev-setup.sh` | Create a virtual environment and install development extras |
| `pull-image.sh` | Pull and verify the pinned container image by digest |
| `render-graph.sh` | Run `auxflow graph` over a document and render the DOT output |
| `check-claims.sh` | Grep the documentation for forbidden claim phrasings |

`check-claims.sh` is worth writing early. The forbidden phrasings are listed in
[../docs/PATENT-NOTES.md](../docs/PATENT-NOTES.md); a mechanical check is more reliable than
remembering them while writing a report at the end of a semester.
