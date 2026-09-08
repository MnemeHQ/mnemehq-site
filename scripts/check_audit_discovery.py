#!/usr/bin/env python3
"""Fail CI if the /audit/ discovery contract regresses.

Two failure families are gated here, both found in the September 2026 Audit
discovery pass.

1. The retired public product name "Architecture Governability Audit"
   reappearing on a customer-facing surface. The public name is the
   "Architecture Protection Audit". The old name outlived the page copy in
   the Vite source for the workspace app (audit/frontend/index.html), in the
   committed build output (site/audit/workspace/index.html) and in the
   OpenGraph card template (site/og-audit.html).

2. /audit/ silently dropping out of the machine-readable discovery surfaces:
   the XML sitemap, llms.txt, its own canonical <title>, and the
   noindex/canonical pair that stops the workspace app competing with
   /audit/ in search.

Scanned sources for (1):
  - site/**/*.html   page copy, the committed workspace build output, AND
                     og-*.html templates. Unlike scripts/check_drift_audit_cta.py
                     the OG templates are IN scope here, because og-audit.html
                     renders into a social card a human reads.
  - site/**/*.txt    llms.txt, llms-full.txt, robots.txt.
  - audit/frontend/*.html
                     the Vite source the build output is generated from.
                     Fixing only the build output regresses on the next
                     `npm run build`.

Deliberately NOT scanned: audit/backend/**, where `governability` remains an
internal model field name and a legacy Markdown export header. Renaming those
is product work with its own contract tests, not site metadata.

Usage:
  python scripts/check_audit_discovery.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RETIRED_NAME = re.compile(r"Architecture\s+Governability\s+Audit", re.IGNORECASE)
RETIRED_SCOPES = ["site/**/*.html", "site/**/*.txt", "audit/frontend/*.html"]

AUDIT_PAGE = "site/audit/index.html"
WORKSPACE_BUILD = "site/audit/workspace/index.html"
WORKSPACE_SOURCE = "audit/frontend/index.html"
SITEMAP = "site/sitemap.xml"
LLMS = "site/llms.txt"

CANONICAL_TITLE = "<title>Architecture Protection Audit | Mneme HQ</title>"
SITEMAP_LOC = "<loc>https://mnemehq.com/audit/</loc>"
LLMS_LINK = "(https://mnemehq.com/audit/)"

ROBOTS_NOINDEX = re.compile(
    r'<meta\s+name="robots"\s+content="noindex,\s*follow"\s*/?>', re.IGNORECASE
)
AUDIT_CANONICAL = re.compile(
    r'<link\s+rel="canonical"\s+href="https://mnemehq\.com/audit/"\s*/?>',
    re.IGNORECASE,
)


def _read(rel: str) -> str | None:
    path = REPO_ROOT / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def retired_name_hits() -> list[tuple[Path, int]]:
    """Every scanned file still carrying the retired product name."""
    found: list[tuple[Path, int]] = []
    for pattern in RETIRED_SCOPES:
        for path in sorted(REPO_ROOT.glob(pattern)):
            count = len(RETIRED_NAME.findall(path.read_text(encoding="utf-8")))
            if count:
                found.append((path, count))
    return found


def contract_failures() -> list[str]:
    """Positive invariants that keep /audit/ discoverable and citable."""
    failures: list[str] = []

    audit_page = _read(AUDIT_PAGE)
    if audit_page is None:
        failures.append(f"{AUDIT_PAGE}: missing")
    elif CANONICAL_TITLE not in audit_page:
        failures.append(
            f"{AUDIT_PAGE}: canonical <title> must be exactly "
            f"'Architecture Protection Audit | Mneme HQ'"
        )

    sitemap = _read(SITEMAP)
    if sitemap is None or SITEMAP_LOC not in sitemap:
        failures.append(f"{SITEMAP}: missing a <url> entry for {SITEMAP_LOC}")

    llms = _read(LLMS)
    if llms is None or LLMS_LINK not in llms:
        failures.append(
            f"{LLMS}: missing a first-class entry linking https://mnemehq.com/audit/"
        )

    for rel in (WORKSPACE_SOURCE, WORKSPACE_BUILD):
        text = _read(rel)
        if text is None:
            failures.append(f"{rel}: missing")
            continue
        if not ROBOTS_NOINDEX.search(text):
            failures.append(f'{rel}: missing <meta name="robots" content="noindex, follow">')
        if not AUDIT_CANONICAL.search(text):
            failures.append(f'{rel}: missing canonical link to https://mnemehq.com/audit/')

    return failures


def main() -> int:
    hits = retired_name_hits()
    failures = contract_failures()

    if not hits and not failures:
        print(
            "audit-discovery-check: PASS (retired product name absent; "
            "sitemap, llms.txt, canonical title and workspace noindex all present)"
        )
        return 0

    print("audit-discovery-check: FAIL")
    for path, count in hits:
        rel = path.relative_to(REPO_ROOT).as_posix()
        print(
            f"  - {rel}: {count} retired-name hit(s) "
            f"(canonical public name: 'Architecture Protection Audit')"
        )
    for failure in failures:
        print(f"  - {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
