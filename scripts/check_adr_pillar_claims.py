#!/usr/bin/env python3
"""
Verify that the four-state table on /use-cases/adr-enforcement/ still matches
what the shipped Architecture Protection classifier actually does.

The table is the centre of that page's argument, and it names a product
contract: Protected / Mneme-ready / Requires modelling / Guidance. If the
classifier's behaviour changes and the page does not, the site starts making a
claim the product no longer honours -- the exact mismatch the P1.2 rewrite was
meant to end.

This asserts the page against the real code rather than against a copy of its
rules: it drives `assess_governability` and `classify_protection` from
`audit/backend`, and it reads the expected states out of the published HTML, so
neither side can drift silently.

Run from the repo root. Requires the audit backend's dependencies (the `mneme`
package); skips with a clear message when they are absent, so it can sit in CI
for the site without making the site build depend on the audit runtime.

Usage:
  python scripts/check_adr_pillar_claims.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "site" / "use-cases" / "adr-enforcement" / "index.html"
BACKEND = REPO_ROOT / "audit" / "backend"

# The decisions the page shows, expressed the way the Audit would receive them.
# `rules` stands for enforcement the Audit verified as already active;
# `anti` is the decision's anti-pattern text.
CASES = [
    {
        "state": "Protected",
        "decision": "Do not use SQLite.",
        "rules": [("FORBID_LITERAL", "sqlite", ("src/persistence/**",))],
        "anti": [],
        "expect_guardrail": "sqlite",
    },
    {
        "state": "Mneme-ready",
        "decision": "Do not use Redis.",
        "rules": [],
        "anti": ["redis"],
        "expect_guardrail": "redis",
    },
    {
        "state": "Requires modelling",
        "decision": "No vector DBs, agent loops, or LiteLLM.",
        "rules": [],
        "anti": ["vector db, agent loop, or litellm"],
        "expect_guardrail": None,
    },
    {
        "state": "Guidance",
        "decision": "Keep retrieval and enforcement conceptually separate.",
        "rules": [],
        "anti": [],
        "expect_guardrail": None,
    },
]


def states_on_page() -> list[str]:
    """The state names the published table actually claims, in order."""
    markup = PAGE.read_text(encoding="utf-8")
    body = re.search(r'<table class="state-table">.*?</table>', markup, re.S)
    if not body:
        raise SystemExit("check_adr_pillar_claims: FAIL - state table not found on the page")
    cells = re.findall(r'<td class="s-[a-z]+">(.*?)</td>', body.group(0), re.S)
    return [html.unescape(c).strip() for c in cells]


def main() -> int:
    sys.path.insert(0, str(BACKEND))
    try:
        from mneme.schemas import Decision, Rule
        from mneme.enforcer import assess_governability
        from app.services.p12_classifier import classify_protection, extract_proposed_rule
    except ImportError as exc:
        print(f"check_adr_pillar_claims: SKIP - audit backend deps unavailable ({exc})")
        return 0

    page_states = states_on_page()
    expected_states = [c["state"] for c in CASES]
    failures: list[str] = []

    if page_states != expected_states:
        failures.append(
            f"page table states {page_states} do not match the cases this check "
            f"verifies {expected_states}"
        )

    for case in CASES:
        decision = Decision(
            id="CHECK",
            decision=case["decision"],
            rationale="",
            scope=[],
            constraints=[],
            anti_patterns=list(case["anti"]),
            created_at="",
            updated_at="",
            rules=[
                Rule(type=t, value=v, include_paths=p, exclude_paths=())
                for (t, v, p) in case["rules"]
            ],
            source_path="docs/adr/check.md",
            memory_path="",
        )
        assessment = assess_governability(decision)
        guardrail = extract_proposed_rule(decision)
        actual = classify_protection(assessment, guardrail=guardrail)
        actual_state = getattr(actual, "value", str(actual))

        if actual_state != case["state"]:
            failures.append(
                f"{case['decision']!r} classifies as {actual_state!r}, "
                f"but the page says {case['state']!r}"
            )

        actual_guardrail = guardrail.pattern if guardrail else None
        if actual_guardrail != case["expect_guardrail"]:
            failures.append(
                f"{case['decision']!r} produced guardrail {actual_guardrail!r}, "
                f"expected {case['expect_guardrail']!r}"
            )

    if failures:
        print("check_adr_pillar_claims: FAIL")
        for f in failures:
            print(f"  - {f}")
        print("\n  The pillar page and the shipped classifier disagree. Fix the page,")
        print("  or update this check if the product contract changed deliberately.")
        return 1

    print(f"check_adr_pillar_claims: OK ({len(CASES)} table rows match the shipped classifier)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
