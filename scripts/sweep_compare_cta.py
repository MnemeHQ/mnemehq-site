#!/usr/bin/env python3
"""P1-2: instrument all /compare/ detail CTAs; route the six highest-intent
pages through an Audit-primary bridge (confirmed experiment split).

Two treatments, deliberately separated so the routing experiment keeps a
control group:

  BRIDGED (6)   -- cursor-rules, claude-md, claude-code-memory,
                   rag-vs-governance, rag-coding-memory, github-copilot
                   The cta-block becomes: topic bridge paragraph -> coral
                   "Run the Architecture Audit" primary (cta_intent=audit) ->
                   neutral GitHub outline (cta_intent=github) -> demoted
                   "Request a pilot" text link (cta_intent=pilot). Editorial
                   read links untouched.

  INSTRUMENT-ONLY (7) -- the remaining compare detail pages keep the Pilot
                   primary exactly as-is, but every conversion CTA gains the
                   missing data-cta-* attributes so clicks stop being
                   invisible to GA4.

All 13 pages, both treatments:
  - lime button fill normalized to --action coral (CTA-system rule: lime is
    never a button fill); lime outlines to neutral border2
  - destinations carry canonical intents from the static-site taxonomy
    (audit | github | pilot) -- no new intents invented

Related correctness fixes shipped in the same milestone: '/compare' added to
pageType() in site/_snippets/cta-analytics.js (page_type=compare) and to the
cta_intent enum in docs/site/gtm-tagging-requirements.md (Wave 1 held-back
articles already emit cta_intent=compare).

Usage:
  python scripts/sweep_compare_cta.py            # report / dry-run (no writes)
  python scripts/sweep_compare_cta.py --write    # apply
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPARE_DIR = REPO_ROOT / "site" / "compare"
NON_DETAIL = {"index"}

# Confirm 2026-09-07: every detail page carries exactly this pilot button
# inside its cta-block. Devin-vs and google-antigravity add two more outline
# buttons, which the style normalization covers but the routing does not.
PILOT_BTN_RE = re.compile(
    r'<a href="/pilot/" class="btn-primary" style="margin-right:0\.5rem;">([^<]*)</a>')
# Outline buttons in the cta-block (github, works-with, read-analysis) share
# one lime inline style; their label differs per button, so capture it.
LIME_OUTLINE_BTN_RE = re.compile(
    r'<a href="([^"]+)" class="btn-primary" '
    r'style="background:transparent;border:1px solid var\(--accent\);color:var\(--accent\);'
    r'([^"]*)">([^<]*)</a>')
LIME_FILL_RE = re.compile(r'(\.btn-primary \{[^}]*?)background: var\(--accent\)')
LIME_FILL_HOVER_RE = re.compile(r'(\.btn-primary:hover \{ background: )var\(--accent-dim\)')

INDENT = "      "

AUDIT_BTN = (
    '<a href="/audit/" class="btn-primary" data-cta-intent="audit" '
    'data-cta-position="end" data-cta-component="end_block" '
    'style="margin-right:0.5rem;">Run the Architecture Audit &rarr;</a>'
)
PILOT_TAGGED_FMT = (
    '<a href="/pilot/" class="btn-primary" data-cta-intent="pilot" '
    'data-cta-position="end" data-cta-component="end_block" '
    'style="margin-right:0.5rem;">{label}</a>'
)
PILOT_TEXT = (
    '<a href="/pilot/" class="cta-secondary" data-cta-intent="pilot" '
    'data-cta-position="end" data-cta-component="end_block">'
    'Evaluating for your team? Request a pilot &rarr;</a>'
)
GITHUB_TAGGED_FMT = (
    '<a href="https://github.com/MnemeHQ/mneme" class="btn-primary" '
    'data-cta-intent="github" data-cta-position="end" '
    'data-cta-component="end_block" '
    'style="background:transparent;border:1px solid var(--border2);color:var(--text);'
    '{extra}">{label}</a>'
)

# Per-topic bridge paragraph for the six bridged pages. Copy stays inside each
# page's own claims; no competitor characterizations.
BRIDGE_COPY: dict[str, str] = {
    "cursor-rules":
        "Already using Cursor Rules? Run an audit to see which architectural "
        "rules could move from guidance to deterministic enforcement.",
    "claude-md":
        "See which decisions in your CLAUDE.md should remain guidance and "
        "which can become enforceable controls.",
    "claude-code-memory":
        "See which decisions in your Claude Code memory files should remain "
        "context and which can become enforceable controls.",
    "rag-vs-governance":
        "Audit your architecture to distinguish retrievable knowledge from "
        "enforceable decisions.",
    "rag-coding-memory":
        "Audit your architecture to see which knowledge belongs in retrieval "
        "and which decisions belong in enforcement.",
    "github-copilot":
        "See which architectural decisions Copilot-assisted changes are "
        "expected to hold in your repository.",
}

BRIDGED_SLUGS = sorted(BRIDGE_COPY)

SKIP_SENTINELS = (
    'data-cta-component="end_block"',  # already instrumented
)


def normalize_styling(text: str) -> tuple[str, list[str]]:
    """Lime fill -> action coral; lime cta-block outlines -> neutral."""
    changes: list[str] = []
    new, n = LIME_FILL_RE.subn(r"\1background: var(--action, #ea735e)", text)
    if n:
        changes.append("btn fill lime->action")
    new, n = LIME_FILL_HOVER_RE.subn(r"\1var(--action-dim, #c95a46)", new)
    if n:
        changes.append("btn hover lime-dim->action-dim")

    def outline_repl(m: re.Match) -> str:
        extra = (m.group(2) or "").strip()
        extra = extra + " " if extra else ""
        return GITHUB_TAGGED_FMT.format(label=m.group(3), extra=extra).replace(
            'data-cta-intent="github"', 'data-cta-intent="github"').replace(
            'href="{}"'.format(m.group(1)), 'href="{}"'.format(m.group(1)))

    # Tagged rebuild keeps each outline button's own href/label; conversion
    # intent is assigned afterwards for the github button specifically.
    def outline_repl_raw(m: re.Match) -> str:
        extra = (m.group(2) or "").strip()
        extra = extra + " " if extra else ""
        return ('<a href="%s" class="btn-primary" '
                'style="background:transparent;border:1px solid var(--border2);'
                'color:var(--text);%s">%s</a>' % (m.group(1), extra, m.group(3)))

    new, n = LIME_OUTLINE_BTN_RE.subn(outline_repl_raw, new)
    if n:
        changes.append(f"outline lime->neutral ({n})")
    return new, changes


def instrument_text(slug: str, text: str) -> tuple[str, list[str]]:
    """Apply the confirmed treatment for one compare detail page."""
    if any(s in text for s in SKIP_SENTINELS):
        return text, []  # already instrumented: idempotent skip
    crlf = "\r\n" in text

    def adapt(s: str) -> str:
        return s.replace("\n", "\r\n") if crlf else s

    changes: list[str] = []
    new, style_changes = normalize_styling(text)
    changes.extend(style_changes)

    # Tag the GitHub outline button in place (label preserved; the two variant
    # pages label it "GitHub" instead of "View on GitHub &rarr;").
    gh_re = re.compile(
        r'<a href="(https://github\.com/MnemeHQ/mneme)" class="btn-primary" '
        r'style="background:transparent;border:1px solid var\(--border2\);'
        r'color:var\(--text\);([^"]*)">([^<]*)</a>')
    new, n = gh_re.subn(
        lambda m: GITHUB_TAGGED_FMT.format(
            label=m.group(3), extra=(m.group(2) or "").strip()), new, count=1)
    if n:
        changes.append("github button tagged")

    if slug in BRIDGED_SLUGS:
        if not PILOT_BTN_RE.search(new):
            return text, ["MISS: pilot button pattern not found"]
        bridge = adapt(f"<p>{BRIDGE_COPY[slug]}</p>\n")
        new = PILOT_BTN_RE.sub(
            lambda _m: bridge + adapt(INDENT + AUDIT_BTN), new, count=1)
        # Demoted pilot text link goes directly under the tagged GitHub
        # outline so the cluster keeps its filled+outline+text shape. Match
        # against the file's own rebuilt button line: some pages use a raw
        # Unicode arrow instead of the &rarr; entity.
        gh_re2 = re.compile(
            r'<a href="https://github\.com/MnemeHQ/mneme" class="btn-primary" '
            r'data-cta-intent="github"[^>]*>[^<]*</a>')
        m = gh_re2.search(new)
        if m:
            new = new.replace(m.group(0),
                              m.group(0) + adapt("\n" + INDENT + PILOT_TEXT), 1)
        changes.append("bridged: audit primary + bridge copy + pilot demoted")
    else:
        new, n = PILOT_BTN_RE.subn(
            lambda m: PILOT_TAGGED_FMT.format(label=m.group(1)), new)
        if n:
            changes.append("pilot button tagged (hierarchy unchanged)")

    return new, changes


def detail_pages() -> list[Path]:
    """One path per compare detail page: site/compare/<slug>/index.html."""
    pages = [p / "index.html" for p in COMPARE_DIR.iterdir()
             if p.is_dir() and p.name not in NON_DETAIL]
    return sorted(p for p in pages if p.exists())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="apply changes (default: report only)")
    args = ap.parse_args()

    problems = 0
    for path in detail_pages():
        slug = path.parent.name
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        new, changes = instrument_text(slug, text)
        if not changes:
            print(f"skip-current  {slug}")
            continue
        if any(c.startswith("MISS") for c in changes):
            print(f"FAIL          {slug}: {changes}")
            problems += 1
            continue
        if args.write:
            path.write_bytes(new.encode("utf-8"))
        status = "written" if args.write else "would-write"
        print(f"{status:<13} {slug}: " + "; ".join(changes))

    if problems:
        print(f"\n{problems} page(s) need manual handling")
        return 1
    if not args.write:
        print("\n(report only -- rerun with --write to apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
