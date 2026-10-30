---
name: audit-health-check
description: Check how the hosted Architecture Audit is performing and whether it is safe to promote. Covers the GA4 funnel, errors, entry sources, backend audit records, API exposure, the ADR checker pilot baseline, and shipping any fix through to live. Use when asked to "check the audit", for audit stats, audit performance or backend audits, or before promoting the Audit or the ADR checker.
---

# Audit health check

One procedure in four stages. It codifies the check run on 2026-10-30, which found:

- a funnel of 8 starts from 62 workspace sessions
- more `missing_input` errors than starts
- no audit traffic from insights
- an API that listed every audited project to anonymous callers

Deploy rules live in `audit/backend/DEPLOYMENTS.md` and `AGENTS.md`. Site publishing rules live in `PUBLISHING.md`. Where this file disagrees with them, they win; fix this file.

## 1. Collect

```bash
python scripts/audit_health_report.py --out audit-report.md
```

Run it from the repository root. Requires `bq` access to `mneme-hq-prod`. It exits 1 when the API exposure check fails. Options:

- `--since YYYYMMDD` narrows the window (it never goes before 2026-08-30, when canonical tagging started).
- `--skip-backend` runs GA4 only.
- `MNEME_AUDIT_OPERATOR_TOKEN` lets it read records once the API refuses anonymous reads.

Write `audit-report.md` outside `site/`, for example in a scratch directory. It is never deployed.

Rules while collecting:

- **Aggregate only.** Never call `/api/v1/projects/{id}/contacts` or print contact data. Repository locators are fine: they are public GitHub URLs or `upload:` markers.
- **Do not hand-edit the GA4 queries** without enumerating events first (`SELECT event_name, COUNT(*) … GROUP BY 1`). Remembered event lists have produced wrong conclusions before.
- **Session ids can be NULL.** A `NOT IN` over a subquery that returns a NULL yields no rows. The script guards against this; keep the guard.

## 2. Read the report

Work through the sections in this order and write down a finding for each.

1. **Exposure (section 4).** FAIL means anyone can list audited projects, which contradicts `site/security/data-handling/`'s operator-only claim. Stop here: raise it with the owner first. Promote nothing until it passes.
2. **Funnel (section 1).** Find the step with the biggest drop. As of 2026-10-30 it is workspace to start (62 → 8).
3. **Errors (section 2).** `missing_input` above the number of starts means visitors press Run with nothing entered (fixed by PR #280). HTTP 5xx or `network_error` points at the backend; check Cloud Run logs before blaming the frontend.
4. **Entry (section 3).** Note which pages actually send audit traffic. Insights sent 2 users in two months, and the nav and hero send most of it. A spike from one source, such as LinkedIn in September, is a campaign, not a trend.
5. **Backend records (section 4).** Separate real demand from testing. A batch of well-known public repositories on one day is internal. A repository audited twice is a returning user and worth a pilot conversation, but outreach is the owner's call.
6. **Pilot thresholds (section 5).** This is the baseline for the ADR checker experiment (30 starts, 20 completions and 4 result-to-Audit clicks in 30 days). The decision record is `mneme-growth-ops/docs/plans/2026-10-29-adr-and-instructions-checker-tools.md`.

## 3. Report

Lead with the exposure verdict, then the funnel leak, then demand (outside audits, last outside audit date, returning users). End with recommendations, each marked as something that is done or something that needs a decision.

When the owner wants a page to share, publish the report as an Artifact. Do not commit it to the repository. Plans go in `mneme-growth-ops/docs/plans`, never in this repository.

## 4. Ship a fix

Every fix gets its own branch with a purpose prefix (`fix/`, `site/`, `feat/`), never `claude/`. Its PR body carries the Execution provenance block (`AGENTS.md`).

**Site changes** (pages, CSS, CTAs):

1. Run the validators CI runs: `check_insights`, `check_nav_footer`, `check_sticky_nav`, `check_line_endings` and `check_encoding`, plus the content checks for the pages you touched.
2. For new reader-facing prose, the content gates apply: stop-slop at least 35/50, `lint_prose.py` with 0 errors, and a cold read of the built page by a reviewer with no context. Record the results in the PR body.
3. Squash-merge stacked or dependent PRs one at a time, after CI is green. Rebase the next PR onto `main` after each merge. A PR retargeted to `main` may need closing and reopening before CI runs.
4. Confirm deployment. You need a successful `Deploy site to mnemehq.com` run for the exact merge SHA, and `site-deployed` resolving to that SHA. A merge alone is not a deploy.
5. Verify live. Use `curl` with a cache-busting query, then the browser with one too, because the browser can serve a cached copy of the page.
6. A changed CSS or image asset ships under a new filename (`-v2`). A `base.css` change bumps its `?v=` on every page.
7. Do not use `sed -i` in Git Bash on site files: it flips CRLF and LF. Edit in binary mode in Python and run `check_line_endings.py`.

**Backend changes** (`audit/backend`):

1. Merge the PR. Deploying it to Cloud Run is a separate decision that needs the owner's explicit go-ahead.
2. Build from a clean `git archive` of the merged SHA and deploy with `--no-traffic --tag candidate`, inheriting all config. Verify the candidate, then shift traffic only after a second go-ahead.
3. Record the cutover in `audit/backend/DEPLOYMENTS.md`. Never read or print secret values.

After any fix that touches the funnel, run stage 1 again a week later and compare.
