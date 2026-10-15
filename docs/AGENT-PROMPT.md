# Implementation-agent prompt

Paste this to an agent running in **goal mode** to build AuxFlow stage by
stage from the GitHub rollout. Keep it as one standing instruction; the
agent should loop over it until all 16 phase issues are closed.

---

## Prompt

You are implementing AuxFlow in `upayanmazumder/auxflow`, main branch.
Work is already filed on GitHub: **Project #8**, 7 milestones (CP1–CP6 +
Evaluation), 16 phase issues, 58 sub-issues (native GitHub sub-issues of
their phase), a native dependency DAG (`blocked by`), a Risk register
issue, a Deferred-scope/cut-order issue, and an Open-decisions issue.
`docs/` holds the authoritative specification; `bench/plan/` holds the
machine-readable plan and verification tools.

**Goal: close every phase issue, in dependency order, with every sub-issue
merged through its own reviewed PR, CI green throughout.**

### Before anything else

1. Read the **Open decisions** issue. **D13 and D14 block implementation.**
   Do not write analysis code until they are resolved and the decision
   recorded in `docs/PROJECT.md` and the Open-decisions issue body. If you
   cannot resolve them yourself, stop and report the blocker — do not
   silently proceed on an assumed answer.
2. Read `docs/SCOPE.md`, `docs/IMPLEMENTATION-PLAN.md`, and the phase
   issue + its linked docs before writing any code for that phase.
3. Run `make install` then `make lint format-check type test-fast
   plan-validate` once to confirm your environment is clean before you
   start.

### Loop, stage by stage

For each phase issue, in **dependency order** (follow the native `blocked
by` links — a phase issue is not actionable while any blocker is open):

1. `gh issue view <phase-number>` — read the phase body (hours, risk,
   depends-on, acceptance) and its sub-issues (`gh issue list --search
   "is:open [P<phase>] in:title"` or the Project board grouped by `Phase`).
2. Work the phase's sub-issues **one at a time**, each as its own branch
   and PR:
   - `git checkout -b phase-<n>/<short-slug>`
   - Implement exactly what the sub-issue's acceptance criteria state.
     Nothing outside it — no speculative extra scope, no unrelated
     refactors.
   - Add or update tests proving the acceptance criteria (unit tests in
     `tests/unit/`, property tests in `tests/property/` where the plan
     calls for one, golden tests in `tests/golden/`).
   - `make lint format type test-fast` locally; fix until clean.
   - Commit, push, open a PR with the template. **PR title starts with
     `[P<phase>]`.** PR body: `Closes #<sub-issue-number>`.
   - Wait for CI (`CI` workflow) to go green on the PR. Fix forward, don't
     bypass checks.
   - Merge (squash). Closing the PR auto-closes the sub-issue. Confirm the
     sub-issue is closed; if GitHub didn't auto-close it, close it
     manually with a comment linking the merge commit.
3. When **every** sub-issue of a phase is closed:
   - Re-read the phase issue's acceptance criteria as a whole (not just
     the union of sub-issues — some phases have an integration-level
     acceptance check, e.g. phase 8's Gate-1-relevant classifier
     separation, phase 11's b08/b05 guard).
   - If the phase has a **checkpoint** (CP1–CP6) or **gate** in its
     milestone description, verify it explicitly and paste the evidence
     (command output, test names) into a closing comment on the phase
     issue.
   - Close the phase issue, referencing the PRs that completed it.
   - Move the phase's Project items to `Status = Done`.
4. Before moving to the next phase, confirm its blockers are closed (the
   native dependency link will show this) — if a later sub-issue depends
   informally on something not yet merged, do not jump ahead.

### Gates — do not paper over a failure

- **Gate 1** (end of the CP4 milestone, phases 7–9): the classifier must
  separate `b08` (AMPLIFYING, three named facts) from `b05` (not
  amplifying). If it cannot, **stop**, comment on the Open-decisions issue
  and the Gate-4 milestone explaining the failure, and re-propose scope
  per `docs/IMPLEMENTATION-PLAN.md`'s "Gates" section rather than forcing
  a pass.
- **Gate 2** (Evaluation milestone): empirical claim EC1 — predicted run
  count ≥ ground truth for every certified document. If it fails, apply
  the documented conservative fallback (open decision D7) and report the
  failing document as a case study. This is a legitimate result; do not
  tune against the corpus to hide it.
- `b11`–`b13` are **declared false negatives** (expected misclassification
  is correct behaviour); `b15_ibid` is the fourth undetectable member,
  expected `UNKNOWN`. Do not "fix" these to classify correctly — that
  would contradict the documented analysis boundary.

### Hard constraints (from docs/SCOPE.md)

- Never build: a TeX engine, macro expansion, category-code redefinition
  support, full package compatibility, ML prediction, a cluster scheduler,
  a web interface. If a sub-issue seems to need one of these, stop and
  flag it — the sub-issue is wrong, not the constraint.
- The core (lexer, parser, symbol tables, semantic diagnostics, ARG, taint
  analysis, SCC detection, stable-pass numbering, classifier, build-plan
  generation, the planner safety invariant, runtime verification, the
  corpus, the harness) is **never cut**. If time runs short, cut only in
  the order listed in the Deferred-scope issue, and say so explicitly in
  the phase issue you're deferring from.

### Keeping the plan honest

- If implementation reveals the plan was wrong (a sub-issue's acceptance
  criteria don't match reality, a dependency is missing, an estimate is
  far off), **fix `bench/plan/implementation-plan.yaml` first**, run
  `make plan-validate` (must stay at `plan_defects=0`), then run
  `python3 bench/plan/post_to_github.py` to sync the correction to the
  live issues before continuing implementation. Do not let GitHub and the
  artifact drift — `python3 bench/plan/reconcile.py` should stay clean.
- Never edit a phase or sub-issue body directly on GitHub without also
  updating the YAML artifact; the YAML is the source of truth.

### Definition of done

All 16 phase issues closed, all 58 sub-issues closed via merged PRs, `make
lint format-check type test` green on `main`, `bench/plan/reconcile.py`
clean, both gates evaluated and reported (pass or documented fallback),
and `docs/IMPLEMENTATION-PLAN.md` / `docs/SCOPE.md` updated if any open
decision changed during the build.

---
