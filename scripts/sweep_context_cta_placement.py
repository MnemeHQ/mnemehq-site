#!/usr/bin/env python3
"""
Bring every insight's contextual CTA (data-mneme-cta="context") in line with
docs/site/cta-system.md and the markup contract in
docs/site/gtm-tagging-requirements.md.

Three fixes, all mechanical:

  1. Track the links. Every CTA control carries data-cta-intent,
     data-cta-position and data-cta-component (cta-system.md section 6). Most
     context CTAs predate that contract, so their clicks were invisible.
     Untracked links get intent from their destination (sweep_audit_cta's
     mapping, with non-quickstart docs pages as "docs"), position "end" and component "context".
     The off-schema pair position="article-end" / component="context-cta" is
     normalised to end/context. Links already on the schema, including the
     Wave 1 audit experiment's position="mid", are left alone so the running
     experiment's data stays continuous.

  2. Place the block after the prose. insert_contextual_ctas.py anchors the
     CTA before the FAQ; pages built since then put it after the FAQ. Move it
     back to just before the FAQ section.

  3. Keep conversion clusters to conversion destinations. cta-system.md
     section 4, rule 3: no more than two destinations in the end block, and
     source links live in the content, not in the cluster. Handled per page
     in PAGE_FIXES.

Idempotent.

Usage:
  python scripts/sweep_context_cta_placement.py           # report only
  python scripts/sweep_context_cta_placement.py --write   # apply
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sweep_audit_cta import intent_for as _audit_intent  # noqa: E402


def intent_for(href: str) -> str:
    """sweep_audit_cta's mapping, except that only the quickstart anchor is
    "quickstart"; other docs pages are "docs", and integration and
    concept pages get their own intents."""
    if href.startswith("/docs") and "#quickstart" not in href:
        return "docs"
    if href.startswith(("/integrations", "/works-with")):
        return "integration"
    if href.startswith("/concepts"):
        return "concept"
    return _audit_intent(href)

REPO_ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = REPO_ROOT / "site" / "insights"
NON_ARTICLE = {"all", "topics", "research"}
MARKER = 'data-mneme-cta="context"'

# (slug, old, new): exact-string fixes for clusters that break rule 3.
PAGE_FIXES = [
    (
        "behind-oreilly-radar-architectural-guardrails-ai-generated-code",
        '<a class="context-cta-secondary" href="https://www.oreilly.com/radar/architectural-guardrails-for-ai-generated-code/" target="_blank" rel="noopener">Read the O&rsquo;Reilly article</a>',
        '<a class="context-cta-secondary" href="/demo/">See the live demo &rarr;</a>',
    ),
    (
        "ai-native-sdlc-architecture-layer",
        '\n        <a href="/compare/claude-md/" class="cta-link" data-cta-intent="compare" data-cta-position="end" data-cta-component="cta_end">See CLAUDE.md vs Mneme &rarr;</a>',
        "",
    ),
]


def block_span(text: str) -> tuple[int, int] | None:
    """Start/end of the element carrying the context marker, matching nested
    tags of the same name (some context blocks are a <div> holding divs)."""
    i = text.find(MARKER)
    if i == -1:
        return None
    start = text.rfind("<", 0, i)
    tag = re.match(r"<(\w+)", text[start:]).group(1)
    depth = 0
    for m in re.finditer(rf"<(/?){tag}\b[^>]*>", text[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start, start + m.end()
    return None


def track_links(block: str) -> str:
    block = block.replace('data-cta-position="article-end" data-cta-component="context-cta"',
                          'data-cta-position="end" data-cta-component="context"')

    def fix(m: re.Match) -> str:
        a = m.group(0)
        if "data-cta-intent" in a:
            return a
        href = re.search(r'href="([^"]+)"', a).group(1)
        return a[:-1] + (f' data-cta-intent="{intent_for(href)}" '
                         f'data-cta-position="end" data-cta-component="context">')

    return re.sub(r"<a\s[^>]*>", fix, block)


def move_before_faq(text: str) -> str:
    span = block_span(text)
    faq = text.find('<section class="article-faq"')
    if not span or faq == -1 or span[0] < faq:
        return text
    start, end = span
    line_start = text.rfind("\n", 0, start) + 1
    block = text[line_start:end]
    nl = "\r\n" if "\r\n" in text else "\n"
    # Remove the block and the blank line before it.
    head = text[:line_start].rstrip(" \t\r\n") + nl
    tail = text[end:]
    text = head + nl + tail.lstrip("\r\n")
    faq = text.find('<section class="article-faq"')
    faq_line = text.rfind("\n", 0, faq) + 1
    return text[:faq_line] + block + nl + nl + text[faq_line:]


def process(path: Path, slug: str) -> tuple[str, list[str]]:
    text = path.read_bytes().decode("utf-8")
    original, changes = text, []
    for s, old, new in PAGE_FIXES:
        if s == slug and old in text:
            text = text.replace(old, new, 1)
            changes.append("cluster-destinations")
    span = block_span(text)
    if span:
        start, end = span
        tracked = track_links(text[start:end])
        if tracked != text[start:end]:
            text = text[:start] + tracked + text[end:]
            changes.append("tracked")
        moved = move_before_faq(text)
        if moved != text:
            text = moved
            changes.append("moved-before-faq")
    return (text if text != original else original), changes


def main() -> int:
    write = "--write" in sys.argv
    tally: dict[str, int] = {}
    for page in sorted(INSIGHTS.glob("*/index.html")):
        slug = page.parent.name
        if slug in NON_ARTICLE:
            continue
        text, changes = process(page, slug)
        for c in changes:
            tally[c] = tally.get(c, 0) + 1
        if changes and write:
            page.write_bytes(text.encode("utf-8"))
    verb = "fixed" if write else "would fix"
    for k, v in sorted(tally.items()):
        print(f"{verb}: {k}: {v} page(s)")
    if not tally:
        print("nothing to fix")
    return 0


if __name__ == "__main__":
    sys.exit(main())
