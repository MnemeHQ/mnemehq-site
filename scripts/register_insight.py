"""register_insight.py - register a queued insight article on the site.

Reads the article's manifest at ``publish-queue/<slug>.json`` and performs
every manual registration step from docs/site/insight-publishing-contract.md
in one idempotent pass:

1. re-dates the article page to the publish date (article:published_time,
   datePublished/dateModified, byline <time>);
2. adds the sitemap ``<url>`` block;
3. adds the archive card (inside the primary topic's ``cards-section``) and
   its ``CollectionPage.hasPart`` entry;
4. adds the topic-hub card and ``hasPart`` entry;
5. adds the OG record to ``site/og/cards.yaml`` (headline + alt) in key order;
6. adds reciprocal links from the related articles listed in the manifest;
7. bumps the archive ``dateModified`` and the /insights/all/ sitemap
   ``lastmod`` to the publish date;
8. parks links to insights not yet on the site and restores parked links to
   this one (see ``settle_links``), so queued articles that link to each
   other never publish a dead link;
9. runs ``sync_insights_catalog.py`` (archive dates + homepage latest set).

It does not render the OG card: ``og-v2.png`` is committed with the article
(rendering needs Chromium, which CI does not have). Run
``render_og.py --strict --out site --only insights/<slug>/`` locally before
queueing.

The scheduled publisher (.github/workflows/scheduled-publish.yml) runs this on
a fresh checkout of ``main`` at publish time, so queued article PRs never
conflict with each other on the shared index files.

Usage:
  python scripts/register_insight.py <slug> [--date YYYY-MM-DD]

Manifest fields: slug, title, description, type, topic, read_time,
og_headline, og_alt, publish_on, reciprocal (list of {host, desc}).
``--date`` overrides ``publish_on``.

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QUEUE = ROOT / "publish-queue"
REQUIRED = ("slug", "title", "description", "type", "topic", "read_time",
            "og_headline", "og_alt", "publish_on")


_CRLF: set[Path] = set()


def read(path: Path) -> str:
    """Read with newlines normalised to \\n, remembering whether the file uses CRLF.

    Some files (site/og/cards.yaml) are stored with CRLF; rewriting them with LF
    turns a three-line registration into a whole-file diff.
    """
    raw = path.read_bytes().decode("utf-8")
    if "\r\n" in raw:
        _CRLF.add(path)
    return raw.replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    if path in _CRLF:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def load_manifest(slug: str) -> dict:
    path = QUEUE / f"{slug}.json"
    if not path.exists():
        sys.exit(f"FATAL: manifest missing: {path.relative_to(ROOT)}")
    m = json.loads(read(path))
    missing = [k for k in REQUIRED if not m.get(k)]
    if missing:
        sys.exit(f"FATAL: manifest {path.name} missing: {', '.join(missing)}")
    if m["slug"] != slug:
        sys.exit(f"FATAL: manifest slug {m['slug']!r} does not match {slug!r}")
    return m


def redate_article(m: dict, date: str) -> None:
    path = SITE / "insights" / m["slug"] / "index.html"
    if not path.exists():
        sys.exit(f"FATAL: article missing: {path.relative_to(ROOT)}")
    s = read(path)
    human = dt.date.fromisoformat(date).strftime("%B %Y")
    s = re.sub(r'(<meta property="article:published_time" content=")[0-9-]{10}(T00:00:00Z")',
               rf"\g<1>{date}\g<2>", s)
    s = re.sub(r'("datePublished":\s*")[0-9-]{10}(")', rf"\g<1>{date}\g<2>", s)
    s = re.sub(r'("dateModified":\s*")[0-9-]{10}(")', rf"\g<1>{date}\g<2>", s)
    s = re.sub(r'(<span class="sep">&middot;</span><time datetime=")[0-9-]{10}(">)[^<]*(</time>)',
               rf"\g<1>{date}\g<2>{human}\g<3>", s)
    write(path, s)


def has_part(m: dict, indent: str) -> str:
    url = f"https://mnemehq.com/insights/{m['slug']}/"
    return f'{indent}{{"@type": "Article", "name": {json.dumps(m["title"], ensure_ascii=False)}, "url": "{url}"}},\n'


def insert_after(s: str, marker: str, text: str, start: int = 0) -> str:
    i = s.index(marker, start) + len(marker)
    return s[:i] + text + s[i:]


def register_sitemap(m: dict, date: str) -> None:
    path = SITE / "sitemap.xml"
    s = read(path)
    loc = f"https://mnemehq.com/insights/{m['slug']}/"
    if f"<loc>{loc}</loc>" not in s:
        block = (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{date}</lastmod>\n"
                 f"    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n")
        s = s.replace("</urlset>", block + "</urlset>")
    s = re.sub(r"(<loc>https://mnemehq\.com/insights/all/</loc>\s*<lastmod>)[0-9-]{10}(</lastmod>)",
               rf"\g<1>{date}\g<2>", s)
    write(path, s)


def register_archive(m: dict, date: str) -> None:
    path = SITE / "insights" / "all" / "index.html"
    s = read(path)
    href = f"/insights/{m['slug']}/"
    if f'href="{href}"' not in s:
        s = insert_after(s, '"hasPart": [\n', has_part(m, "      "))
        section = s.index(f'<div class="cards-section" id="{m["topic"]}">')
        human = dt.date.fromisoformat(date).strftime("%b %-d, %Y") if sys.platform != "win32" \
            else dt.date.fromisoformat(date).strftime("%b %#d, %Y")
        card = f'''      <a href="{href}" class="insight-card-link" data-published="{date}">
        <div class="insight-card">
          <div class="card-meta">
            <span class="card-tag">{m["type"]}</span>
            <span class="card-dot"></span>
            <time class="card-date" datetime="{date}">{human}</time>
            <span class="card-dot"></span>
            <span class="card-read-time">{m["read_time"]}</span>
          </div>
          <h3>{esc(m["title"])}</h3>
          <p>{esc(m["description"])}</p>
          <div class="card-footer">
            <span class="read-pill">Read insight</span>
          </div>
        </div>
      </a>
'''
        s = insert_after(s, '<div class="cards-grid">\n', card, section)
    s = re.sub(r'("url": "https://mnemehq\.com/insights/all/",\s*"dateModified": ")[0-9-]{10}(")',
               rf"\g<1>{date}\g<2>", s)
    write(path, s)


def register_hub(m: dict) -> None:
    path = SITE / "insights" / "topics" / m["topic"] / "index.html"
    s = read(path)
    href = f"/insights/{m['slug']}/"
    if f'href="{href}"' in s:
        return
    s = insert_after(s, '"hasPart": [\n', has_part(m, "          "))
    section = s.index('<span class="section-label">More in ')
    card = f'''
      <a href="{href}" class="insight-card-link">
        <div class="insight-card">
          <div class="card-meta"><span class="card-tag">{m["type"]}</span><span class="card-dot"></span><span class="card-read-time">{m["read_time"]}</span></div>
          <h2>{esc(m["title"])}</h2>
          <p>{esc(m["description"])}</p>
          <div class="card-footer"><span class="read-pill">Read insight</span></div>
        </div>
      </a>
'''
    write(path, insert_after(s, '<div class="cards-grid">\n', card, section))


def register_og(m: dict) -> None:
    path = SITE / "og" / "cards.yaml"
    s = read(path)
    key = f"insights/{m['slug']}/:"
    if re.search(rf"^{re.escape(key)}\n", s, re.M):
        return
    record = (f"{key}\n  alt: {json.dumps(m['og_alt'], ensure_ascii=False)}\n"
              f"  headline: {json.dumps(m['og_headline'], ensure_ascii=False)}\n")
    for match in re.finditer(r"^insights/[^\n]*:\n", s, re.M):
        if match.group(0) > key + "\n":
            write(path, s[:match.start()] + record + s[match.start():])
            return
    sys.exit("FATAL: no insertion point for the OG record in cards.yaml")


def register_reciprocal(m: dict) -> None:
    href = f"/insights/{m['slug']}/"
    for link in m.get("reciprocal", []):
        path = SITE / "insights" / link["host"] / "index.html"
        if not path.exists():
            sys.exit(f"FATAL: reciprocal host missing: {link['host']}")
        s = read(path)
        if href in s:
            continue
        if '<ul class="related-list">' in s:
            item = (f'      <li><a href="{href}"><div class="rel-title">{esc(m["title"])}</div>'
                    f'<p class="rel-desc">{esc(link["desc"])}</p></a></li>\n')
            s = insert_after(s, '<ul class="related-list">\n', item)
        else:
            match = re.search(r'Related reading</h2>\s*<ul>\n', s)
            if not match:
                sys.exit(f"FATAL: no related-links slot in {link['host']}")
            s = s[:match.end()] + f'        <li><a href="{href}">{esc(m["title"])}</a></li>\n' + s[match.end():]
        write(path, s)


PENDING_LI = re.compile(r"<!--pending-insight:([a-z0-9-]+) (<li>.*?</li>)-->", re.S)
PENDING_SPAN = re.compile(r'<span data-pending-insight="([a-z0-9-]+)">(.*?)</span>', re.S)
INSIGHT_LI = re.compile(r'<li><a href="/insights/([a-z0-9-]+)/">.*?</a></li>', re.S)
INSIGHT_A = re.compile(r'<a href="/insights/([a-z0-9-]+)/">(.*?)</a>', re.S)


def published(slug: str) -> bool:
    return (SITE / "insights" / slug / "index.html").exists()


def settle_links(path: Path) -> None:
    """Park links to insights not yet on the site; restore parked links whose target now exists.

    Queued articles often link to each other. Whichever publishes first would carry a dead link
    until its partner goes live, so a related-list item to an unpublished insight is kept as an
    HTML comment and an inline link becomes a plain-text span. Both are restored automatically
    when the target is registered.
    """
    s = read(path)
    original = s
    s = PENDING_LI.sub(lambda m: m.group(2) if published(m.group(1)) else m.group(0), s)
    s = PENDING_SPAN.sub(lambda m: f'<a href="/insights/{m.group(1)}/">{m.group(2)}</a>'
                         if published(m.group(1)) else m.group(0), s)
    s = INSIGHT_LI.sub(lambda m: m.group(0) if published(m.group(1))
                       else f"<!--pending-insight:{m.group(1)} {m.group(0)}-->", s)
    # Inline links outside comments only, so parked list items are left alone.
    parts = re.split(r"(<!--.*?-->)", s, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = INSIGHT_A.sub(lambda m: m.group(0) if published(m.group(1))
                                 else f'<span data-pending-insight="{m.group(1)}">{m.group(2)}</span>',
                                 parts[i])
    s = "".join(parts)
    if s != original:
        write(path, s)


def settle_all_links(slug: str) -> None:
    settle_links(SITE / "insights" / slug / "index.html")
    for page in (SITE / "insights").glob("*/index.html"):
        text = read(page)
        if f"pending-insight:{slug} " in text or f'data-pending-insight="{slug}"' in text:
            settle_links(page)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--date", help="publish date (YYYY-MM-DD); defaults to the manifest's publish_on")
    args = ap.parse_args()
    m = load_manifest(args.slug)
    date = args.date or m["publish_on"]
    dt.date.fromisoformat(date)
    redate_article(m, date)
    register_sitemap(m, date)
    register_archive(m, date)
    register_hub(m)
    register_og(m)
    register_reciprocal(m)
    settle_all_links(args.slug)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_insights_catalog.py")], check=True)
    print(f"registered {args.slug} for {date}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
