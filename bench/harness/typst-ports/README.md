# Hand-ported Typst cross-checks

Per docs/EVALUATION.md: "Reference implementations to run alongside... and
(for the amplifying and oscillating members, ported by hand) Typst." These
are hand ports of the *mechanism*, not the corpus source verbatim -- Typst
has no `\label`/`\pageref`/`\forloop` syntax, so a literal translation is
not possible. Each port reproduces the same page/content feedback the
corresponding LaTeX corpus member exercises, in Typst's own idiom
(`state`, `context`, `here().page()`).

## Ported

| Port | Corpus member | Mechanism | Result |
|---|---|---|---|
| `b08_cycle.typ` | `b08_cycle` (M1) | A loop bounded by a forward page reference, generating a page break per iteration | **`error: loop seems to be infinite`.** Typst's own compiler independently refuses, via its own internal relayout-until-fixpoint bound -- a different implementation reaching the same AMPLIFYING verdict as AuxFlow's static analysis. |
| `b14_ifthen.typ` | `b14_ifthen` (M2) | A page-conditioned font size that can change the label's own page | **Compiles cleanly, 2 pages, no error.** Typst's internal relayout loop finds a genuine fixpoint that LaTeX's write-then-reread `.aux` model cannot see in one pass. This is evidence *for* AuxFlow's own documented over-approximation here: AuxFlow flags this AMPLIFYING "for the wrong reason... nothing changes the *quantity* of content, only its size" (`docs/BENCHMARKS.md`), and Typst's architecture sidesteps the whole mechanism class by construction. |

## Not ported

`b11_width`, `b12_float` and `b13_varioref` are **not ported**. Typst's layout model has no
direct analogue for:

- `b11`: a *resolved reference's rendered width* changing a LaTeX line break, which only exists
  because LaTeX commits to a line break before the reference's final page number is known. Typst
  resolves `here().page()` through its own internal relayout rather than a stale first-pass
  value, so the specific two-pass width-feedback mechanism being tested does not have a
  corresponding failure mode to port.
- `b12`: LaTeX's `[!t]` float-placement algorithm is a LaTeX-specific heuristic with no Typst
  counterpart; Typst's `place()` model does not share it.
- `b13`: `varioref`'s "above/below" text selection is a LaTeX-package-specific mechanism.

Porting these would require inventing a Typst analogue of a LaTeX-specific algorithm rather than
translating one, which would not be a faithful cross-check. This is a disclosed scope limitation,
not an omission: see `docs/EVALUATION.md`'s threats-to-validity section.
