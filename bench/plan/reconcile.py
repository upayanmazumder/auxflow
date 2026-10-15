#!/usr/bin/env python3
"""Reconcile the live GitHub rollout against the validated plan artifact.

The GitHub project/issues are the real deliverable; this tool proves they match
bench/plan/implementation-plan.yaml (the source of truth validated by
validate_plan.py). It reports every drift and exits non-zero if any is found.
It mutates nothing — run post_to_github.py to repair drift.

Checks:
  * every phase issue and sub-issue exists;
  * each sub-issue is natively linked to its phase (addSubIssue);
  * phase issue milestone, labels, and body are in sync with the artifact;
  * the seven milestones exist with the expected titles;
  * the risk-register, deferred-scope, and open-decisions tracking issues exist;
  * Project #8 holds every issue, and phase items carry Phase/Risk/Estimate.
"""

from __future__ import annotations

import json

import post_to_github as P
import yaml


def proj_items(number: int) -> list[dict]:
    out = P.run(
        [
            "gh", "project", "item-list", str(number),
            "--owner", P.OWNER, "--format", "json", "--limit", "500",
        ]
    )
    return json.loads(out).get("items", [])


def phase_milestone_title(plan: dict, key: str) -> str:
    for m in plan["milestones"]:
        if m["key"] == key:
            return m["title"]
    return ""


def main() -> int:
    plan = yaml.safe_load(P.PLAN_PATH.read_text())
    store = P.Store(P.MAP_PATH)
    issues_map = store.data["issues"]
    drift: list[str] = []

    # milestones
    gh_ms = {m["title"] for m in P.gh_api(f"repos/{P.NWO}/milestones?state=all")}
    for m in plan["milestones"]:
        if m["title"] not in gh_ms:
            drift.append(f"milestone missing on GitHub: {m['title']}")

    # phase issues: existence, milestone, labels, body
    phase_recs: dict[int, dict] = {}
    for issue in plan["issues"]:
        rec = issues_map.get(issue["title"])
        if not rec:
            drift.append(f"phase issue not in map: {issue['title']}")
            continue
        phase_recs[issue["phase"]] = rec
        live = P.gh_api(f"repos/{P.NWO}/issues/{rec['number']}")
        want_ms = phase_milestone_title(plan, issue["milestone"])
        got_ms = (live.get("milestone") or {}).get("title")
        if got_ms != want_ms:
            drift.append(f"#{rec['number']} milestone: want {want_ms!r} got {got_ms!r}")
        want_labels = {str(x) for x in issue.get("labels", [])}
        got_labels = {lbl["name"] for lbl in live.get("labels", [])}
        if not want_labels <= got_labels:
            drift.append(f"#{rec['number']} labels missing: {want_labels - got_labels}")
        if P.text_body(live.get("body")) != P.text_body(P.phase_issue_body(issue, plan)):
            drift.append(f"#{rec['number']} body out of sync with artifact")

    # sub-issues: existence + native link to parent
    for issue in plan["issues"]:
        parent = phase_recs.get(issue["phase"])
        if not parent:
            continue
        num = int(parent["number"])
        q = (
            "query($o:String!,$n:String!){repository(owner:$o,name:$n){issue(number:"
            + str(num)
            + "){subIssues(first:50){nodes{number}}}}}"
        )
        linked = P.graphql(q, o=P.OWNER, n=P.REPO)
        child_numbers = {
            node["number"]
            for node in linked["data"]["repository"]["issue"]["subIssues"]["nodes"]
        }
        for sub in issue.get("sub_issues", []):
            title = f"[P{issue['phase']}] {sub['title']}"
            rec = issues_map.get(title)
            if not rec:
                drift.append(f"sub-issue not in map: {title}")
                continue
            if rec["number"] not in child_numbers:
                drift.append(
                    f"sub-issue #{rec['number']} NOT natively linked to phase "
                    f"#{parent['number']}: {title}"
                )

    # tracking issues
    for title in ("Risk register", "Deferred scope and cut order"):
        if title not in issues_map:
            drift.append(f"tracking issue missing: {title}")
    if not any(t.startswith("Open decisions") for t in issues_map):
        drift.append("tracking issue missing: Open decisions")

    # project items + phase field values
    proj = store.data.get("project", {})
    if proj.get("number"):
        items = proj_items(proj["number"])
        titles = {it.get("content", {}).get("title") for it in items}
        for title in issues_map:
            if title not in titles:
                drift.append(f"project item missing: {title}")
        phase_titles = {i["title"]: i for i in plan["issues"]}
        sub_phase = {
            f"[P{i['phase']}] {s['title']}": i["phase"]
            for i in plan["issues"]
            for s in i.get("sub_issues", [])
        }
        for it in items:
            title = it.get("content", {}).get("title")
            if title in phase_titles:
                issue = phase_titles[title]
                if str(it.get("phase")) != str(issue["phase"]):
                    drift.append(f"project Phase wrong for {title}: {it.get('phase')}")
                if it.get("risk") != issue["risk"]:
                    drift.append(f"project Risk wrong for {title}: {it.get('risk')}")
                if it.get("estimate") != issue["hours"]:
                    drift.append(f"project Estimate wrong for {title}: {it.get('estimate')}")
            elif title in sub_phase and str(it.get("phase")) != str(sub_phase[title]):
                drift.append(f"project Phase unset/wrong for sub-issue {title}: {it.get('phase')}")
    else:
        drift.append("project not created")

    if drift:
        print(f"RECONCILE: {len(drift)} drift(s)")
        for d in drift:
            print(f"  - {d}")
        return 1
    print(
        "RECONCILE: clean — "
        f"{len(plan['issues'])} phase issues, "
        f"{sum(len(i.get('sub_issues', [])) for i in plan['issues'])} sub-issues linked, "
        f"{len(plan['milestones'])} milestones, project in sync."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
