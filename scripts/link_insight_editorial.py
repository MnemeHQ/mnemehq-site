#!/usr/bin/env python3
"""
Link the shared insight layout layer (site/assets/css/insight-editorial.css)
on every insight article page.

An insight article is site/insights/<slug>/index.html carrying
class="article-wrap"; the index, /all/ and /topics/ listings are not articles.
The tag goes straight after the base.css link, so a page's own inline
<style> still loads later and wins where it styles the same component.

Idempotent. sync_shared.py calls stamp() as a safety net for new pages.

Usage:
  python scripts/link_insight_editorial.py           # report only
  python scripts/link_insight_editorial.py --write   # apply
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = REPO_ROOT / "site" / "insights"

MARKER = "/assets/css/insight-editorial.css"
TAGS = (
    '<link rel="stylesheet" href="/assets/css/insight-editorial.css">',
)
BASE_LINK = re.compile(r'<link rel="stylesheet" href="/assets/css/base\.css(\?v=\d+)?">')


def is_article(rel_posix: str, text: str) -> bool:
    parts = rel_posix.split("/")
    return (
        len(parts) == 3
        and parts[0] == "insights"
        and parts[2] == "index.html"
        and parts[1] not in ("all", "topics")
        and 'class="article-wrap"' in text
    )


def stamp(text: str, rel_posix: str) -> str:
    """Return text with the editorial tags linked, or unchanged."""
    if MARKER in text or not is_article(rel_posix, text):
        return text
    m = BASE_LINK.search(text)
    if not m:
        return text
    nl = "\r\n" if "\r\n" in text else "\n"
    insert = "".join(nl + "  " + t for t in TAGS)
    return text[:m.end()] + insert + text[m.end():]


def main() -> int:
    write = "--write" in sys.argv
    changed, missing_base = [], []
    for page in sorted(INSIGHTS.glob("*/index.html")):
        rel_posix = page.relative_to(REPO_ROOT / "site").as_posix()
        raw = page.read_bytes()
        text = raw.decode("utf-8")
        new = stamp(text, rel_posix)
        if new != text:
            changed.append(rel_posix)
            if write:
                page.write_bytes(new.encode("utf-8"))
        elif is_article(rel_posix, text) and MARKER not in text:
            missing_base.append(rel_posix)
    verb = "linked" if write else "would link"
    print(f"{verb}: {len(changed)} insight article(s)")
    for p in missing_base:
        print(f"  WARN: no base.css link, not stamped: {p}")
    return 1 if missing_base else 0


if __name__ == "__main__":
    sys.exit(main())
