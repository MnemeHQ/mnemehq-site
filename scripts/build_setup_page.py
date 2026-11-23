#!/usr/bin/env python3
"""Build the /setup/ section from its sources in templates/setup/.

Each source, templates/setup/<slug>.html (``_hub.html`` for /setup/ itself), is
a JSON header between ``<!--meta`` and ``-->`` followed by the page body. The
builder reuses the how-to guide chrome and code-block styling from
scripts/build_howto_page.py, writes site/setup/<slug>/index.html, and fills
every empty ``<pre data-fixture="out:STEP">`` or ``<pre data-fixture="file:PATH">``
from tests/setup/, the outputs recorded from mneme-hq (scripts/core_version.json).

The hub's no-JavaScript chooser fallback (``<!-- setup:fallback -->``) is
rendered from site/assets/js/setup-chooser-data-v1.js, the same data the
interactive chooser reads, so the two cannot disagree.

After building, run:
    python scripts/check_setup_chooser.py   # chooser data vs the integration catalogue

Usage:
    python scripts/build_setup_page.py            # every page
    python scripts/build_setup_page.py _hub ci    # selected pages
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_howto_page as howto  # noqa: E402

W = Path(__file__).resolve().parents[1]
SRC = W / "templates" / "setup"
FIXTURE = W / "tests" / "setup"
DATA_JS = W / "site" / "assets" / "js" / "setup-chooser-data-v1.js"
SETUP_CSS = '  <link rel="stylesheet" href="/assets/css/setup-v1.css">\n'
HUB_URL = "https://mnemehq.com/setup/"


def chooser_data() -> dict:
    text = DATA_JS.read_text(encoding="utf-8")
    start = text.index("window.MNEME_SETUP_CHOOSER = ") + len("window.MNEME_SETUP_CHOOSER = ")
    return json.loads(text[start : text.rindex(";")])


def fallback_html(data: dict) -> str:
    """Grouped list of links: the chooser as plain HTML for readers without JS."""
    e = lambda s: html.escape(s, quote=True)
    out = ['<div class="chooser-fallback" data-chooser-fallback>']
    for group in data["groups"]:
        opts = [o for o in data["options"] if o["group"] == group["id"]]
        if not opts:
            continue
        out.append(f'  <div>\n    <h3>{e(group["label"])}</h3>\n    <ul>')
        for o in opts:
            href = o["guide"] or o["page"] or "/setup/ci/"
            intent = "setup" if href.startswith("/setup/") else "integration"
            status = f' <span class="fb-status">{e(o["status"])}</span>' if o["status"] else ""
            out.append(
                f'      <li><a href="{href}" data-cta-intent="{intent}" data-cta-position="mid" '
                f'data-cta-component="context">{e(o["name"])}</a>{status}</li>'
            )
        out.append("    </ul>\n  </div>")
    out.append("</div>")
    return "\n".join(out)


def jsonld(meta: dict, crumbs: list, image_url: str, guides: list) -> str:
    page_id = f"{meta['url']}#webpage"
    breadcrumb_id = f"{meta['url']}#breadcrumb"
    image = {"@type": "ImageObject", "url": image_url, "width": 1200, "height": 630}
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    graph = [{"@type": "BreadcrumbList", "@id": breadcrumb_id, "itemListElement": items}]
    publisher = {"@type": "Organization", "@id": "https://mnemehq.com/#organization", "name": "Mneme HQ",
                 "url": "https://mnemehq.com/", "logo": {"@type": "ImageObject", "url": "https://mnemehq.com/logo-v3.png"}}
    if meta.get("hub"):
        graph.append({
            "@type": "CollectionPage", "@id": page_id, "name": meta["h1_plain"],
            "description": meta["description"], "url": meta["url"], "inLanguage": "en",
            "datePublished": meta["date"], "dateModified": meta.get("modified", meta["date"]),
            "image": image, "breadcrumb": {"@id": breadcrumb_id}, "publisher": publisher,
            "hasPart": [{"@type": "TechArticle", "name": n, "url": u} for n, u in guides],
        })
    else:
        graph.append({
            "@type": ["Article", "TechArticle"], "@id": f"{meta['url']}#article",
            "headline": meta["h1_plain"], "description": meta["description"], "url": meta["url"],
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_id},
            "isPartOf": {"@type": "CollectionPage", "@id": f"{HUB_URL}#webpage", "name": "Set up Mneme", "url": HUB_URL},
            "inLanguage": "en", "datePublished": meta["date"], "dateModified": meta.get("modified", meta["date"]),
            "image": image, "proficiencyLevel": "Beginner",
            "author": {"@type": "Person", "@id": "https://mnemehq.com/founder/#person", "name": "Theo Valmis",
                       "url": "https://mnemehq.com/founder/"},
            "publisher": publisher,
        })
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    return '  <script type="application/ld+json">\n' + body + "\n  </script>\n"


def load(slug: str):
    raw = (SRC / f"{slug}.html").read_text(encoding="utf-8")
    meta = json.loads(raw[raw.index("<!--meta") + 8 : raw.index("-->")])
    body = raw[raw.index("-->") + 3 :].strip("\n")
    return meta, body


def guide_list() -> list:
    out = []
    for path in sorted(SRC.glob("*.html")):
        if path.stem == "_hub":
            continue
        meta, _ = load(path.stem)
        out.append((meta["order"], meta["h1_plain"], f"{HUB_URL}{path.stem}/"))
    return [(n, u) for _, n, u in sorted(out)]


def build(slug: str) -> Path:
    meta, body = load(slug)
    is_hub = slug == "_hub"
    meta["hub"] = is_hub
    path_part = "setup/" if is_hub else f"setup/{slug}/"
    meta["url"] = f"https://mnemehq.com/{path_part}"
    if is_hub:
        body = body.replace("<!-- setup:fallback -->", fallback_html(chooser_data()))
    body = howto.decorate_blocks(howto.fill_blocks(body, FIXTURE))
    head_start, consent, icon, style, body_start, tail = howto.chrome_parts()
    e = lambda s: html.escape(s, quote=True)
    og_img = howto.og_image_url(path_part)
    head = (
        head_start
        + f"  <title>{meta['title']}</title>\n"
        + '  <link rel="preload" href="/assets/fonts/InstrumentSerif-400.woff2" as="font" type="font/woff2" crossorigin>\n'
        + '  <link rel="preload" href="/assets/fonts/Inter-400.woff2" as="font" type="font/woff2" crossorigin>\n'
        + '  <link rel="stylesheet" href="/assets/css/fonts.css">\n'
        + '  <link rel="stylesheet" href="/assets/css/base.css?v=20261031">\n'
        + SETUP_CSS
        + f'  <meta name="description" content="{e(meta["description"])}" />\n'
        + '  <meta name="robots" content="index, follow" />\n'
        + '  <meta name="theme-color" content="#0c0c0d" />\n'
        + '  <meta name="mneme:content-segment" content="developer_evaluation" />\n'
        + f'  <link rel="canonical" href="{meta["url"]}" />\n'
        + '  <link rel="dns-prefetch" href="https://www.googletagmanager.com" />\n'
        + f'  <meta property="og:type" content="{"website" if is_hub else "article"}" />\n'
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
    crumbs = [("Home", "https://mnemehq.com/"), ("Setup", HUB_URL)]
    if not is_hub:
        crumbs.append((meta["crumb"], meta["url"]))
    head += jsonld(meta, crumbs, og_img, guide_list() if is_hub else []) + style
    crumb_html = (
        '<nav aria-label="Breadcrumb" class="breadcrumb-nav">\n  <ol class="breadcrumb">\n'
        '    <li><a href="/">Home</a></li>\n'
        + ('    <li><span aria-current="page">Setup</span></li>\n' if is_hub else
           '    <li><a href="/setup/">Setup</a></li>\n'
           f'    <li><span aria-current="page">{meta["crumb"]}</span></li>\n')
        + "  </ol>\n</nav>\n\n"
    )
    if is_hub:
        hero = (
            '<section class="setup-hero">\n'
            f'  <h1>{meta["h1"]}</h1>\n'
            f'  <p class="lede">{meta["lede"]}</p>\n'
            "</section>\n\n"
        )
        main = hero + '<div class="setup-wrap">\n\n' + body + "\n\n</div>\n\n"
        scripts = ('<script src="/assets/js/setup-chooser-data-v1.js"></script>\n'
                   '<script src="/assets/js/setup-chooser-v1.js"></script>\n')
        page_tail = tail.replace("</body>", howto.COPY_SCRIPT + scripts + "\n</body>")
    else:
        version = json.loads((W / "scripts" / "core_version.json").read_text())["minimum_version"]
        modified = meta.get("modified", meta["date"])
        strip = [
            f"Tested with mneme-hq {version}",
            f'Updated <time datetime="{modified}">{howto.display_date(modified)}</time>',
            'By <a href="/founder/">Theo Valmis</a>',
            meta["surface"],
        ]
        chips = "".join(
            f'<span class="layer-chip layer-chip--{kind}">{label}</span>' for kind, label in meta["layers"]
        )
        toc = "".join(f'    <a href="#{a}">{t}</a>\n' for a, t in meta["toc"])
        hero = (
            '<section class="hero">\n'
            f'  <div class="section-eyebrow">{meta["eyebrow"]}</div>\n'
            f'  <h1>{meta["h1"]}</h1>\n'
            f'  <p class="lede">{meta["answer"]}</p>\n'
            f'  <p class="howto-meta byline">{" &middot; ".join(strip)}</p>\n'
            f'  <div class="layer-strip" aria-label="Layers this guide sets up">{chips}</div>\n'
            f'  <p class="end-up"><strong>You&rsquo;ll end up with:</strong> {meta["end_up"]}</p>\n'
            '  <nav class="howto-toc" aria-label="On this page">\n'
            '    <span class="howto-toc-label">On this page</span>\n'
            + toc
            + "  </nav>\n</section>\n\n"
        )
        main = hero + '<div class="wrap">\n\n' + body + "\n\n</div>\n\n"
        page_tail = tail.replace("</body>", howto.COPY_SCRIPT + "\n</body>")
    page = head + body_start + crumb_html + main + page_tail
    out = W / "site" / path_part / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    slugs = sys.argv[1:] or sorted(p.stem for p in SRC.glob("*.html"))
    for slug in slugs:
        print(build(slug))
