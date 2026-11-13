#!/usr/bin/env python3
"""
Give every insight article the mid-article CTA band (templates/
cta-components.html, component 4) that 160 articles already carry.

templates/article.html has no band, so articles built from it shipped
without one until new_article.py started calling stamp() below. This script inserts the canonical
band, word for word as the existing 160 carry it, so no new copy is added.

Placement: at the end of the article's first full section, immediately
before the next section <h2>, once at least MIN_WORDS words of prose come
before it. That matches the existing bands, and the reading data behind
it: since 2026-08-30, engaged insight sessions (10 s or more) have a
median of 39 s of engagement and only 26% reach the 90% scroll mark, so
most readers never get to the 45-60% point docs/site/cta-system.md gives
as a heuristic. The end of the first section is where they are.

Idempotent and CRLF-preserving. check_insights.py fails an article with
no band and points here.

Usage:
  python scripts/insert_mid_cta_band.py           # report only
  python scripts/insert_mid_cta_band.py --write   # apply
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = REPO_ROOT / "site" / "insights"
NON_ARTICLE = {"all", "topics", "research"}
MIN_WORDS = 150

BAND = """<aside class="cta-band" aria-label="Try Mneme">
  <div class="cta-band-eyebrow">Runnable in five minutes</div>
  <h3>See this enforced on your own repository</h3>
  <p>Install the CLI, add one decision, run one check. No signup, no telemetry &mdash; MIT licensed.</p>
  <div class="cta-row">
    <a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="install" data-cta-position="mid" data-cta-component="cta_band">Install Mneme</a>
    <a href="/demo/" class="cta-btn-outline" data-cta-intent="demo" data-cta-position="mid" data-cta-component="cta_band">Run the 2-minute demo</a>
  </div>
</aside>"""

BODY_OPEN = re.compile(r'<div class="article-body"[^>]*>')
PROSE_END_MARKERS = ('<section class="article-faq"', 'data-mneme-cta="context"',
                     '<section class="related-panel"', "</article>")


def prose_end(text: str, start: int) -> int:
    ends = []
    for marker in PROSE_END_MARKERS:
        i = text.find(marker, start)
        if i != -1:
            ends.append(text.rfind("<", 0, i + 1) if marker.startswith("data-") else i)
    return min(ends) if ends else len(text)


def words(fragment: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", fragment).split())


def stamp(text: str) -> str:
    if 'class="cta-band"' in text:
        return text
    body = BODY_OPEN.search(text)
    if not body:
        return text
    end = prose_end(text, body.end())
    heads = [m.start() for m in re.finditer(r"<h2\b", text[body.end():end])]
    heads = [body.end() + h for h in heads]
    # Never before the first section heading; first boundary with enough prose.
    target = next((h for h in heads[1:] if words(text[body.end():h]) >= MIN_WORDS), None)
    if target is None:
        return text
    nl = "\r\n" if "\r\n" in text else "\n"
    line_start = text.rfind("\n", 0, target) + 1
    indent = re.match(r"[ \t]*", text[line_start:]).group(0)
    band = nl.join(indent + line for line in BAND.split("\n"))
    return text[:line_start] + band + nl + nl + text[line_start:]


def main() -> int:
    write = "--write" in sys.argv
    changed, skipped = [], []
    for page in sorted(INSIGHTS.glob("*/index.html")):
        if page.parent.name in NON_ARTICLE:
            continue
        text = page.read_bytes().decode("utf-8")
        new = stamp(text)
        if new != text:
            changed.append(page.parent.name)
            if write:
                page.write_bytes(new.encode("utf-8"))
        elif 'class="cta-band"' not in text:
            skipped.append(page.parent.name)
    print(f"{'added' if write else 'would add'} mid-article band: {len(changed)} article(s)")
    for s in skipped:
        print(f"  skipped (no section boundary after {MIN_WORDS} words): {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
