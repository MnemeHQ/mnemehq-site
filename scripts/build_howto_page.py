#!/usr/bin/env python3
"""Build how-to guide pages from their sources in templates/howto/.

Each source, templates/howto/<slug>.html (``_hub.html`` for /docs/how-to/), is
a JSON header between ``<!--meta`` and ``-->`` followed by the page body.
The builder wraps the body in the shared docs chrome (head, nav, footer),
writes site/docs/how-to/<slug>/index.html, and fills every empty
``<pre data-fixture="out:STEP">`` or ``<pre data-fixture="file:PATH">`` from
the guide's fixture in tests/howto/<slug>/, so recorded output is pasted, never
retyped. ``data-lines="A-B"`` keeps only those lines (1-based, inclusive).

After building, run:
    python scripts/sync_docs_nav.py      # fills the breadcrumb switcher
    python scripts/check_howto.py        # verifies blocks against fixtures

Usage:
    python scripts/build_howto_page.py SLUG [SLUG ...]   # e.g. _hub adr-to-enforceable-decision
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1]
SRC = W / "templates" / "howto"
CHROME = (W / "site/docs/decision-model/index.html").read_text(encoding="utf-8")

EXTRA_CSS = """
    .howto-meta { font-family: 'DM Mono', monospace; font-size: 0.74rem; letter-spacing: 0.04em; color: var(--muted); margin-top: 1.4rem; }
    .end-up { margin-top: 0.85rem; font-size: 0.95rem; color: var(--text); line-height: 1.7; max-width: 720px; }
    .end-up strong { color: var(--accent); font-weight: 500; }
    .prose-section h3 { font-family: 'Inter', sans-serif; font-size: 0.98rem; font-weight: 600; margin: 1.75rem 0 0.6rem; color: var(--text); }
    .prose-section ul.plain { margin: 0.25rem 0 1rem 1.2rem; color: var(--muted); font-size: 0.93rem; line-height: 1.85; }
    .prose-section ul.plain li { margin-bottom: 0.35rem; }
    .prose-section ul.plain li code, .prose-section h3 code, .ref-table td code, .end-up code { font-family: 'DM Mono', monospace; font-size: 0.84em; color: var(--text); background: var(--surface2); border: 1px solid var(--border); border-radius: 4px; padding: 0.05rem 0.35rem; }
    .prose-section ul.plain li a, .ref-table td a, .bound-list a { color: var(--accent); text-decoration: none; }
    .term-label { font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 1.1rem 0 0.4rem; }
    .term-block { margin-top: 0; }
    .hero p.lede code { font-family: 'DM Mono', monospace; font-size: 0.86em; color: var(--text); }
    .bound-list .term-block { margin: 0.6rem 0; }
    .ref-table td:first-child { white-space: normal; }
