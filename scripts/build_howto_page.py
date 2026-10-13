#!/usr/bin/env python3
"""Build how-to guide pages from their sources in templates/howto/.

Each source, templates/howto/<slug>.html (``_hub.html`` for /docs/how-to/), is
a JSON header between ``<!--meta`` and ``-->`` followed by the page body.
The builder wraps the body in the shared docs chrome (head, nav, footer),
writes site/docs/how-to/<slug>/index.html, and fills every empty
``<pre data-fixture="out:STEP">`` or ``<pre data-fixture="file:PATH">`` from
the guide's fixture in tests/howto/<slug>/, so recorded output is pasted, never
retyped. ``data-lines="A-B"`` keeps only those lines (1-based, inclusive).

A guide's ``answer`` field is its opening paragraph under the title: a direct
answer to the guide's question. The hub, which has no answer, uses ``lede``.

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
from datetime import date
from pathlib import Path

W = Path(__file__).resolve().parents[1]
SRC = W / "templates" / "howto"
MANIFEST = W / "site" / "og" / "cards.yaml"


def og_image_url(path_part: str) -> str:
    """The page's OG card URL, using the card filename its manifest record names."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import og_manifest

    record = og_manifest.resolve(path_part, og_manifest.load(MANIFEST).get(path_part), strict=True)
    return f"https://mnemehq.com/{path_part}{record['card']}"
CHROME = (W / "site/docs/decision-model/index.html").read_text(encoding="utf-8")

EXTRA_CSS = """
    .howto-meta.byline { font-family: 'DM Mono', monospace; font-size: 0.74rem; letter-spacing: 0.04em; color: var(--muted); margin-top: 1.4rem; }
    .howto-meta a { color: inherit; text-decoration-color: var(--border); text-underline-offset: 0.2em; }
    .howto-meta a:hover { color: var(--text); }
    .end-up { margin-top: 0.85rem; font-size: 0.95rem; color: var(--text); line-height: 1.7; max-width: 720px; }
    .end-up strong { color: var(--accent); font-weight: 500; }
    .howto-toc { display: flex; flex-wrap: wrap; align-items: center; gap: 0.55rem 1rem; margin-top: 1.15rem; max-width: 760px; font-size: 0.78rem; }
    .howto-toc-label { font-family: 'DM Mono', monospace; letter-spacing: 0.07em; text-transform: uppercase; color: var(--muted); }
    .howto-toc a { color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border); padding-bottom: 0.08rem; }
    .howto-toc a:hover { color: var(--accent); border-color: var(--accent); }
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


def display_date(iso_date: str) -> str:
    value = date.fromisoformat(iso_date)
    return f"{value.strftime('%b')} {value.day}, {value.year}"


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


def jsonld(meta, crumbs, image_url):
    page_id = f"{meta['url']}#webpage"
    breadcrumb_id = f"{meta['url']}#breadcrumb"
    image = {
        "@type": "ImageObject",
        "@id": f"{meta['url']}#primaryimage",
        "url": image_url,
        "contentUrl": image_url,
        "width": 1200,
        "height": 630,
    }
    items = [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
        for i, (n, u) in enumerate(crumbs)
    ]
    graph = [{"@type": "BreadcrumbList", "@id": breadcrumb_id, "itemListElement": items}]
    if meta.get("collection"):
        item_list_id = f"{meta['url']}#itemlist"
        article_refs = [
            {
                "@type": ["Article", "TechArticle"],
                "@id": f"{url}#article",
                "headline": name,
                "name": name,
                "url": url,
            }
            for name, url in meta["collection"]
        ]
        graph.append({
            "@type": "CollectionPage",
            "@id": page_id,
            "name": meta["h1_plain"],
            "description": meta["description"],
            "url": meta["url"],
            "inLanguage": "en",
            "datePublished": meta["date"],
            "dateModified": meta.get("modified", meta["date"]),
            "image": image,
            "breadcrumb": {"@id": breadcrumb_id},
            "isPartOf": {
                "@type": "WebSite",
                "@id": "https://mnemehq.com/#website",
                "name": "Mneme HQ",
                "url": "https://mnemehq.com/",
            },
            "mainEntity": {"@id": item_list_id},
            "hasPart": article_refs,
        })
        graph.append({
            "@type": "ItemList",
            "@id": item_list_id,
            "name": "Mneme how-to guides",
            "numberOfItems": len(article_refs),
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@id": article["@id"]}}
                for i, article in enumerate(article_refs)
            ],
        })
    else:
        graph.append({
            "@type": ["Article", "TechArticle"],
            "@id": f"{meta['url']}#article",
            "headline": meta["h1_plain"],
            "description": meta["description"],
            "url": meta["url"],
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_id},
            "isPartOf": {
                "@type": "CollectionPage",
                "@id": "https://mnemehq.com/docs/how-to/#webpage",
                "name": "How-to guides",
                "url": "https://mnemehq.com/docs/how-to/",
            },
            "inLanguage": "en",
            "datePublished": meta["date"],
            "dateModified": meta.get("modified", meta["date"]),
            "image": image,
            "proficiencyLevel": "Beginner",
            "author": {"@type": "Person", "@id": "https://mnemehq.com/founder/#person",
                       "name": "Theo Valmis", "url": "https://mnemehq.com/founder/"},
            "publisher": {"@type": "Organization", "@id": "https://mnemehq.com/#organization",
                          "name": "Mneme HQ", "url": "https://mnemehq.com/",
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
    og_img = og_image_url(path_part)
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
    head += jsonld(meta, crumbs, og_img) + style
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
        # The lede is the guide's direct answer when it has one, so readers and
        # answer engines get the answer first, right under the title.
        f'  <p class="lede">{meta.get("answer") or meta["lede"]}</p>\n'
    )
    if not is_hub:
        # Minutes appear only once a timed reader run has measured them.
        version = json.loads((W / "scripts" / "core_version.json").read_text())["minimum_version"]
        modified = meta.get("modified", meta["date"])
        strip = [
            f'Tested with mneme-hq {version}',
            f'Updated <time datetime="{modified}">{display_date(modified)}</time>',
            f'By <a href="/founder/">Theo Valmis</a>',
            meta["surface"],
        ]
        if meta.get("minutes"):
            strip.insert(0, f"~{meta['minutes']} min")
        hero += (
            f'  <p class="howto-meta byline">{" &middot; ".join(strip)}</p>\n'
            f'  <p class="end-up"><strong>You&rsquo;ll end up with:</strong> {meta["end_up"]}</p>\n'
            '  <nav class="howto-toc" aria-label="On this page">\n'
            '    <span class="howto-toc-label">On this page</span>\n'
            '    <a href="#prerequisites">Prerequisites</a>\n'
            '    <a href="#configure">Configure</a>\n'
            '    <a href="#run">Run</a>\n'
            '    <a href="#expected-result">Expected result</a>\n'
            '    <a href="#troubleshooting">Troubleshooting</a>\n'
            '  </nav>\n'
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
