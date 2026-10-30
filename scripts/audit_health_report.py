#!/usr/bin/env python3
"""
Health report for the hosted Architecture Audit (/audit/ and api.mnemehq.com).

Writes a Markdown report with five sections:

  1. Funnel. Session-level steps from GA4: CTA click, landing, workspace,
     input, start, complete, error. Sessions flagged debug_mode and
     localhost traffic are excluded. One flag per session (MAX), so
     duplicate tags do not inflate counts.
  2. Errors. audit_error by error_code and stage. A missing_input count
     above the number of starts means visitors are pressing Run with
     nothing entered.
  3. Entry. Where visitors arrive from: traffic source of /audit/ landings,
     the pages and positions of cta_intent="audit" clicks, and internal
     referrers.
  4. Backend. API exposure probe first. An anonymous GET of the project list
     must be refused (401/403). A 200 means the data-handling page's
     operator-only access claim is false, and the report says FAIL. Then it
     lists stored projects and audits, splitting internal repositories
     (MnemeHQ, test fixtures) from outside users.
  5. Pilot thresholds. The 30-day ADR checker thresholds agreed on
     2026-10-29, compared with the trailing 30 days of the full Audit.

Requires the `bq` CLI with access to mneme-hq-prod. The backend section
uses MNEME_AUDIT_OPERATOR_TOKEN as a Bearer token when set. If the API
refuses anonymous reads and no token is set, the section is skipped.

GA4 traps (see the analytics data-sources notes): enumerate events instead
of filtering to a remembered list; canonical tagging starts 2026-08-30; a
NOT IN over a subquery that yields NULL returns no rows, so session ids are
NULL-guarded.

Usage:
  python scripts/audit_health_report.py                  # since 2026-08-30
  python scripts/audit_health_report.py --since 20261001
  python scripts/audit_health_report.py --skip-backend
  python scripts/audit_health_report.py --out report.md
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

TABLE = "mneme-hq-prod.analytics_534820916.events_*"
API = "https://api.mnemehq.com"
GA4_START = "20260830"
INTERNAL_OWNERS = {"MnemeHQ"}
INTERNAL_LOCATORS = {"test/repo"}
# ADR checker pilot, agreed 2026-10-29 (30-day thresholds).
THRESHOLDS = {"started": 30, "completed": 20, "cta_to_audit": 4}

PARAM = "(SELECT value.{t}_value FROM UNNEST(event_params) WHERE key='{k}')"


def p(key: str, kind: str = "string") -> str:
    return PARAM.format(t=kind, k=key)


def bq(sql: str) -> list[dict]:
    out = subprocess.run(
        ["bq", "query", "--quiet", "--use_legacy_sql=false", "--format=json", "--max_rows=1000"],
        input=sql, capture_output=True, text=True, shell=os.name == "nt",
    )
    if out.returncode != 0:
        sys.exit(f"bq failed:\n{out.stderr or out.stdout}")
    text = out.stdout.strip()
    return json.loads(text) if text else []


def table(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "") if r.get(c) is not None else "") for c in cols) + " |")
    return "\n".join(lines) + "\n"


def sessions_cte(since: str) -> str:
    return f"""
WITH e AS (
  SELECT CONCAT(user_pseudo_id, '-', CAST({p('ga_session_id', 'int')} AS STRING)) s,
         event_name, PARSE_DATE('%Y%m%d', event_date) d,
         {p('page_location')} loc, {p('debug_mode', 'int')} dbg, {p('cta_intent')} intent
  FROM `{TABLE}` WHERE _TABLE_SUFFIX >= '{since}'),
excluded AS (
  SELECT DISTINCT s FROM e
  WHERE s IS NOT NULL AND (dbg = 1 OR loc LIKE '%localhost%' OR loc LIKE '%127.0.0.1%')),
