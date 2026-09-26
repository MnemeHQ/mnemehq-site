#!/usr/bin/env python3
"""Sync the docs switcher (breadcrumb dropdown) across every /docs/* page.

Each doc page's last breadcrumb item is a <details> dropdown listing every
doc, grouped, with the current page marked. DOCS below is the single source
of truth: add a page here, then run this script.

Rendering is shared with scripts/sync_integrations_nav.py via
scripts/page_switcher.py.

Usage:
    python scripts/sync_docs_nav.py          # rewrite pages in place
    python scripts/sync_docs_nav.py --check  # CI: fail if any page is stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page_switcher import render_block, splice  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "site" / "docs"

# (group label, [(slug, label)]). Slug "" is the docs overview page.
DOCS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Start here", [
        ("", "Docs overview"),
        ("how-enforcement-works", "How enforcement works"),
        ("decision-model", "Decision model"),
    ]),
    ("Guides", [
        ("protection-activation", "Protection activation"),
        ("decision-proposals", "Decision proposals"),
    ]),
    ("Reference", [
        ("cli", "CLI reference"),
        ("mcp", "MCP server"),
        ("supported-languages", "Supported languages"),
        ("governance-violations", "Governance violations"),
    ]),
    ("Methodology", [
        ("benchmark-methodology", "Benchmark methodology"),
    ]),
]


def href(slug: str) -> str:
    return f"/docs/{slug}/" if slug else "/docs/"


def render(current: str) -> str:
    current_label = next(l for _, items in DOCS for s, l in items if s == current)
    groups = [
        (group, [(href(s), l, s == current) for s, l in items])
        for group, items in DOCS
    ]
    return render_block(
        current_label=current_label,
        groups=groups,
        more_href="/integrations/",
        more_label="Integration guides",
        aria_label="All docs",
        sr_noun="page",
    )


def pages() -> list[tuple[str, Path]]:
    return [
        (s, DOCS_DIR / s / "index.html")
        for _, items in DOCS
        for s, _ in items
        if s  # the overview page lists every doc already
    ]


def sync(check: bool) -> int:
    stale = []
    for slug, path in pages():
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        eol = "\r\n" if "\r\n" in text else "\n"
        block = render(slug).replace("\n", eol)
        new, ok = splice(text, block)
        if not ok:
            print(f"sync_docs_nav: no breadcrumb anchor in {path.relative_to(ROOT)}")
            return 1
        if new != text:
            stale.append(path)
            if not check:
                path.write_bytes(new.encode("utf-8"))
    if check and stale:
        print("sync_docs_nav: FAIL, stale docs switcher in:")
        for p in stale:
            print(f"  {p.relative_to(ROOT)}")
        print("Run: python scripts/sync_docs_nav.py")
        return 1
    verb = "OK" if check else f"updated {len(stale)} page(s)"
    print(f"sync_docs_nav: {verb} ({len(pages())} doc pages)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    return sync(ap.parse_args().check)


if __name__ == "__main__":
    sys.exit(main())
