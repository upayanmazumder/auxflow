# TeX-family convergence machinery

Supplementary source record, gathered directly by the audit lead rather than delegated. Audit
date 2026-08-27. Purpose: establish, from primary sources, what the TeX ecosystem itself already
does about convergence detection, since this is the practical baseline AuxFlow is measured
against and any mischaracterisation of it invalidates the comparison.

## Search log

### CTAN
```
query    : rerunfilecheck (package page)
url      : https://ctan.org/pkg/rerunfilecheck
examined : 1 page
outcome  : package title and abstract retrieved verbatim
status   : SOURCED
```

### ConTeXt source repository
```
query    : contextgarden/context scripts/context/lua/mtx-context.lua
url      : https://raw.githubusercontent.com/contextgarden/context/main/scripts/context/lua/mtx-context.lua
examined : full file (86382 bytes), grepped for nofruns|multipass|converg|checksum|stable
outcome  : md5-based multipass convergence loop located and read in full
status   : SOURCED
```

### Web search
```
query    : ConTeXt multipass data .tuc file convergence "additional run" typesetting
examined : ~74 results
outcome  : ConTeXt wiki confirms the multi-pass data concept; no research literature on
           statically deciding ConTeXt pass counts
status   : SOURCED (wiki), NOTHING RELEVANT (research literature)
```

```
query    : "multipass" typesetting convergence detection ConTeXt LuaTeX job.passes tuc
examined : ~38 results
outcome  : NOTHING RELEVANT beyond the wiki and manpage. Surfaced two unrelated patents titled
           "Dynamic typesetting" (US10769348B1, US11334708B2) which were checked and discarded
           — see below.
status   : SOURCED
```

---

## Verified sources

### ConTeXt / `mtx-context.lua` — checksum-based multipass convergence with an oscillation cap

- **Citation.** ConTeXt (mkiv/lmtx) job driver, `scripts/context/lua/mtx-context.lua`, Hans
  Hagen / PRAGMA ADE, ConTeXt source distribution.
- **URL.** `https://raw.githubusercontent.com/contextgarden/context/main/scripts/context/lua/mtx-context.lua`
  (mirror of `https://www.pragma-ade.nl`).
- **Access.** Full source read.
- **Verbatim quote** (lines 351-374):

```lua
-- multipass control

local multipass_suffixes   = { ".tuc" }
local multipass_nofruns    = 9 -- better for tracing oscillation
local multipass_forcedruns = false

local function multipass_hashfiles(jobname)
    local hash = { }
    for i=1,#multipass_suffixes do
        local suffix = multipass_suffixes[i]
        local full = jobname .. suffix
        hash[full] = md5.hex(io.loaddata(full) or "unknown")
    end
    return hash
end

local function multipass_changed(oldhash, newhash)
    for k,v in next, oldhash do
        if v ~= newhash[k] then
            return true
        end
    end
    return false
end
```

  and the driving loop (lines 974-1033, abridged):

```lua
for currentrun=1,maxnofruns do
    ...
    newhash = multipass_hashfiles(jobname)
    if multipass_changed(oldhash,newhash) then
        changed[jobname] = true
        oldhash = newhash
        ...
```

- **Exact contribution.** ConTeXt detects convergence by MD5-hashing its single consolidated
  multipass state file (`.tuc`) after each run and comparing against the previous hash. The
  iteration cap is 9. The inline comment `-- better for tracing oscillation` is a first-party
  acknowledgement that non-converging documents are an expected phenomenon, and that the cap
  exists partly so oscillation can be observed rather than merely aborted.
- **What it does NOT do.** No static analysis of the source. No prediction of the run count. No
  cycle detection. No attribution of a cause when the cap is reached: the only signal is
  `"maxruns"`.
- **Relevance to AuxFlow.** This is the strongest available confirmation that (a) checksum /
  state comparison is the established convergence oracle in the TeX family, not merely a
  `latexmk` idiosyncrasy, and (b) that the ecosystem's own authors treat oscillation as real and
  undiagnosed. It also confirms the structural one-extra-run cost: the loop can only stop after a
  run whose hash matched the previous one.