f AS (
  SELECT s, FORMAT_DATE('%Y-%m', MIN(d)) m,
    MAX(IF(event_name = 'cta_click' AND intent = 'audit' AND loc NOT LIKE '%/audit%', 1, 0)) cta_to_audit,
    MAX(IF(event_name = 'page_view' AND REGEXP_CONTAINS(loc, r'mnemehq\\.com/audit/?(\\?|#|$)'), 1, 0)) landing,
    MAX(IF(event_name = 'page_view' AND loc LIKE '%/audit/workspace%', 1, 0)) workspace,
    MAX(IF(event_name = 'audit_input_selected', 1, 0)) input_selected,
    MAX(IF(event_name = 'audit_start', 1, 0)) started,
    MAX(IF(event_name = 'audit_complete', 1, 0)) completed,
    MAX(IF(event_name = 'audit_error', 1, 0)) errored
  FROM e
  WHERE s IS NOT NULL AND s NOT IN (SELECT s FROM excluded)
  GROUP BY s)"""


FUNNEL_COLS = ["cta_to_audit", "landing", "workspace", "input_selected", "started", "completed", "errored"]


def funnel(since: str) -> str:
    sums = ", ".join(f"COUNTIF({c} = 1) {c}" for c in FUNNEL_COLS)
    rows = bq(sessions_cte(since) + f"""
SELECT IFNULL(m, 'TOTAL') month, {sums}
FROM f GROUP BY ROLLUP(m) ORDER BY month""")
    return table(rows, ["month"] + FUNNEL_COLS)


def trailing_30(today: date) -> dict:
    since = (today - timedelta(days=30)).strftime("%Y%m%d")
    sums = ", ".join(f"COUNTIF({c} = 1) {c}" for c in FUNNEL_COLS)
    rows = bq(sessions_cte(since) + f"\nSELECT {sums} FROM f")
    return {k: int(v) for k, v in rows[0].items()} if rows else {}


def errors(since: str) -> str:
    rows = bq(f"""
SELECT {p('error_code')} error_code, {p('stage')} stage, COUNT(*) events
FROM `{TABLE}`
WHERE _TABLE_SUFFIX >= '{since}' AND event_name = 'audit_error'
  AND IFNULL({p('debug_mode', 'int')}, 0) != 1
GROUP BY 1, 2 ORDER BY 3 DESC""")
    return table(rows, ["error_code", "stage", "events"])


def entry(since: str) -> str:
    sources = bq(f"""
SELECT FORMAT_DATE('%Y-%m', PARSE_DATE('%Y%m%d', event_date)) month,
  IFNULL(collected_traffic_source.manual_source, IFNULL(traffic_source.source, '(none)')) source,
  COUNT(DISTINCT user_pseudo_id) users
FROM `{TABLE}`
WHERE _TABLE_SUFFIX >= '{since}' AND event_name = 'page_view'
  AND REGEXP_CONTAINS({p('page_location')}, r'mnemehq\\.com/audit/?(\\?|#|$)')
GROUP BY 1, 2 HAVING users > 1 ORDER BY 1, 3 DESC""")
    clicks = bq(f"""
SELECT REGEXP_EXTRACT({p('page_location')}, r'mnemehq\\.com(/[^?#]*)') page,
  {p('cta_position')} position, {p('cta_component')} component, COUNT(*) clicks
FROM `{TABLE}`
WHERE _TABLE_SUFFIX >= '{since}' AND event_name = 'cta_click'
  AND {p('cta_intent')} = 'audit' AND {p('page_location')} NOT LIKE '%/audit%'
GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 20""")
    referrers = bq(f"""
SELECT REGEXP_EXTRACT({p('page_referrer')}, r'mnemehq\\.com(/[^/?#]*/?)') section,
  COUNT(DISTINCT user_pseudo_id) users
FROM `{TABLE}`
WHERE _TABLE_SUFFIX >= '{since}' AND event_name = 'page_view'
  AND {p('page_location')} LIKE '%mnemehq.com/audit%'
  AND {p('page_referrer')} LIKE '%mnemehq.com%'
  AND {p('page_referrer')} NOT LIKE '%mnemehq.com/audit%'
