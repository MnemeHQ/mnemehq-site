#!/usr/bin/env python3
"""Strict coverage and reproducibility gate for the OG card manifest.

Three things can go wrong once cards are generated from a manifest instead
of hand-maintained per page, and none of them show up by looking at the
manifest alone:

  1. A page ships with no manifest record at all -- it would fall back to
     a silently-derived generic card (see og_manifest.resolve's docstring
     on why that is exactly the drift this system replaces).
  2. A manifest record survives after its page is deleted or renamed --
     dead weight that will confuse the next person editing cards.yaml.
  3. A page advertises an og:image that the manifest cannot actually
     reproduce (wrong filename, stale URL, hand-edited tag) -- so what
     ships to Twitter/Slack/etc. silently diverges from what render_og.py
     would produce.

`audit()` is the pure, testable core. `main()` gathers the real inputs:
every site/**/index.html that carries an og:image tag (pages without one,
like the audit/workspace/ tool SPA, are out of scope for OG cards --
noindex, no OpenGraph tags at all, nothing to reproduce) and the manifest
at site/og/cards.yaml.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import og_manifest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
MANIFEST = REPO / "site" / "og" / "cards.yaml"
CARD_NAME = "og-v2.png"

OG_IMAGE_RE = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"')


def _rel_for(index_html: Path) -> str:
    """site/foo/bar/index.html -> 'foo/bar/'; site/index.html -> ''."""
    rel = index_html.parent.relative_to(SITE).as_posix()
    return "" if rel == "." else rel + "/"


def _og_image_path(html: str) -> str | None:
    """The og:image URL's path, with the domain and leading slash stripped."""
    m = OG_IMAGE_RE.search(html)
    if m is None:
        return None
    return urlparse(m.group(1)).path.lstrip("/")


def pages() -> list[str]:
    """Site-relative page paths that participate in the OG card system.

    A page participates iff it carries an og:image tag at all -- that
    excludes tool/app pages like audit/workspace/ (noindex, no OpenGraph
    tags whatsoever), the same pages the legacy og.png system never
    covered either.
    """
    out = []
    for path in sorted(SITE.rglob("index.html")):
        html = path.read_text(encoding="utf-8")
        if _og_image_path(html) is None:
            continue
        out.append(_rel_for(path))
    return out


def advertised() -> dict[str, str]:
    """rel page path -> the og:image URL's path (domain stripped)."""
    result: dict[str, str] = {}
    for path in sorted(SITE.rglob("index.html")):
        html = path.read_text(encoding="utf-8")
        img = _og_image_path(html)
        if img is None:
            continue
        result[_rel_for(path)] = img
    return result


def audit(pages: list[str], manifest: dict, advertised: dict) -> list[str]:
    """Return coverage/reproducibility errors. Pure -- no filesystem I/O."""
    errors: list[str] = []
    page_set = set(pages)

    # 1 & 3-ish: every page must have a record, and that record must
    # resolve cleanly in strict mode (catches lines/headline mismatches).
    for rel in pages:
        raw = manifest.get(rel)
        try:
            og_manifest.resolve(rel, raw, strict=True)
        except og_manifest.ManifestError as exc:
            errors.append(str(exc))

    # 2: every record must have a page.
    for rel in manifest:
        if rel not in page_set:
            errors.append(f"{rel or '<home>'}: manifest record has no page (orphan)")

    # 3: what the page advertises must be exactly what render_og.py would
    # produce for that record -- <path>og-v2.png.
    for rel in pages:
        if rel not in manifest:
            continue  # already flagged above
        expected = f"{rel}{CARD_NAME}"
        got = advertised.get(rel)
        if got is not None and got != expected:
            errors.append(
                f"{rel or '<home>'}: og:image advertises {got!r}, not reproducible "
                f"from the manifest (expected {expected!r})")

    return errors


def main() -> int:
    manifest = og_manifest.load(MANIFEST)
    errors = audit(pages(), manifest, advertised())

    for e in errors:
        print(f"ERROR -- {e}")

    if errors:
        print(f"{len(errors)} coverage issue(s) found")
        return 1
    print(f"OK -- {len(manifest)} record(s), 0 coverage issue(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
