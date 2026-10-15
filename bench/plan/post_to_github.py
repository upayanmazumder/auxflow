#!/usr/bin/env python3
"""Post the AuxFlow implementation plan to GitHub.

Reads bench/plan/implementation-plan.yaml (validated by validate_plan.py) and
creates, idempotently and resumably:

  * one label per area,
  * seven checkpoint milestones (CP1-CP6 + Evaluation),
  * sixteen phase issues with accurate hours/risk/dependencies,
  * fifty-eight sub-issues, each linked to its phase via the native
    ``addSubIssue`` GraphQL mutation,
  * a Project v2 board with Phase / Risk / Estimate fields and every issue
    added as an item.

State is persisted to bench/plan/github-map.json after every create, so a
re-run skips work already done. Requires an authenticated ``gh`` with
``repo`` and ``project`` scopes.

Usage:
    python3 bench/plan/post_to_github.py           # full run
    python3 bench/plan/post_to_github.py --no-project   # skip the board
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

OWNER = "upayanmazumder"
REPO = "auxflow"
NWO = f"{OWNER}/{REPO}"

HERE = Path(__file__).resolve().parent
PLAN_PATH = HERE / "implementation-plan.yaml"
MAP_PATH = HERE / "github-map.json"

AREA_COLORS = {
    "phase": "1f6feb",
    "infra": "6e7781",
    "safety": "d73a4a",
    "lexer": "0e8a16",
    "parser": "b60205",
    "ast": "5319e7",
    "symbol-table": "0052cc",
    "semantic": "006b75",
    "ir": "5319e7",
    "analysis": "fbca04",
    "planner": "c2e0c6",
    "cli": "bfdadc",
    "test": "d4c5f9",
    "benchmarks": "f9d0c4",
    "task": "ededed",
}


def run(cmd: list[str], *, stdin: str | None = None, check: bool = True) -> str:
    proc = subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{proc.stderr}")
    return proc.stdout


def text_body(value: object) -> str:
    # Normalise line endings and trailing space for stable body comparison.
    text = value if isinstance(value, str) else ""
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def gh_api(path: str, method: str = "GET", fields: dict | None = None) -> object:
    cmd = ["gh", "api", "-X", method, path]
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"] if isinstance(value, str) else ["-F", f"{key}={value}"]
    out = run(cmd)
    return json.loads(out) if out.strip() else None


def graphql(query: str, **variables: str) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        cmd += ["-f", f"{key}={value}"]
    return json.loads(run(cmd))


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict = {
            "labels": [],
            "milestones": {},  # key -> number
            "issues": {},      # title -> {number, node_id}
            "sub_links": [],   # list of "parent#child"
            "project": {},     # number, id, url, fields, items(title->item_id)
        }
        if path.is_file():
            self.data.update(json.loads(path.read_text()))

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2))


def repo_node_id() -> str:
    data = graphql(
        'query($o:String!,$n:String!){repository(owner:$o,name:$n){id}}',
        o=OWNER,
        n=REPO,
    )
    return data["data"]["repository"]["id"]


def load_existing_issues() -> dict[str, dict]:
    """title -> {number, node_id} for every issue already in the repo."""
    result: dict[str, dict] = {}
    page = 1
    while True:
        batch = gh_api(
            f"repos/{NWO}/issues?state=all&per_page=100&page={page}"
        )
        if not batch:
            break
        for item in batch:
            if "pull_request" in item:
                continue
            result[item["title"]] = {
                "number": item["number"],
                "node_id": item["node_id"],
            }
        if len(batch) < 100:
            break
        page += 1
    return result


def ensure_labels(plan: dict, store: Store) -> None:
    names: set[str] = set()
    for issue in plan["issues"]:
        names.update(str(x) for x in issue.get("labels", []))
        for sub in issue.get("sub_issues", []):
            names.update(str(x) for x in sub.get("labels", []))
    for name in sorted(names):
        if name in store.data["labels"]:
            continue
        color = AREA_COLORS.get(name, "ededed")
        run(
            [
                "gh", "label", "create", name,
                "--repo", NWO, "--color", color, "--force",
            ]
        )
        store.data["labels"].append(name)
        store.save()
        print(f"label  {name}")


def ensure_milestones(plan: dict, store: Store) -> dict[str, int]:
    existing = {m["title"]: m["number"] for m in gh_api(f"repos/{NWO}/milestones?state=all")}
    key_to_number: dict[str, int] = {}
    for ms in plan["milestones"]:
        title = ms["title"]
        if title in existing:
            number = existing[title]
        else:
            created = gh_api(
                f"repos/{NWO}/milestones",
                method="POST",
                fields={"title": title, "description": ms.get("description", "")},
            )
            number = created["number"]
            print(f"milestone  {title}")
        key_to_number[ms["key"]] = number
        store.data["milestones"][ms["key"]] = number
    store.save()
    return key_to_number


def phase_issue_body(issue: dict, plan: dict) -> str:
    deps = issue.get("depends_on", [])
    names = {i["phase"]: i["title"] for i in plan["issues"]}
    dep_txt = (
        ", ".join(f"phase {d} ({names.get(d, '').split(' — ')[-1]})" for d in deps)
        if deps
        else "none"
    )
    meta = (
        f"\n\n---\n"
        f"**Phase:** {issue['phase']}  |  "
        f"**Estimate:** {issue['hours']} h  |  "
        f"**Risk:** {issue['risk']}  |  "
        f"**Milestone:** {issue['milestone']}\n\n"
        f"**Depends on:** {dep_txt}\n"
    )
    gate = ""
    if issue["phase"] == 1:
        blockers = [
            d["id"]
            for d in (plan.get("decisions") or {}).get("items", [])
            if d.get("blocks_implementation")
        ]
        if blockers:
            gate = (
                f"\n\n> **Gate:** docs/PROJECT.md forbids starting implementation until "
                f"{' and '.join(blockers)} are resolved. See the Open decisions issue.\n"
            )
    return issue["body"].strip() + meta + gate


def create_issue(
    title: str,
    body: str,
    labels: list[str],
    milestone: int | None,
    store: Store,
    existing: dict[str, dict],
) -> dict:
    def _sync_body(rec: dict) -> dict:
        # Keep the live issue body in step with the plan artifact.
        current = gh_api(f"repos/{NWO}/issues/{rec['number']}")
        if text_body(current.get("body")) != text_body(body):
            gh_api(
                f"repos/{NWO}/issues/{rec['number']}",
                method="PATCH",
                fields={"body": body},
            )
            print(f"update #{rec['number']}  {title}")
        return rec

    if title in store.data["issues"]:
        return _sync_body(store.data["issues"][title])
    if title in existing:
        store.data["issues"][title] = existing[title]
        store.save()
        return _sync_body(existing[title])
    payload: dict = {"title": title, "body": body, "labels": labels}
    if milestone is not None:
        payload["milestone"] = milestone
    cmd = ["gh", "api", "-X", "POST", f"repos/{NWO}/issues", "--input", "-"]
    out = run(cmd, stdin=json.dumps(payload))
    created = json.loads(out)
    rec = {"number": created["number"], "node_id": created["node_id"]}
    store.data["issues"][title] = rec
    store.save()
    print(f"issue  #{rec['number']}  {title}")
    return rec


def issue_db_id(number: int, cache: dict[int, int]) -> int:
    if number not in cache:
        cache[number] = gh_api(f"repos/{NWO}/issues/{number}")["id"]
    return cache[number]


def post_dependencies(plan: dict, phase_recs: dict[int, dict]) -> None:
    """Wire each phase issue's depends_on as a native 'blocked by' dependency."""
    id_cache: dict[int, int] = {}
    for issue in plan["issues"]:
        blocked = phase_recs.get(issue["phase"])
        if not blocked:
            continue
        existing_blockers = {
            d["number"]
            for d in gh_api(
                f"repos/{NWO}/issues/{blocked['number']}/dependencies/blocked_by"
            )
        }
        for dep_phase in issue.get("depends_on", []):
            blocker = phase_recs.get(dep_phase)
            if not blocker or blocker["number"] in existing_blockers:
                continue
            run(
                [
                    "gh", "api", "-X", "POST",
                    f"repos/{NWO}/issues/{blocked['number']}/dependencies/blocked_by",
                    "-F", f"issue_id={issue_db_id(blocker['number'], id_cache)}",
                ]
            )
            print(f"dep  #{blocked['number']} blocked_by #{blocker['number']}")


