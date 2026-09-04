#!/usr/bin/env python3
"""
Wave 1 of the Architecture Audit routing experiment: point the existing
contextual CTA on evidence-selected organic landing pages at /audit/, and make
those CTAs measurable.

Why this is a re-route rather than a second CTA
-----------------------------------------------
Every insight already carries one contextual CTA (scripts/insert_contextual_ctas.py).
The CTA system allows one primary intent per cluster (templates/cta-components.html
rules 1-2), so adding an Audit block beside the existing one would put two filled
buttons in the same view. This script rewrites the block that is already there.

Why two segments rather than one blanket re-route
-------------------------------------------------
Organic Insight landing pages were measured over 2026-06-01..2026-09-01 (GA4
session-level, localhost excluded, activation counted as GitHub outbound OR demo
OR docs OR pilot):

    developer/evaluation content   93 sessions   62% engaged   7.5% activated
    problem-awareness/exec content 146 sessions  59% engaged   4.1% activated

Developer content converts into product activation; analyst and problem-awareness
content converts into nothing at all. A blanket re-route to /audit/ would have
replaced a working activation path on the technical articles.

Two caveats are deliberately preserved in this design:

  * 7 activations vs 6 is NOT a statistically meaningful gap. The split is made
    on reader intent, not on that difference. The analytics decide whether to
    expand or reverse it later.
  * `pip install` activation was historically unmeasurable -- `code_copy` only
    began flowing when GTM canonical analytics went live 2026-08-30. True
    activation on technical pages is therefore unknown and higher than 7.5%,
    which is the strongest reason not to disturb their primary CTA.

So:

    SEGMENT_DEV      primary preserved exactly; the /pilot/ secondary, which
                     produced zero measurable activation on every organic
                     Insight landing page, becomes the Audit.

    SEGMENT_PROBLEM  Audit becomes primary with page-specific copy; the previous
                     primary demotes to secondary rather than being discarded.

Copy is deliberately metric-neutral: it never names Enforceable/Partial/Guidance
or Protected/Protectable/Potential, so it stays correct across the pending Audit
model change and cannot describe an unshipped product.

Measurement
-----------
The contextual CTA links carried no data-cta-* attributes, so every click on them
was invisible. This script adds them, and stamps each page with
`<meta name="mneme:content-segment">` so cta-analytics.js can report which content
type produced a conversion. See docs/site/gtm-tagging-requirements.md.

Usage:
  python scripts/sweep_audit_cta.py            # report / dry-run (no writes)
  python scripts/sweep_audit_cta.py --write     # apply
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSIGHTS_DIR = REPO_ROOT / "site" / "insights"

AUDIT_HREF = "/audit/"
AUDIT_LABEL = "Run the Architecture Audit"

SEGMENT_DEV = "developer_evaluation"
SEGMENT_PROBLEM = "problem_awareness"

SEGMENT_META = 'mneme:content-segment'

# ---------------------------------------------------------------------------
# Segment A -- developer / evaluation. Primary preserved; Audit as secondary.
# Value is an optional custom secondary label; None uses AUDIT_LABEL.
# ---------------------------------------------------------------------------
SEGMENT_DEV_SLUGS: dict[str, str | None] = {
    # The cleanest developer journey on the site: ADR search -> mechanism ->
    # compilation. Sending that reader to a whole-repository audit instead would
    # interrupt an unusually strong intent match, so the compiler stays primary
    # and the Audit is offered as the complementary next step.
    "how-ai-coding-agents-use-adrs": "Already have ADRs? Run the Architecture Audit",
    "ai-native-sdlc-architecture-layer": None,
    "ai-coding-agent-guardrails": None,
    "cursor-developer-habits-report-governance-infrastructure": None,
    "why-code-review-cannot-scale-with-ai-output": None,
    "harness-engineering-still-needs-governance": None,
    "open-knowledge-format-vs-governance": None,
    "harness-engineering-verification-layer": None,
    "what-is-harness-engineering": None,
    "google-spec-driven-development-not-enough": None,
    "what-makes-prompts-a-graph-prompt-graph-engineering-governance": None,
    # Someone arriving on a Liskov/encapsulation/Python query is in a
    # software-design frame; the jump to a repository audit is too far.
    "barbara-liskov-python-encapsulation-ai-governance": None,
}

# ---------------------------------------------------------------------------
# Segment B -- problem-awareness / governance / exec. Audit becomes primary.
# ---------------------------------------------------------------------------
SEGMENT_PROBLEM_SLUGS: dict[str, str] = {
    "mckinsey-ai-table-stakes-to-advantage":
        "The distance between a pilot and an advantage is whether decisions survive "
        "delivery. Find out which of your architectural decisions a coding agent "
        "could violate today.",
    "ai-native-engineering-intent-debt":
        "Intent debt is the distance between the decisions you recorded and the "
        "decisions your repository can hold. Measure yours.",
    "mckinsey-agentic-software-delivery-governance":
        "Governance at delivery speed starts with knowing which decisions your "
        "repository can actually hold against an agent. Find out which of yours do.",
    "palantir-agentic-governance-engineering-governance":
        "Enterprise governance stops at the repository boundary unless decisions are "
        "enforced there. See where yours stand.",
    "bcg-ai-era-operating-models-governance":
        "An operating model only holds if the architecture underneath it does. See "
        "which of your architectural decisions a coding agent could violate today.",
    "zero-trust-for-ai-agents-architectural-governance":
        "Zero trust means verifying the change rather than trusting the agent. Find "
        "out which of your architectural decisions your repository can verify.",
    "acceleration-whiplash-governance-gap":
        "The governance gap is measurable. Find out how many of your architectural "
        "decisions a coding agent could violate without anything stopping it.",
    "dora-metrics-insufficient-for-agentic-development":
        "If DORA does not capture architectural decay, measure what does &mdash; starting "
        "with which of your architectural decisions your repository can hold.",
    "ai-agents-are-not-employees-governance":
        "Agents do not absorb architectural judgement the way colleagues do. See "
        "which of your decisions are enforced rather than assumed.",
    "governance-control-plane-after-agent-frameworks":
        "A control plane needs something to control. Find out which architectural "
        "decisions your repository can hold today.",
    "bain-ai-development-lifecycle-governance":
        "Lifecycle governance depends on decisions holding at every stage. See which "
        "of yours the repository can hold.",
    "enterprise-ai-guardrails-five-layers":
        "Guardrails only count at the layer where the code is written. Find out which "
        "of your architectural decisions hold there.",
}

# Pages that qualified on traffic but keep their current routing: the existing
# /compare/ target answers the reader's question more precisely than a general
# repository audit would.
HELD_BACK = {
    "cursor-developer-habits-report-governance-infrastructure": "/compare/cursor-rules/",
    "why-rag-fails-for-architectural-governance": "/compare/rag-vs-governance/",
    "open-knowledge-format-vs-governance": "/compare/claude-code-memory/",
}

ASIDE_RE = re.compile(
    r'<aside class="context-cta" data-mneme-cta="context".*?</aside>', re.S)
# A few articles use the richer end-block variant instead of the compact aside.
# It already carries data-cta-* attributes, so only the destination moves.
END_BLOCK_RE = re.compile(
    r'<aside class="cta-block-end" data-mneme-cta="context".*?</aside>', re.S)
PILOT_LINK_RE = re.compile(
    r'<a href="/pilot/"([^>]*?)data-cta-intent="pilot"([^>]*)>(.*?)</a>', re.S)
COPY_RE = re.compile(r'(<p class="context-cta-copy">)(.*?)(</p>)', re.S)
# Attribute-order tolerant: this script emits class before the data-cta-*
# attributes while insert_contextual_ctas.py emits href then class, and the
# sweep must be able to re-parse its own output to stay idempotent.
PRIMARY_RE = re.compile(
    r'<a\b[^>]*\bclass="context-cta-primary"[^>]*>(.*?)</a>', re.S)
SECONDARY_RE = re.compile(
    r'<a\b[^>]*\bclass="context-cta-secondary"[^>]*>(.*?)</a>', re.S)
HREF_RE = re.compile(r'\bhref="([^"]*)"')
ARROW = " &rarr;"


def intent_for(href: str) -> str:
    """Map a destination to the cta_intent enum in gtm-tagging-requirements.md."""
    if href.startswith("/audit"):
        return "audit"
    if href.startswith("/demo"):
        return "demo"
    if href.startswith("/compare"):
        return "compare"
    if href.startswith("/docs"):
        return "quickstart"
    if href.startswith("/pilot"):
        return "pilot"
    if href.startswith("/use-cases"):
        return "use_case"
    return "other"


def strip_arrow(label: str) -> str:
    return label[:-len(ARROW)] if label.endswith(ARROW) else label


def link(href: str, label: str, cls: str) -> str:
    return (f'<a href="{href}" class="{cls}" data-cta-intent="{intent_for(href)}" '
            f'data-cta-position="mid" data-cta-component="context">'
            f'{strip_arrow(label)}{ARROW}</a>')


def ensure_segment_meta(html: str, segment: str, nl: str) -> tuple[str, bool]:
    """Stamp a real head meta tag, never an example in a script or comment."""
    tag = f'<meta name="{SEGMENT_META}" content="{segment}" />'
    head = re.search(r'<head\b[^>]*>(.*?)</head\s*>', html, re.I | re.S)
    if head is None:
        return html, False
    # Preserve offsets while hiding non-markup examples, including analytics JS.
    markup = re.sub(r'<!--.*?-->|<script\b[^>]*>.*?</script\s*>',
                    lambda m: ' ' * len(m.group(0)), head.group(1),
                    flags=re.I | re.S)
    offset = head.start(1)
    existing = re.search(rf'<meta name="{re.escape(SEGMENT_META)}"[^>]*/?>', markup)
    if existing:
        if existing.group(0) == tag:
            return html, False
        return html[:offset + existing.start()] + tag + html[offset + existing.end():], True
    robots = re.search(r'[ \t]*<meta name="robots"[^>]*/?>', markup)
    if robots:
        indent = re.match(r'[ \t]*', robots.group(0)).group(0)
        end = offset + robots.end()
        return html[:end] + nl + indent + tag + html[end:], True
    end = head.end(1)
    return html[:end] + "  " + tag + nl + html[end:], True


def rewrite_block(block: str, segment: str, slug: str) -> tuple[str, dict] | None:
    pm = PRIMARY_RE.search(block)
    sm = SECONDARY_RE.search(block)
    cm = COPY_RE.search(block)
    if not (pm and sm and cm):
        return None
    ph = HREF_RE.search(pm.group(0))
    sh = HREF_RE.search(sm.group(0))
    if not (ph and sh):
        return None

    old_primary_href, old_primary_label = ph.group(1), pm.group(1)
    old_secondary_href = sh.group(1)
    info = {"old_primary": old_primary_href}

    # Already routed: re-derive from the pre-sweep destination so a re-run is a
    # no-op rather than promoting /audit/ into its own secondary.
    if segment == SEGMENT_PROBLEM and old_primary_href == AUDIT_HREF:
        old_primary_href, old_primary_label = old_secondary_href, sm.group(1)
        info["old_primary"] = old_primary_href

    if segment == SEGMENT_DEV:
        # Preserve the primary exactly as it is -- including targets this
        # script's rules would not regenerate, e.g. /docs/#quickstart.
        new_primary = link(old_primary_href, old_primary_label, "context-cta-primary")
        label = SEGMENT_DEV_SLUGS[slug] or AUDIT_LABEL
        new_secondary = link(AUDIT_HREF, label, "context-cta-secondary")
        new_copy = None
        info["new_primary"] = old_primary_href
        info["new_secondary"] = AUDIT_HREF
    else:
        new_primary = link(AUDIT_HREF, AUDIT_LABEL, "context-cta-primary")
        # Demote the previous primary rather than discarding it.
        new_secondary = link(old_primary_href, old_primary_label,
                             "context-cta-secondary")
        new_copy = SEGMENT_PROBLEM_SLUGS[slug]
        info["new_primary"] = AUDIT_HREF
        info["new_secondary"] = old_primary_href

    out = PRIMARY_RE.sub(lambda _m: new_primary, block, count=1)
    out = SECONDARY_RE.sub(lambda _m: new_secondary, out, count=1)
    if new_copy is not None:
        out = COPY_RE.sub(lambda m: m.group(1) + new_copy + m.group(3), out, count=1)
    return out, info


def process(slug: str, segment: str, write: bool) -> dict:
    path = INSIGHTS_DIR / slug / "index.html"
    if not path.exists():
        return {"slug": slug, "status": "MISSING"}
    with io.open(path, encoding="utf-8", newline="") as fh:
        html = fh.read()
    nl = "\r\n" if "\r\n" in html else "\n"

    m = ASIDE_RE.search(html)
    if m:
        res = rewrite_block(m.group(0), segment, slug)
        if res is None:
            return {"slug": slug, "status": "UNPARSED-BLOCK"}
        new_block, info = res
        new_html = html[:m.start()] + new_block + html[m.end():]
    else:
        # End-block variant. Only the dead /pilot/ destination moves; the
        # install/demo primary is left exactly as it is, which is the Segment A
        # treatment. A Segment B page in this shape would need its primary
        # rewritten too, so refuse rather than half-apply.
        m = END_BLOCK_RE.search(html)
        if not m:
            return {"slug": slug, "status": "NO-CTA-BLOCK"}
        if segment != SEGMENT_DEV:
            return {"slug": slug, "status": "END-BLOCK-NEEDS-MANUAL"}
        block = m.group(0)
        if f'href="{AUDIT_HREF}"' in block:
            new_block = block
        else:
            pm = PILOT_LINK_RE.search(block)
            if not pm:
                return {"slug": slug, "status": "NO-PILOT-SECONDARY"}
            label = SEGMENT_DEV_SLUGS[slug] or AUDIT_LABEL
            new_link = (f'<a href="{AUDIT_HREF}"{pm.group(1)}data-cta-intent="audit"'
                        f'{pm.group(2)}>{strip_arrow(label)}</a>')
            new_block = PILOT_LINK_RE.sub(lambda _m: new_link, block, count=1)
        info = {"old_primary": "(end-block)", "new_primary": "(unchanged)",
                "new_secondary": AUDIT_HREF}
        new_html = html[:m.start()] + new_block + html[m.end():]
    new_html, meta_changed = ensure_segment_meta(new_html, segment, nl)

    if new_html == html:
        return {"slug": slug, "status": "skip-current", "segment": segment, **info}

    if write:
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_html)
    return {"slug": slug, "status": "written" if write else "would-write",
            "segment": segment, **info}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="apply changes (default: report only)")
    args = ap.parse_args()

    overlap = set(SEGMENT_DEV_SLUGS) & set(SEGMENT_PROBLEM_SLUGS)
    if overlap:
        print(f"!! a slug cannot be in both segments: {sorted(overlap)}")
        return 1

    results = []
    for slug in SEGMENT_DEV_SLUGS:
        results.append(process(slug, SEGMENT_DEV, args.write))
    for slug in SEGMENT_PROBLEM_SLUGS:
        results.append(process(slug, SEGMENT_PROBLEM, args.write))

    print(f"\n=== Segment A: {SEGMENT_DEV} "
          f"(primary preserved, Audit as secondary) ===")
    for r in results:
        if r.get("segment") == SEGMENT_DEV:
            print(f"  {r['old_primary']:<32} -> secondary {r['new_secondary']:<10} "
                  f"{r['slug']}")

    print(f"\n=== Segment B: {SEGMENT_PROBLEM} (Audit as primary) ===")
    for r in results:
        if r.get("segment") == SEGMENT_PROBLEM:
            print(f"  {r['new_primary']:<10} (was {r['old_primary']:<28}) "
                  f"{r['slug']}")

    print("\n=== Held back (existing /compare/ target is more precise) ===")
    for slug, href in sorted(HELD_BACK.items()):
        note = " [segment A: primary preserved]" if slug in SEGMENT_DEV_SLUGS else ""
        print(f"  {href:<32} {slug}{note}")

    by_status: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    print("\n=== Status ===")
    for k in sorted(by_status):
        print(f"  {k:<16} {by_status[k]}")

    bad = [r for r in results
           if r["status"] in {"MISSING", "NO-CTA-BLOCK", "UNPARSED-BLOCK",
                              "END-BLOCK-NEEDS-MANUAL", "NO-PILOT-SECONDARY"}]
    if bad:
        print("\n!!! needs manual handling:")
        for r in bad:
            print(f"    {r['status']:<16} {r['slug']}")
        return 1

    if not args.write:
        print("\n(report only -- rerun with --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
