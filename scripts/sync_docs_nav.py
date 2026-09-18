#!/usr/bin/env python3
"""Sync the docs switcher (breadcrumb dropdown) across every /docs/* page.

Each doc page's last breadcrumb item is a <details> dropdown listing every
doc, grouped, with the current page marked. DOCS below is the single source
of truth: add a page here, then run this script.

Usage:
    python scripts/sync_docs_nav.py          # rewrite pages in place
    python scripts/sync_docs_nav.py --check  # CI: fail if any page is stale

The block lives between <!-- mneme:docs-nav:start --> and
<!-- mneme:docs-nav:end -->. On a page without markers, the script replaces
the breadcrumb's `<li aria-current="page">...</li>` item. Styles live in
site/assets/css/base.css under "Docs switcher".
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "site" / "docs"

# (group label, [(slug, label)]). Slug "" is the docs overview page.
DOCS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Start here", [
        ("", "Docs overview"),
        ("how-enforcement-works", "How enforcement works"),
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

START = "<!-- mneme:docs-nav:start -->"
END = "<!-- mneme:docs-nav:end -->"
BLOCK_PAT = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
CURRENT_CRUMB_PAT = re.compile(r'<li aria-current="page">[^<]*</li>')

CHEVRON = (
    '<svg class="docs-switcher-chevron" width="10" height="10" viewBox="0 0 10 10" '
    'aria-hidden="true"><path d="M2 3.5 5 6.5 8 3.5" fill="none" stroke="currentColor" '
    'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

# Close on Escape (returning focus to the toggle) and on outside click.
SCRIPT = """<script>
(function(){
  var d = document.currentScript.parentNode.querySelector('.docs-switcher');
  if (!d) return;
  document.addEventListener('click', function(e){ if (d.open && !d.contains(e.target)) d.open = false; });
  d.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && d.open) { d.open = false; d.querySelector('summary').focus(); }
  });
})();
</script>"""


def href(slug: str) -> str:
    return f"/docs/{slug}/" if slug else "/docs/"


def render(current: str) -> str:
    label = next(l for _, items in DOCS for s, l in items if s == current)
    groups = []
    for group, items in DOCS:
        links = "\n".join(
            f'          <li><a href="{href(s)}"'
            + (' aria-current="page"' if s == current else "")
            + f">{l}</a></li>"
            for s, l in items
        )
        groups.append(
            '      <div class="docs-switcher-group">\n'
            f'        <div class="docs-switcher-label">{group}</div>\n'
            f"        <ul>\n{links}\n        </ul>\n"
            "      </div>"
        )
    return (
        f'{START}<li class="docs-switcher-item">\n'
        '    <details class="docs-switcher">\n'
        f'      <summary><span class="docs-switcher-sr">Current page: </span>{label} {CHEVRON}'
        '<span class="docs-switcher-sr"> (show all docs)</span></summary>\n'
        # A div, not <nav>: several pages carry bare `nav { position: sticky }`
        # rules that would otherwise restyle the panel.
        '      <div class="docs-switcher-panel" role="navigation" aria-label="All docs">\n'
        + "\n".join(groups)
        + '\n      <a class="docs-switcher-more" href="/integrations/">Integration guides &rarr;</a>\n'
        "      </div>\n"
        "    </details>\n"
        f"{SCRIPT}\n"
        f"    </li>{END}"
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
        if START in text:
            new = BLOCK_PAT.sub(lambda _: block, text, count=1)
        elif len(CURRENT_CRUMB_PAT.findall(text)) == 1:
            new = CURRENT_CRUMB_PAT.sub(lambda _: block, text, count=1)
        else:
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