def link_sub_issue(parent: dict, child: dict, store: Store) -> None:
    key = f"{parent['number']}#{child['number']}"
    if key in store.data["sub_links"]:
        return
    graphql(
        "mutation($p:ID!,$c:ID!){addSubIssue(input:{issueId:$p,subIssueId:$c}){issue{number}}}",
        p=parent["node_id"],
        c=child["node_id"],
    )
    store.data["sub_links"].append(key)
    store.save()
    print(f"  sub-issue #{child['number']} -> #{parent['number']}")


def ensure_project(plan: dict, store: Store) -> None:
    proj = store.data["project"]
    if not proj.get("number"):
        out = run(
            [
                "gh", "project", "create",
                "--owner", OWNER,
                "--title", plan["project"]["name"],
                "--format", "json",
            ]
        )
        created = json.loads(out)
        proj.update(
            {
                "number": created["number"],
                "id": created["id"],
                "url": created["url"],
                "fields": {},
                "items": {},
            }
        )
        store.save()
        print(f"project  #{proj['number']}  {proj['url']}")

    # custom fields
    want_fields = {"Phase": "TEXT", "Risk": "TEXT", "Estimate": "NUMBER"}
    existing_fields = json.loads(
        run(
            [
                "gh", "project", "field-list", str(proj["number"]),
                "--owner", OWNER, "--format", "json",
            ]
        )
    )["fields"]
    by_name = {f["name"]: f for f in existing_fields}
    for name, dtype in want_fields.items():
        if name in by_name:
            proj["fields"][name] = by_name[name]["id"]
            continue
        out = run(
            [
                "gh", "project", "field-create", str(proj["number"]),
                "--owner", OWNER, "--name", name, "--data-type", dtype,
                "--format", "json",
            ]
        )
        proj["fields"][name] = json.loads(out)["id"]
        store.save()
        print(f"project field  {name}")

    # add every issue as an item; set fields for phase issues, Phase for sub-issues
    phase_titles = {i["title"]: i for i in plan["issues"]}
    sub_phase = {
        f"[P{i['phase']}] {s['title']}": i["phase"]
        for i in plan["issues"]
        for s in i.get("sub_issues", [])
    }
    for title, rec in list(store.data["issues"].items()):
        url = f"https://github.com/{NWO}/issues/{rec['number']}"
        item_id = proj["items"].get(title)
        if not item_id:
            out = run(
                [
                    "gh", "project", "item-add", str(proj["number"]),
                    "--owner", OWNER, "--url", url, "--format", "json",
                ]
            )
            item_id = json.loads(out)["id"]
            proj["items"][title] = item_id
            store.save()
        if title in phase_titles:
            issue = phase_titles[title]
            _set_text(proj, item_id, "Phase", str(issue["phase"]))
            _set_text(proj, item_id, "Risk", issue["risk"])
            _set_number(proj, item_id, "Estimate", issue["hours"])
        elif title in sub_phase:
            _set_text(proj, item_id, "Phase", str(sub_phase[title]))
    print(f"project items: {len(proj['items'])}")
    store.save()


