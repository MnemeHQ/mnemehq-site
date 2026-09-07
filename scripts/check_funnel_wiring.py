#!/usr/bin/env python3
"""Fail CI when the canonical site -> Audit workspace -> /pilot/ funnel wiring drifts.

The commercial funnel is joined across three surfaces that evolve independently:

  1. the static marketing site   (cta_click via site/_snippets/cta-analytics.js)
  2. the Audit workspace SPA     (audit_start / audit_complete / cta_click,
                                  audit/frontend/src/analytics.ts)
  3. the /pilot/ form page       (pilot_form_start/attempt/error/success)

GTM v7 (docs/site/gtm-tagging-requirements.md) routes all of them through one
canonical GA4 router tag, so the funnel is only measurable if the emit-side
contract stays intact. This lint pins the emit side:

  - the canonical taxonomy (ONE cta_click + cta_intent; never per-intent
    event names -- those were the duplication legacy paused in container v6)
  - the pilot form event names and Formspree action
  - the Audit -> Pilot handoff (PilotLink, pilotContext, /pilot/?source=...)
  - the privacy contract: identifiers and reconstructed scores are never
    GA4 parameters (audit_id, protection_score must stay out of payloads)

Usage:
  python scripts/check_funnel_wiring.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CTA_ANALYTICS = "site/_snippets/cta-analytics.js"
NAV_SNIPPET = "site/_snippets/nav.html"
AUDIT_LANDING = "site/audit/index.html"
PILOT_PAGE = "site/pilot/index.html"
AUDIT_ANALYTICS = "audit/frontend/src/analytics.ts"
AUDIT_API = "audit/frontend/src/hooks/useAuditApi.ts"
PILOT_CONTEXT = "audit/frontend/src/utils/pilotContext.ts"
PILOT_LINK = "audit/frontend/src/components/PilotLink.tsx"

# Canonical GA4 summary metrics, copied verbatim from validated backend
# responses. Reconstructing or renaming these is a measurement regression.
AUDIT_SUMMARY_METRICS = [
    "decisions_discovered",
    "protection_relevant",
    "protected_count",
    "mneme_ready_count",
    "requires_modelling_count",
    "guidance_count",
    "current_protection",
    "identified_mneme_potential",
]

# Legacy per-intent event names. The canonical taxonomy is cta_click +
# cta_intent; reintroducing any of these (under any name) reopens the
# duplicate-counting hole that container v6 closed.
FORBIDDEN_EVENT_NAMES = [
    "audit_cta_click",
    "pilot_cta_click",
    "demo_cta_click",
    "install_cta_click",
    "cta_demo_click",
    "cta_github_click",
    "cta_clicked",
]

# Retired customer-facing CTA terminology must not return through the funnel
# surfaces this lint covers (site-wide zero-hit gate lives in sweep checks).
FORBIDDEN_CTA_PHRASES = ["drift audit"]

REQUIRED = [
    # (file, [required substrings], [forbidden substrings])
    (CTA_ANALYTICS,
     ["push('cta_click'", "cta_intent:", "cta_position:", "cta_component:",
      "cta_destination:", "link_text:", "source_page", "content_segment",
      "page_type", "isDevHost"],
     FORBIDDEN_EVENT_NAMES),
    (NAV_SNIPPET,
     ['data-cta-intent="audit"', 'data-cta-intent="pilot"', "Request a pilot"],
     FORBIDDEN_CTA_PHRASES),
    (AUDIT_LANDING,
     ['data-cta-intent="start_audit"', "/audit/workspace/",
      "Run Architecture Audit", 'data-cta-intent="request_pilot"',
      "Request a Pilot"],
     FORBIDDEN_EVENT_NAMES + FORBIDDEN_CTA_PHRASES),
    (PILOT_PAGE,
     ["pilot_form_start", "pilot_form_attempt", "pilot_form_error",
      "pilot_form_success", "form_id: 'pilot-form'", "mneme_pilot_context",
      "architecture-audit", "page_type: 'pilot'",
      "formspree.io/f/meennlwj"],
     FORBIDDEN_EVENT_NAMES + FORBIDDEN_CTA_PHRASES),
    (AUDIT_ANALYTICS,
     ["'audit_start'", "'audit_complete'"] + AUDIT_SUMMARY_METRICS +
     ["'request_pilot'", "'start_pilot'", "'audit_result'",
      "docs|pilot|demo|audit", "GTM-KL7FB67N"],
     ["audit_id", "protection_score"] + FORBIDDEN_EVENT_NAMES),
    (AUDIT_API,
     ["track('audit_start'", "track('audit_complete'"],
     ["protection_score"]),
    (PILOT_CONTEXT,
     ["mneme_pilot_context", "source: 'architecture-audit'", "/pilot/?",
      "storePilotContext", "buildPilotHref"],
     ["protection_score"]),
    (PILOT_LINK,
     ["data-cta-intent", "data-cta-position", "storePilotContext",
      "buildPilotHref"],
     []),
    # P0-B: the post-audit pilot activation band (commercial motion) must sit
    # beside, not replace, the self-serve install section on the audit result.
    ("audit/frontend/src/pages/AuditOverviewPage.tsx",
     ["Protect these decisions with Mneme", 'ctaPosition="audit_result"',
      'id="next-step-install"'],
     ["protection_score"]),
    # P1-A: mid-page Audit bridges on the high-intent team/pricing pages.
    ("site/for/index.html",
     ['data-cta-intent="audit" data-cta-position="mid" data-cta-component="cta_band"'],
     FORBIDDEN_CTA_PHRASES),
    ("site/for/cto/index.html",
     ['data-cta-intent="audit" data-cta-position="mid" data-cta-component="cta_band"'],
     FORBIDDEN_CTA_PHRASES),
    ("site/for/platform/index.html",
     ['data-cta-intent="audit" data-cta-position="mid" data-cta-component="cta_band"'],
     FORBIDDEN_CTA_PHRASES),
    ("site/for/principal-engineer/index.html",
     ['data-cta-intent="audit" data-cta-position="mid" data-cta-component="cta_band"'],
     FORBIDDEN_CTA_PHRASES),
    ("site/pricing/index.html",
     ['data-cta-intent="audit" data-cta-position="mid" data-cta-component="pricing_card"'],
     FORBIDDEN_CTA_PHRASES),
    # P1-2: /compare/ pages are instrumented (page_type=compare); the six
    # bridged pages carry audit-primary, the rest remain the tagged control.
    (CTA_ANALYTICS, ["['/compare', 'compare']"], []),
    ("site/compare/cursor-rules/index.html",
     ['data-cta-intent="audit" data-cta-position="end"',
      'data-cta-intent="pilot"', 'data-cta-intent="github"'],
     FORBIDDEN_EVENT_NAMES + FORBIDDEN_CTA_PHRASES),
    ("site/compare/windsurf/index.html",
     ['data-cta-intent="pilot"', 'data-cta-intent="github"'],
     FORBIDDEN_EVENT_NAMES + FORBIDDEN_CTA_PHRASES),
]

# Structural pairing checks: one anchor tag must carry both the destination
# and the funnel intent, so a relabel cannot silently split them.
PAIRED_ANCHORS = [
    (NAV_SNIPPET,
     r'<a\b(?=[^>]*href="/pilot/")(?=[^>]*data-cta-intent="pilot")'
     r'[^>]*>\s*Request a pilot\s*</a>'),
    (AUDIT_LANDING,
     r'<a\b(?=[^>]*href="/audit/workspace/")(?=[^>]*data-cta-intent="start_audit")'
     r'[^>]*>\s*Run Architecture Audit\s*</a>'),
    (AUDIT_LANDING,
     r'<a\b(?=[^>]*href="/pilot/")(?=[^>]*data-cta-intent="request_pilot")'
     r'[^>]*>\s*Request a Pilot\s*</a>'),
]


def check() -> list[str]:
    errors: list[str] = []
    for path, required, forbidden in REQUIRED:
        file = REPO_ROOT / path
        if not file.exists():
            errors.append(f"missing funnel surface: {path}")
            continue
        text = file.read_text(encoding="utf-8")
        for needle in required:
            if needle not in text:
                errors.append(f"{path}: required wiring absent: {needle!r}")
        for needle in forbidden:
            if needle in text:
                errors.append(
                    f"{path}: forbidden token present (canonical taxonomy / "
                    f"privacy contract violation): {needle!r}")
    for path, pattern in PAIRED_ANCHORS:
        file = REPO_ROOT / path
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8")
        if not re.search(pattern, text):
            errors.append(
                f"{path}: anchor pairing drifted (destination + intent + "
                f"label must live on one tag): {pattern}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("funnel-wiring-check: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("funnel-wiring-check: PASS "
          f"({len(REQUIRED)} surfaces, {len(PAIRED_ANCHORS)} paired anchors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