GROUP BY 1 ORDER BY 2 DESC LIMIT 12""")
    return ("**Traffic source of /audit/ landings** (users, more than one)\n\n"
            + table(sources, ["month", "source", "users"])
            + "\n**Clicks on audit CTAs, by page**\n\n"
            + table(clicks, ["page", "position", "component", "clicks"])
            + "\n**Internal referrers into /audit/**\n\n"
            + table(referrers, ["section", "users"]))


def get(path: str, token: str | None) -> tuple[int, object]:
    req = urllib.request.Request(API + path, headers={"Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None


def is_internal(locator: str) -> bool:
    if locator in INTERNAL_LOCATORS:
        return True
    parts = locator.replace("https://github.com/", "").split("/")
    return "github.com" in locator and parts[0] in INTERNAL_OWNERS


def backend(since: str) -> tuple[str, str]:
    """Returns (markdown, exposure verdict)."""
    code, _ = get("/api/v1/projects?limit=1", None)
    if code == 200:
        verdict = "FAIL"
        md = ("**Exposure: FAIL.** An anonymous `GET /api/v1/projects` returned 200. "
              "Anyone can list audited projects, which contradicts the data-handling "
              "page's operator-only access claim. Fix before promoting the Audit.\n\n")
    elif code in (401, 403):
        verdict = "PASS"
        md = f"**Exposure: PASS.** Anonymous project listing is refused ({code}).\n\n"
    else:
        verdict = f"UNKNOWN ({code})"
        md = f"**Exposure: unknown.** Anonymous project listing returned {code}.\n\n"

    token = os.environ.get("MNEME_AUDIT_OPERATOR_TOKEN")
    if verdict != "FAIL" and not token:
        return md + "_Records skipped: set MNEME_AUDIT_OPERATOR_TOKEN to list them._\n", verdict

    code, projects = get("/api/v1/projects?limit=500", token)
    if code != 200 or not isinstance(projects, list):
        return md + f"_Project listing returned {code}; records skipped._\n", verdict

    def audits_of(project: dict) -> list[tuple[dict, dict]]:
        c, body = get(f"/api/v1/projects/{project['id']}/audits", token)
        items = body if isinstance(body, list) else (body or {}).get("audits", [])
        return [(project, a) for a in items] if c == 200 else []

    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = [r for chunk in pool.map(audits_of, projects) for r in chunk]

    cutoff = f"{since[:4]}-{since[4:6]}-{since[6:]}"
    rows = [(pr, a) for pr, a in rows if (a.get("created_at") or "") >= cutoff]
    external = [(pr, a) for pr, a in rows if not is_internal(pr.get("source_locator") or "")]
    status = Counter(a.get("status") for _, a in rows)
    months = Counter((a.get("created_at") or "")[:7] for _, a in rows)
    repos = Counter(pr.get("source_locator") for pr, _ in external)
    last = max((a.get("created_at") or "" for _, a in external), default="none")

    md += (f"Audits stored since {cutoff}: **{len(rows)}** "
           f"({len(external)} outside, {len(rows) - len(external)} internal), "
           f"status {dict(status)}, by month {dict(sorted(months.items()))}.\n\n"
           f"Last outside audit: **{last[:10]}**. Outside repositories, with audit counts "
           "(a count above 1 is a returning user or a re-audit):\n\n")
    md += table([{"repository": k, "audits": v} for k, v in repos.most_common()], ["repository", "audits"])
    md += ("\nA batch of well-known public repositories on one day is usually internal "
           "testing. Check before counting it as demand.\n")
    return md, verdict


def thresholds(today: date) -> str:
    t = trailing_30(today)
    rows = [{"metric": k, "last 30 days": t.get(k, 0), "pilot threshold": v,
             "met": "yes" if t.get(k, 0) >= v else "no"} for k, v in THRESHOLDS.items()]
    return ("Baseline for the ADR checker pilot: the full Audit's trailing 30 days "
            "against the checker's 30-day thresholds. The checker's own metric is "
            "result-to-Audit clicks; until it ships, cta_to_audit (site CTA clicks "
            "into the Audit) is only a proxy.\n\n"
            + table(rows, ["metric", "last 30 days", "pilot threshold", "met"]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", default=GA4_START, help="YYYYMMDD, not before 20260830")
    ap.add_argument("--skip-backend", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()
    since = max(args.since, GA4_START)
    today = date.today()

    parts = [f"# Architecture Audit health report, {today.isoformat()}\n",
             f"GA4 window: {since} to today. Debug and localhost sessions excluded.\n",
             "## 1. Funnel (sessions)\n", funnel(since),
             "\n## 2. Errors\n", errors(since),
             "\n## 3. Entry\n", entry(since)]
    verdict = "skipped"
    if not args.skip_backend:
        md, verdict = backend(since)
        parts += ["\n## 4. Backend records\n", md]
    parts += ["\n## 5. Pilot thresholds\n", thresholds(today)]
    report = "\n".join(parts)

    if args.out:
        open(args.out, "w", encoding="utf-8").write(report)
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