"""


def chrome_parts():
    head_start = CHROME[: CHROME.index("  <title>")]
    consent = CHROME[CHROME.index("  <!-- Consent defaults -->") : CHROME.index('  <link rel="icon"')]
    icon = '  <link rel="icon" href="/favicon-v2.png" type="image/png">\n'
    style_start = CHROME.index("  <style>")
    style_end = CHROME.index("  </style>", style_start)
    style = CHROME[style_start:style_end] + EXTRA_CSS + "  </style>\n"
    body_start = CHROME[CHROME.index("\n</head>") : CHROME.index('<main id="main-content" tabindex="-1">')]
    body_start += '<main id="main-content" tabindex="-1">\n'
    tail = CHROME[CHROME.index("</main>") :]
    return head_start, consent, icon, style, body_start, tail


def fill_blocks(body: str, fixture: Path) -> str:
    def repl(m):
        attrs, inner = m.group(1), m.group(2)
        fx = re.search(r'data-fixture="([^"]+)"', attrs)
        lines = re.search(r'\s*data-lines="(\d+)-(\d+)"', attrs)
        attrs = re.sub(r'\s*data-lines="[^"]*"', "", attrs)
        if not fx or inner.strip():
            return f"<pre{attrs}>{inner}</pre>"
        kind, _, ref = fx.group(1).partition(":")
        if kind == "out":
            text = (fixture / "expected" / f"{ref}.txt").read_text(encoding="utf-8")
            text = re.sub(r"\nexit=\d+\n?$", "\n", "\n" + text)[1:]
        elif kind == "file":
            text = (fixture / ref).read_text(encoding="utf-8")
        else:
            raise SystemExit(f"empty cmd block in {fixture.name}")
        rows = text.rstrip("\n").split("\n")
        if lines:
            a, b = int(lines.group(1)), int(lines.group(2))
            rows = rows[a - 1 : b]
        return f"<pre{attrs}>{html.escape(chr(10).join(rows).rstrip(), quote=False)}</pre>"

    return re.sub(r"<pre([^>]*)>(.*?)</pre>", repl, body, flags=re.S)


def jsonld(meta, crumbs):
    items = [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
        for i, (n, u) in enumerate(crumbs)
    ]
    graph = [{"@type": "BreadcrumbList", "itemListElement": items}]
    if meta.get("collection"):
        graph.append({
            "@type": "CollectionPage",
            "name": meta["h1_plain"],
            "description": meta["description"],
            "url": meta["url"],
            "hasPart": [{"@type": "TechArticle", "name": n, "url": u} for n, u in meta["collection"]],
        })
    else:
        graph.append({
            "@type": "TechArticle",
            "headline": meta["h1_plain"],
            "description": meta["description"],
            "url": meta["url"],
            "datePublished": meta["date"],
            "dateModified": meta.get("modified", meta["date"]),
            "proficiencyLevel": "Beginner",
            "author": {"@type": "Person", "name": "Theo Valmis", "url": "https://mnemehq.com/founder/"},
            "publisher": {"@type": "Organization", "name": "Mneme HQ", "url": "https://mnemehq.com/",
                          "logo": {"@type": "ImageObject", "url": "https://mnemehq.com/logo-v3.png"}},
        })
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    return '  <script type="application/ld+json">\n' + body + "\n  </script>\n"


def build(slug: str) -> Path:
    raw = (SRC / f"{slug}.html").read_text(encoding="utf-8")
    meta = json.loads(raw[raw.index("<!--meta") + 8 : raw.index("-->")])
    body = raw[raw.index("-->") + 3 :].strip("\n")
    is_hub = slug == "_hub"
    path_part = "docs/how-to/" if is_hub else f"docs/how-to/{slug}/"
    meta["url"] = f"https://mnemehq.com/{path_part}"
    if not is_hub:
        body = fill_blocks(body, W / "tests/howto" / slug)
    head_start, consent, icon, style, body_start, tail = chrome_parts()
    e = lambda s: html.escape(s, quote=True)
    og_img = f"https://mnemehq.com/{path_part}og-v2.png"
    head = (
        head_start
        + f"  <title>{meta['title']}</title>\n"
        + '  <link rel="preload" href="/assets/fonts/InstrumentSerif-400.woff2" as="font" type="font/woff2" crossorigin>\n'
        + '  <link rel="preload" href="/assets/fonts/Inter-400.woff2" as="font" type="font/woff2" crossorigin>\n'
        + '  <link rel="stylesheet" href="/assets/css/fonts.css">\n'
        + '  <link rel="stylesheet" href="/assets/css/base.css?v=20260921">\n'
        + f'  <meta name="description" content="{e(meta["description"])}" />\n'
        + '  <meta name="robots" content="index, follow" />\n'
        + '  <meta name="theme-color" content="#0c0c0d" />\n'
        + '  <meta name="mneme:content-segment" content="developer_evaluation" />\n'
        + f'  <link rel="canonical" href="{meta["url"]}" />\n'
        + '  <link rel="dns-prefetch" href="https://www.googletagmanager.com" />\n'
        + '  <meta property="og:type" content="article" />\n'
        + '  <meta property="og:site_name" content="Mneme HQ" />\n'
        + f'  <meta property="og:title" content="{meta["title"]}" />\n'
        + f'  <meta property="og:description" content="{e(meta["description"])}" />\n'
        + f'  <meta property="og:url" content="{meta["url"]}" />\n'
        + f'  <meta property="og:image" content="{og_img}" />\n'
        + '<meta property="og:image:width" content="1200" />\n'
        + '<meta property="og:image:height" content="630" />\n'
        + f'<meta property="og:image:alt" content="{e(meta["og_alt"])}" />\n'
        + '  <meta name="twitter:card" content="summary_large_image" />\n'
        + f'  <meta name="twitter:title" content="{meta["title"]}" />\n'
        + f'  <meta name="twitter:description" content="{e(meta["description"])}" />\n'
        + f'  <meta name="twitter:image" content="{og_img}" />\n'
        + f'<meta name="twitter:image:alt" content="{e(meta["og_alt"])}" />\n'
        + consent + icon
    )
    crumbs = [("Home", "https://mnemehq.com/"), ("Docs", "https://mnemehq.com/docs/")]
    if is_hub:
        crumbs.append(("How-to guides", "https://mnemehq.com/docs/how-to/"))
    else:
        crumbs += [("How-to guides", "https://mnemehq.com/docs/how-to/"), (meta["crumb"], meta["url"])]
    head += jsonld(meta, crumbs) + style
    crumb_html = (
        '<nav aria-label="Breadcrumb" class="breadcrumb-nav">\n  <ol class="breadcrumb">\n'
        '    <li><a href="/">Home</a></li>\n    <li><a href="/docs/">Docs</a></li>\n'
        + ("" if is_hub else '    <li><a href="/docs/how-to/">How-to guides</a></li>\n')
        + "    <!-- mneme:page-switcher:start --><!-- mneme:page-switcher:end -->\n  </ol>\n</nav>\n\n"
    )
    hero = (
        '<section class="hero">\n'
        f'  <div class="section-eyebrow">{meta["eyebrow"]}</div>\n'
        f'  <h1>{meta["h1"]}</h1>\n'
        f'  <p class="lede">{meta["lede"]}</p>\n'
    )
    if not is_hub:
        hero += (
            f'  <p class="howto-meta">~{meta["minutes"]} min &middot; Tested with mneme-hq 0.9.2 &middot; {meta["surface"]}</p>\n'
            f'  <p class="end-up"><strong>You&rsquo;ll end up with:</strong> {meta["end_up"]}</p>\n'
        )
    hero += "</section>\n\n"
    page = head + body_start + crumb_html + hero + '<div class="wrap">\n\n' + body + "\n\n</div>\n\n" + tail
    out = W / "site" / path_part / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        print(build(slug))
