#!/usr/bin/env python3
"""Fail CI if retired "drift audit" CTA terminology returns to customer-facing sources.

P0 terminology decision: "Request a drift audit" described an Audit action but
linked to /pilot/, and the label "drift audit" is retired as customer-facing
CTA copy entirely. Canonical language (docs/site/cta-system.md):

    Analyze repository  -> Run Architecture Audit
    Experience Mneme    -> Run the 2-minute demo
    Self-serve          -> Install Mneme
    Work with Mneme HQ  -> Request a pilot

Scanned sources:
  - site/**/*.html except og-*.html (OpenGraph image templates are render
    surfaces, not page copy)
  - templates/**/*.html (canonical CTA partials consumed when scaffolding)
  - docs/site/*.md (site system docs that guide future pages)

The match is case-insensitive and covers "drift audit" and "drift-audit"
spelling variants. Architectural-drift terminology in general ("architectural
drift", "drift prevention") is unaffected — only the retired compound label.

Usage:
  python scripts/check_drift_audit_cta.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PATTERN = re.compile(r"drift[ -]audit", re.IGNORECASE)

SCOPES = ["site/**/*.html", "templates/**/*.html", "docs/site/*.md"]
EXCLUDED_FILENAME_PREFIXES = ("og-",)


def hits() -> list[tuple[Path, int]]:
    found: list[tuple[Path, int]] = []
    for pattern in SCOPES:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.name.startswith(EXCLUDED_FILENAME_PREFIXES):
                continue
            text = path.read_text(encoding="utf-8")
            count = len(PATTERN.findall(text))
            if count:
                found.append((path, count))
    return found


def main() -> int:
    found = hits()
    if found:
        print("drift-audit-terminology-check: FAIL")
        for path, count in found:
            rel = path.relative_to(REPO_ROOT)
            print(f"  - {rel}: {count} retired-label hit(s) "
                  f"(canonical: 'Request a pilot' for /pilot/ destinations)")
        return 1
    print("drift-audit-terminology-check: PASS "
          "(zero retired-label hits across site, templates and docs/site)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