def _set_text(proj: dict, item_id: str, field: str, value: str) -> None:
    run(
        [
            "gh", "project", "item-edit",
            "--project-id", proj["id"], "--id", item_id,
            "--field-id", proj["fields"][field], "--text", value,
        ]
    )


def _set_number(proj: dict, item_id: str, field: str, value: int) -> None:
    run(
        [
            "gh", "project", "item-edit",
            "--project-id", proj["id"], "--id", item_id,
            "--field-id", proj["fields"][field], "--number", str(value),
        ]
    )


def post_risk_register(plan: dict, store: Store, existing: dict[str, dict]) -> None:
    rows = plan.get("risk_register", [])
    if not rows:
        return
    run(["gh", "label", "create", "risk", "--repo", NWO, "--color", "b60205", "--force"])
    lines = [
        "The eight risks from docs/IMPLEMENTATION-PLAN.md, tracked for the 5-day build.",
        "",
        "| # | Risk | Likelihood | Impact | Mitigation |",
        "|---|---|---|---|---|",
    ]
    for n, r in enumerate(rows, 1):
        lines.append(
            f"| {n} | {r['risk']} | {r['likelihood']} | {r['impact']} | {r['mitigation']} |"
        )
    create_issue("Risk register", "\n".join(lines), ["risk"], None, store, existing)