- **Anticipation verdict.** FULL ANTICIPATION of checksum-based dynamic convergence detection.
  ORTHOGONAL to static analysis. INFORMS the non-convergence framing.
- **Evidence label.** SOURCED.

### `rerunfilecheck` — base LaTeX's rerun warning is insufficient

- **Citation.** Heiko Oberdiek and the Oberdiek Package Support Group / The LaTeX Project Team,
  `rerunfilecheck`, version 1.11, 2025-06-21. LPPL 1.3c.
- **URL.** `https://ctan.org/pkg/rerunfilecheck`
- **Access.** CTAN package page read; PDF documentation not opened in this pass.
- **Verbatim quote.** Package title: "rerunfilecheck – Checksum based rerun checks on auxiliary
  files". Abstract: "The package provides additional rerun warnings if some auxiliary files have
  changed. It is based on MD5 checksum provided by pdfTeX, LuaTeX, XeTeX."
- **Exact contribution.** Adds checksum-based rerun warnings for auxiliary files beyond what the
  LaTeX kernel reports.
- **What it does NOT do.** No static analysis; no run-count prediction; no cause attribution.
- **Relevance to AuxFlow.** The word "additional" is the load-bearing evidence: a package
  maintained by the LaTeX Project Team exists specifically to add rerun detection that the kernel
  does not provide. This supports, from a primary source, the claim that the engine's own warning
  is an incomplete completion signal. It does not by itself prove the kernel warning is *unsound*
  for generated lists — that remains an empirical claim to be measured (see
  `research/preliminary-measurements.md` E1) and the package documentation PDF should be read to
  see whether it states the gap explicitly.
- **Anticipation verdict.** FULL ANTICIPATION of checksum-based auxiliary-change detection inside
  the engine run itself. ORTHOGONAL to static analysis.
- **Evidence label.** SOURCED (title and abstract); the specific claim "base LaTeX misses
  generated-list changes" remains REPORTED pending the PDF.

### Discarded: patents titled "Dynamic typesetting"

- US10769348B1 and US11334708B2, Typetura LLC (later assigned to Kellum and Fitzner), priority
  2019-09-23, status Active. Subject matter is responsive web typography: serving a "typesetting
  package" of fonts and CSS-like rendering rules that adapt text across layout contexts in a
  browser.
- **Relevance to AuxFlow: NONE.** No multi-pass compilation, no dependency analysis, no
  convergence. Recorded only so that the query that surfaced them is not re-run in the belief it
  was never tried.
- **Evidence label.** SOURCED (Google Patents record read).

---

## Negative results

- No research publication was found that statically derives the number of ConTeXt passes, or
  that treats ConTeXt's `.tuc` fixpoint as a static-analysis problem. Queries above.
- No literature was found analysing the *class* of documents for which the TeX-family multipass
  loop fails to converge; the only first-party acknowledgement located is the source comment
  quoted above.

## Summary for the audit

- Checksum-based dynamic convergence detection is not one tool's design choice; it is the
  convergent answer of at least three independent TeX-family systems (`latexmk`, ConTeXt's
  `mtx-context`, and the `rerunfilecheck` package operating inside the engine). AuxFlow must
  present it as the established baseline and must not present its own state comparison as a
  contribution in any form.
- Every one of these caps iteration with a magic constant (ConTeXt: 9). None reports a cause.
  This is direct primary-source support for the diagnostic-gap framing.
- The ConTeXt comment "better for tracing oscillation" is the single most quotable piece of
  first-party evidence that non-convergence is a known, tolerated, undiagnosed condition in
  production typesetting systems.
- The "one extra run" structural cost of consecutive-state comparison is visible in the ConTeXt
  loop and is therefore a property of the mechanism, not of `latexmk`. This strengthens RQ1.
- Nothing here anticipates static pre-execution classification. This area yields no new threat.
