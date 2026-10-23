"""publish_queue.py - list or pick queued insight PRs for scheduled publishing.

A queued article is an open PR labelled ``scheduled-publish`` whose branch adds
exactly one manifest under ``publish-queue/<slug>.json``. The manifest's
``publish_on`` date (YYYY-MM-DD, UTC) is the single source of truth for when it
goes live. PRs also labelled ``publish-blocked`` are skipped until a person
clears the label.

Commands:
  list   print the queue in publish order (for people)
  pick   print GitHub Actions outputs for the next due PR, or nothing if none
         is due: pr, head, slug, title, date

``pick`` returns at most one PR per run, so a daily schedule publishes at most
one article per day; a backlog drains one day at a time.

Needs ``gh`` (authenticated) and ``git`` with ``origin`` fetched.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys

LABEL = "scheduled-publish"
BLOCKED = "publish-blocked"


def run(*cmd: str) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def queued() -> list[dict]:
    prs = json.loads(run("gh", "pr", "list", "--label", LABEL, "--state", "open", "--limit", "100",
                         "--json", "number,headRefName,title,labels"))
    items = []
    for pr in prs:
        labels = {label["name"] for label in pr["labels"]}
        head = pr["headRefName"]
        run("git", "fetch", "--quiet", "origin", f"+refs/heads/{head}:refs/remotes/origin/{head}")
        names = run("git", "diff", "--name-only", "--diff-filter=A", f"origin/main...origin/{head}",
                    "--", "publish-queue/").split()
        manifests = [n for n in names if n.endswith(".json")]
        item = {"pr": pr["number"], "head": head, "title": pr["title"], "blocked": BLOCKED in labels}
        if len(manifests) != 1:
            item["error"] = f"expected one publish-queue manifest, found {len(manifests)}"
        else:
            manifest = json.loads(run("git", "show", f"origin/{head}:{manifests[0]}"))
            item.update(slug=manifest.get("slug", ""), date=manifest.get("publish_on", ""))
            try:
                dt.date.fromisoformat(item["date"])
            except ValueError:
                item["error"] = f"bad publish_on {item['date']!r}"
        items.append(item)
    return sorted(items, key=lambda i: (i.get("date", "9999"), i["pr"]))


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    items = queued()
    if cmd == "list":
        for i in items:
            state = "ERROR: " + i["error"] if "error" in i else ("blocked" if i["blocked"] else
                                                                 ("due" if i["date"] <= today else "scheduled"))
            print(f"{i.get('date', '?'):10}  #{i['pr']:<5} {state:10} {i.get('slug', '?')}")
        return 0
    if cmd == "pick":
        for i in items:
            if "error" in i or i["blocked"]:
                continue
            if i["date"] <= today:
                for key in ("pr", "head", "slug", "title"):
                    print(f"{key}={i[key]}")
                print(f"date={today}")
                return 0
        return 0
    sys.exit(f"unknown command {cmd!r} (use list or pick)")


if __name__ == "__main__":
    sys.exit(main())