def post_deferred(plan: dict, store: Store, existing: dict[str, dict]) -> None:
    d = plan.get("deferred") or {}
    if not d:
        return
    run(["gh", "label", "create", "deferred", "--repo", NWO, "--color", "fef2c0", "--force"])
    lines = [d.get("note", ""), ""]
    for heading, key in (
        ("## SHOULD build (after the core)", "should"),
        ("## STRETCH (after MUST item 16)", "stretch"),
        ("## Cut order (drop first -> last if time runs short)", "cut_order"),
    ):
        lines.append(heading)
        for item in d.get(key, []):
            lines.append(f"- {item}")
        lines.append("")
    create_issue(
        "Deferred scope and cut order", "\n".join(lines), ["deferred"], None, store, existing
    )


def post_decisions(plan: dict, store: Store, existing: dict[str, dict]) -> None:
    d = plan.get("decisions") or {}
    items = d.get("items", [])
    if not items:
        return
    run(["gh", "label", "create", "decision", "--repo", NWO, "--color", "0e8a16", "--force"])
    run(["gh", "label", "create", "blocker", "--repo", NWO, "--color", "b60205", "--force"])
    lines = [d.get("note", ""), "", "| ID | Status | Blocks impl. | Question | Resolve by |",
             "|---|---|---|---|---|"]
    for it in items:
        blocks = "YES" if it.get("blocks_implementation") else "-"
        phase = it.get("resolve_by_phase")
        resolve = "before Phase 1" if phase == 0 else f"phase {phase}"
        lines.append(
            f"| {it['id']} | {it['status']} | {blocks} | {it['question']} | {resolve} |"
        )
    blockers = [it["id"] for it in items if it.get("blocks_implementation")]
    labels = ["decision"] + (["blocker"] if blockers else [])
    title = "Open decisions" + (f" (blocks impl.: {', '.join(blockers)})" if blockers else "")
    create_issue(title, "\n".join(lines), labels, None, store, existing)


def main(argv: list[str]) -> int:
    plan = yaml.safe_load(PLAN_PATH.read_text())
    store = Store(MAP_PATH)
    existing = load_existing_issues()

    ensure_labels(plan, store)
    key_to_ms = ensure_milestones(plan, store)

    # phase issues
    phase_recs: dict[int, dict] = {}
    for issue in plan["issues"]:
        rec = create_issue(
            issue["title"],
            phase_issue_body(issue, plan),
            [str(x) for x in issue.get("labels", [])],
            key_to_ms.get(issue["milestone"]),
            store,
            existing,
        )
        phase_recs[issue["phase"]] = rec

    post_dependencies(plan, phase_recs)

    # sub-issues + native links
    for issue in plan["issues"]:
        parent = phase_recs[issue["phase"]]
        for sub in issue.get("sub_issues", []):
            title = f"[P{issue['phase']}] {sub['title']}"
            child = create_issue(
                title,
                sub.get("body", "").strip() + f"\n\n---\nSub-issue of: {issue['title']}",
                [str(x) for x in sub.get("labels", [])],
                key_to_ms.get(issue["milestone"]),
                store,
                existing,
            )
            link_sub_issue(parent, child, store)

    post_risk_register(plan, store, existing)
    post_deferred(plan, store, existing)
    post_decisions(plan, store, existing)

    if "--no-project" not in argv:
        ensure_project(plan, store)

    print("\nDone.")
    print(f"  milestones: {len(store.data['milestones'])}")
    print(f"  issues:     {len(store.data['issues'])}")
    print(f"  sub-links:  {len(store.data['sub_links'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
