#!/usr/bin/env python3
"""Repoint every page's og:image / twitter:image to the og-v2.png card set.

The render/manifest pipeline (og_manifest.py, render_og.py) produces
og-v2.png cards without ever touching the pages that advertise them --
pages still point at the legacy og.png. `rewrite()` is the pure, testable
core: it repoints the image URLs and stamps the four metadata tags
(og:image:width/height/alt, twitter:image:alt) that Slack/Twitter/LinkedIn
use to lay the card out and describe it. `main()` walks every
site/**/index.html that has an og:image tag, resolves its manifest alt
text via og_manifest.resolve, and rewrites it in place.

Idempotent by construction: existing og:image:width/height/alt and
twitter:image:alt tags are replaced, not duplicated, and repointing an
already-og-v2.png URL is a no-op string replace.
"""
from __future__ import annotations

import html as html_mod
import re
import sys
from pathlib import Path

import og_manifest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
MANIFEST = REPO / "site" / "og" / "cards.yaml"
CARD_NAME = "og-v2.png"

OG_IMAGE_RE = re.compile(
    r'<meta property="og:image" content="([^"]*)"\s*/?>')
TWITTER_IMAGE_RE = re.compile(
    r'<meta name="twitter:image" content="([^"]*)"\s*/?>')

OG_WIDTH_RE = re.compile(r'<meta property="og:image:width" content="[^"]*"\s*/?>\n?')
OG_HEIGHT_RE = re.compile(r'<meta property="og:image:height" content="[^"]*"\s*/?>\n?')
OG_ALT_RE = re.compile(r'<meta property="og:image:alt" content="[^"]*"\s*/?>\n?')
TWITTER_ALT_RE = re.compile(r'<meta name="twitter:image:alt" content="[^"]*"\s*/?>\n?')


def _new_image_url(rel: str) -> str:
    return f"https://mnemehq.com/{rel}{CARD_NAME}"


def rewrite(html: str, rel: str, alt: str) -> str:
    """Repoint og:image/twitter:image to og-v2.png and stamp the four
    image-metadata tags. Idempotent: running this twice on its own
    output produces identical output.
    """
    url = _new_image_url(rel)
    escaped_alt = html_mod.escape(alt, quote=True)

    # Strip any previously-inserted metadata tags so re-running this
    # doesn't duplicate them (idempotence).
    for pattern in (OG_WIDTH_RE, OG_HEIGHT_RE, OG_ALT_RE, TWITTER_ALT_RE):
        html = pattern.sub("", html)

    def _repoint_og(match: "re.Match[str]") -> str:
        inserted = (
            f'<meta property="og:image" content="{url}" />\n'
            f'<meta property="og:image:width" content="1200" />\n'
            f'<meta property="og:image:height" content="630" />\n'
            f'<meta property="og:image:alt" content="{escaped_alt}" />'
        )
        return inserted

    def _repoint_twitter(match: "re.Match[str]") -> str:
        return (
            f'<meta name="twitter:image" content="{url}" />\n'
            f'<meta name="twitter:image:alt" content="{escaped_alt}" />'
        )

    html = OG_IMAGE_RE.sub(_repoint_og, html, count=1)
    html = TWITTER_IMAGE_RE.sub(_repoint_twitter, html, count=1)
    return html


def _rel_for(index_html: Path) -> str:
    """site/foo/bar/index.html -> 'foo/bar/'; site/index.html -> ''."""
    rel = index_html.parent.relative_to(SITE).as_posix()
    return "" if rel == "." else rel + "/"


def main(argv: list[str] | None = None) -> int:
    raw = og_manifest.load(MANIFEST)

    updated = 0
    for path in sorted(SITE.rglob("index.html")):
        with open(path, "r", encoding="utf-8", newline="") as f:
            source = f.read()
        if OG_IMAGE_RE.search(source) is None:
            continue

        rel = _rel_for(path)
        record = og_manifest.resolve(rel, raw.get(rel), strict=True)
        alt = record["alt"]

        out = rewrite(source, rel, alt)
        if out != source:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(out)
            updated += 1

    print(f"OK -- synced {updated} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
