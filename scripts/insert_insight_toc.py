#!/usr/bin/env python3
"""
Give every insight article the "In this article" contents box from the
reference layout (/insights/emerging-ai-agent-infrastructure-stack/).

Only longer, sectioned articles get one: at least MIN_WORDS words of prose
and at least MIN_SECTIONS sections of MIN_SECTION_WORDS words or more.
Short commentary and announcement posts do not need navigation. A page that
already has a .toc (hand-made) is never touched.

For each eligible article, this script:

  * gives each section <h2> an id if it has none (a slug of its text,
    unique on the page),
  * inserts <nav class="toc"> as the first child of .article-body, listing
    the section headings and, when the page has one, the FAQ.

Sections are the <h2> elements between the start of .article-body and the
first of the FAQ, the contextual CTA, the related panel or </article>, the
same prose boundary sweep_context_cta_placement.py uses. Styles live in
site/assets/css/insight-editorial.css.

Idempotent and CRLF-preserving. sync_shared.py calls stamp() as a safety
net for new pages.

Usage:
  python scripts/insert_insight_toc.py           # report only
  python scripts/insert_insight_toc.py --write   # apply
"""
import html as html_lib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from link_insight_editorial import is_article  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = REPO_ROOT / "site" / "insights"
MIN_SECTIONS = 4        # sections with at least MIN_SECTION_WORDS words
MIN_SECTION_WORDS = 80
MIN_WORDS = 1000        # prose words; shorter commentary and announcements get no box

BODY_OPEN = re.compile(r'<div class="article-body"[^>]*>')
H2 = re.compile(r"<h2\b([^>]*)>(.*?)</h2>", re.DOTALL)
PROSE_END_MARKERS = (
    '<section class="article-faq"',
    'data-mneme-cta="context"',
    '<section class="related-panel"',
    "</article>",
)


def slugify(text: str) -> str:
    text = html_lib.unescape(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return "-".join(text.split("-")[:6]) or "section"


def heading_text(inner: str) -> str:
    """Visible heading text, still HTML-escaped, on one line."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()


def prose_end(text: str, start: int) -> int:
    ends = []
    for marker in PROSE_END_MARKERS:
        i = text.find(marker, start)
        if i != -1:
            ends.append(text.rfind("<", 0, i + 1) if marker.startswith("data-") else i)
    return min(ends) if ends else len(text)


def word_count(fragment: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", fragment).split())


def eligible(prose: str, sections: list, offset: int) -> bool:
    if word_count(prose) < MIN_WORDS:
        return False
    bounds = [m.start() - offset for m in sections] + [len(prose)]
    substantial = sum(1 for i in range(len(sections))
                      if word_count(prose[bounds[i]:bounds[i + 1]]) >= MIN_SECTION_WORDS)
    return substantial >= MIN_SECTIONS


def stamp(text: str, rel_posix: str) -> str:
    """Return text with a contents box inserted, or unchanged."""
    if 'class="toc"' in text or not is_article(rel_posix, text):
        return text
    body = BODY_OPEN.search(text)
    if not body:
        return text
    end = prose_end(text, body.end())
    sections = list(H2.finditer(text, body.end(), end))
    if not eligible(text[body.end():end], sections, body.end()):
        return text

    taken = set(re.findall(r'\bid="([^"]+)"', text))
    entries, edits = [], []
    for m in sections:
        attrs, inner = m.group(1), m.group(2)
        label = heading_text(inner)
        idm = re.search(r'\bid="([^"]+)"', attrs)
        if idm:
            anchor = idm.group(1)
        else:
            base = anchor = slugify(label)
            n = 2
            while anchor in taken:
                anchor = f"{base}-{n}"
                n += 1
            taken.add(anchor)
            edits.append((m.start(), m.start() + len("<h2"), f'<h2 id="{anchor}"'))
        entries.append((anchor, label))

    faq = re.search(r'<section class="article-faq"[^>]*>\s*<h2\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h2>', text, re.DOTALL)
    if faq:
        entries.append((faq.group(1), heading_text(faq.group(2))))

    nl = "\r\n" if "\r\n" in text else "\n"
    line_start = text.rfind("\n", 0, body.start()) + 1
    indent = re.match(r"[ \t]*", text[line_start:]).group(0) + "  "
    items = "".join(f'{nl}{indent}    <li><a href="#{a}">{t}</a></li>' for a, t in entries)
    toc = (f'{nl}{nl}{indent}<nav class="toc" aria-label="Table of contents">'
           f'{nl}{indent}  <div class="toc-title">In this article</div>'
           f'{nl}{indent}  <ol>{items}{nl}{indent}  </ol>'
           f'{nl}{indent}</nav>')

    # Apply heading ids back to front, then the box (it sits before them all).
    for s, e, new in sorted(edits, reverse=True):
        text = text[:s] + new + text[e:]
    return text[:body.end()] + toc + text[body.end():]


def main() -> int:
    write = "--write" in sys.argv
    changed, skipped = [], []
    for page in sorted(INSIGHTS.glob("*/index.html")):
        rel_posix = page.relative_to(REPO_ROOT / "site").as_posix()
        text = page.read_bytes().decode("utf-8")
        new = stamp(text, rel_posix)
        if new != text:
            changed.append(rel_posix)
            if write:
                page.write_bytes(new.encode("utf-8"))
        elif is_article(rel_posix, text) and 'class="toc"' not in text:
            skipped.append(rel_posix)
    print(f"{'added' if write else 'would add'} contents box: {len(changed)} article(s)")
    for p in skipped:
        print(f"  not eligible (under {MIN_WORDS} words or {MIN_SECTIONS} substantial sections): {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
