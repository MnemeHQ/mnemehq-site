#!/usr/bin/env python3
"""new_article.py - create an insight article from the canonical template.

Emits site/insights/<slug>/index.html from templates/article.html,
composing the JSON-LD @graph (BreadcrumbList + TechArticle [+ FAQPage])
from structured arguments. The emitted page is already on the shared
base.css system; sync_shared.py remains a safety net, not a requirement.

With --register it also inserts the archive card (top of --archive-section),
the archive CollectionPage.hasPart entry, and the sitemap entry; each step is
skipped when the slug is already present. Run scripts/sync_insights_catalog.py
afterwards to derive the card date, archive count, and homepage latest set.
Still manual per PUBLISHING.md: the OG card record in site/og/cards.yaml
rendered via scripts/render_og.py, an optional topic-hub card, and reciprocal
internal links. This script prints that checklist.

Usage:
  python scripts/new_article.py \
    --slug my-article-slug \
    --title "Title Used Verbatim Across All Six Fields" \
    --description "150-160 char description with source + figure." \
    --date 2026-08-23 \
    --lede "One-paragraph standfirst." \
    --body-file body.html \
    [--section Engineering] [--eyebrow Concept] [--read-time "9 min read"] \
    [--faq faq.json] [--about-terms "term one","term two"] \
    [--register --card-summary "One-sentence archive card summary." \
     --archive-section latest-analysis [--card-tag "Report Response"]] \
    [--force]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
TEMPLATE = REPO / "templates" / "article.html"
FOUNDER_URL = "https://mnemehq.com/founder/"
ARCHIVE = SITE / "insights" / "all" / "index.html"
SITEMAP = SITE / "sitemap.xml"
HAS_PART_OPEN = '"hasPart": ['


def render_jsonld(slug_url: str, og_image: str, title: str, description: str,
                  date_iso: str, section: str, about_terms: list[str],
                  faq_items: list | None) -> str:
    graph = [
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home",
                 "item": "https://mnemehq.com/"},
                {"@type": "ListItem", "position": 2, "name": "Insights",
                 "item": "https://mnemehq.com/insights/"},
                {"@type": "ListItem", "position": 3, "name": title,
                 "item": slug_url},
            ],
        },
        {
            "@type": "TechArticle",
            "headline": title,
            "description": description,
            "url": slug_url,
            "datePublished": date_iso,
            "dateModified": date_iso,
            "author": {"@type": "Person", "name": "Theo Valmis", "url": FOUNDER_URL},
            "publisher": {"@type": "Organization", "name": "Mneme HQ",
                          "url": "https://mnemehq.com/",
                          "logo": {"@type": "ImageObject",
                                   "url": "https://mnemehq.com/logo-v3.png"}},
            "image": og_image,
            "mainEntityOfPage": slug_url,
        },
    ]
    if about_terms:
        graph[1]["about"] = about_terms
    if faq_items:
        graph.append({"@type": "FAQPage", "mainEntity": faq_items})
    payload = {"@context": "https://schema.org", "@graph": graph}
    # </script> inside any value would terminate the script element early;
    # escape '<' at the serialization level (valid JSON escape).
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(payload, indent=2, ensure_ascii=False).replace("<", "\\u003c")
        + "\n</script>"
    )


def archive_card(slug: str, title: str, tag: str, read_time: str, summary: str) -> str:
    # Date slot is filled by sync_insights_catalog.py from article:published_time.
    esc = lambda s: html.escape(s, quote=False)
    return (
        f'      <a href="/insights/{slug}/" class="insight-card-link">\n'
        '        <div class="insight-card">\n'
        '          <div class="card-meta">\n'
        f'            <span class="card-tag">{esc(tag)}</span>\n'
        '            <span class="card-dot"></span>\n'
        f'            <span class="card-read-time">{esc(read_time)}</span>\n'
        '          </div>\n'
        f'          <h3>{esc(title)}</h3>\n'
        f'          <p>{esc(summary)}</p>\n'
        '          <div class="card-footer">\n'
        '            <span class="read-pill">Read insight</span>\n'
        '          </div>\n'
        '        </div>\n'
        '      </a>\n'
    )


def register(slug: str, title: str, tag: str, read_time: str, summary: str,
             section: str, archive: Path = ARCHIVE, sitemap: Path = SITEMAP) -> list[str]:
    """Insert archive card, hasPart entry, and sitemap entry; return actions taken."""
    href = f"/insights/{slug}/"
    url = "https://mnemehq.com" + href
    done: list[str] = []

    src = archive.read_text(encoding="utf-8")
    if f'href="{href}"' in src:
        done.append("archive card already present")
    else:
        section_tag = f'<div class="cards-section" id="{section}">'
        if src.count(section_tag) != 1:
            raise ValueError(f"archive has no single cards-section #{section}")
        grid_tag = '<div class="cards-grid">'
        grid = src.index(grid_tag, src.index(section_tag)) + len(grid_tag)
        line_end = src.index("\n", grid) + 1
        src = src[:line_end] + archive_card(slug, title, tag, read_time, summary) + src[line_end:]
        done.append(f"archive card added to #{section}")

    if f'"url": "{url}"' in src:
        done.append("hasPart entry already present")
    else:
        if src.count(HAS_PART_OPEN) != 1:
            raise ValueError("archive must contain exactly one hasPart array")
        at = src.index(HAS_PART_OPEN) + len(HAS_PART_OPEN)
        entry = json.dumps({"@type": "Article", "name": title, "url": url},
                           ensure_ascii=False).replace("<", "\\u003c")
        src = src[:at] + f"\n      {entry}," + src[at:]
        done.append("hasPart entry added")
    archive.write_bytes(src.encode("utf-8"))

    xml = sitemap.read_text(encoding="utf-8")
    if f"<loc>{url}</loc>" in xml:
        done.append("sitemap entry already present")
    else:
        if xml.count("</urlset>") != 1:
            raise ValueError("sitemap must contain exactly one </urlset>")
        block = (
            "  <url>\n"
            f"    <loc>{url}</loc>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>\n"
        )
        xml = xml.replace("</urlset>", block + "</urlset>")
        sitemap.write_bytes(xml.encode("utf-8"))
        done.append("sitemap entry added")
    return done


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="e.g. my-article-slug")
    ap.add_argument("--title", required=True,
                    help="verbatim searchable title, used across all six fields")
    ap.add_argument("--description", required=True,
                    help="150-160 chars, leads with source + concrete figure")
    ap.add_argument("--lede", required=True, help="standfirst paragraph HTML/text")
    ap.add_argument("--date", required=True, help="ISO date, e.g. 2026-08-23")
    ap.add_argument("--body-file", required=True, type=Path,
                    help="HTML fragment: everything between </header> and the newsletter aside")
    ap.add_argument("--section", default="Engineering")
    ap.add_argument("--eyebrow", default="Concept", help="Concept | Guide | Analysis ...")
    ap.add_argument("--read-time", default=None, help='e.g. "7 min read"')
    ap.add_argument("--faq", type=Path, default=None,
                    help="JSON file of FAQPage mainEntity items")
    ap.add_argument("--about-terms", default="",
                    help="comma-separated TechArticle about terms")
    ap.add_argument("--register", action="store_true",
                    help="also insert the archive card, hasPart entry, and sitemap entry")
    ap.add_argument("--card-summary", default=None,
                    help="archive card summary sentence (required with --register)")
    ap.add_argument("--archive-section", default=None,
                    help="archive cards-section id, e.g. latest-analysis (required with --register)")
    ap.add_argument("--card-tag", default=None, help="archive card tag (default: --eyebrow)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    if args.register and not (args.card_summary and args.archive_section):
        ap.error("--register requires --card-summary and --archive-section")

    if not TEMPLATE.exists():
        print(f"FATAL: template missing: {TEMPLATE}", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        print(f"FATAL: slug must be kebab-case: {args.slug!r}", file=sys.stderr)
        return 1
    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"FATAL: --date must be ISO: {args.date!r}", file=sys.stderr)
        return 1
    out_dir = SITE / "insights" / args.slug
    out_file = out_dir / "index.html"
    if out_file.exists() and not args.force:
        print(f"FATAL: {out_file} exists (use --force to overwrite)", file=sys.stderr)
        return 1
    if not args.body_file.exists():
        print(f"FATAL: body file missing: {args.body_file}", file=sys.stderr)
        return 1
    faq_data = None
    if args.faq:
        try:
            faq_data = json.loads(args.faq.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"FATAL: bad FAQ JSON ({args.faq}): {e}", file=sys.stderr)
            return 1

    words = len(re.sub(r"<[^>]+>", " ", args.body_file.read_text(encoding="utf-8")).split())
    read_time = args.read_time or f"{max(1, round(words / 220))} min read"
    date_iso = args.date
    date_human = dt.date.fromisoformat(date_iso).strftime("%B %Y")
    slug_url = f"https://mnemehq.com/insights/{args.slug}/"
    og_image = slug_url + "og-v2.png"
    about_terms = [t.strip() for t in args.about_terms.split(",") if t.strip()]

    html_text = TEMPLATE.read_text(encoding="utf-8")
    # Plain-text fields are HTML-escaped for attribute/text contexts; pass
    # entities via the body/lede fragments if you need markup.
    esc = lambda s: html.escape(s, quote=True)
    replacements = {
        "{{TITLE}}": esc(args.title),
        "{{DESCRIPTION}}": esc(args.description),
        "{{SLUG_URL}}": slug_url,
        "{{OG_IMAGE_URL}}": og_image,
        "{{OG_IMAGE_ALT}}": esc(args.title),
        "{{PUB_TIMESTAMP}}": date_iso + "T00:00:00Z",
        "{{PUB_DATE_ISO}}": date_iso,
        "{{PUB_DATE_HUMAN}}": date_human,
        "{{SECTION}}": esc(args.section),
        "{{EYEBROW_TAG}}": esc(args.eyebrow),
        "{{READ_TIME}}": esc(read_time),
        "{{LEDE}}": args.lede,
        "{{JSON_LD_BLOCK}}": render_jsonld(
            slug_url, og_image, args.title, args.description,
            date_iso, args.section, about_terms, faq_data),
        "{{BODY_CONTENT}}": args.body_file.read_text(encoding="utf-8").strip(),
    }
    for token, value in replacements.items():
        assert token in html_text, f"template lost token {token}"
        html_text = html_text.replace(token, value)

    leftover = re.findall(r"\{\{[A-Z_]+\}\}", html_text)
    if leftover:
        print(f"FATAL: unresolved tokens after render: {leftover}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(html_text.encode("utf-8"))
    print(f"wrote {out_file} ({len(html_text)} bytes, ~{words} words)")

    registered = False
    if args.register:
        try:
            for action in register(args.slug, args.title, args.card_tag or args.eyebrow,
                                   read_time, args.card_summary, args.archive_section):
                print(f"register: {action}")
            registered = True
        except (OSError, ValueError) as e:
            print(f"FATAL: registration failed: {e}", file=sys.stderr)
            return 1
    tick = "x" if registered else " "

    print(
        "\nRegistration checklist (PUBLISHING.md):\n"
        f"  [{tick}] sitemap.xml entry for {slug_url}\n"
        f"  [{tick}] archive card + hasPart entry (--register)\n"
        "  [ ] sync dates/count/homepage -> python scripts/sync_insights_catalog.py\n"
        "      then verify with: python scripts/sync_insights_catalog.py --check\n"
        "  [ ] optional topic-hub card under site/insights/topics/<hub>/\n"
        f"  [ ] add a record to site/og/cards.yaml\n"
        f"      then render -> python scripts/render_og.py --strict --out site\n"
        f"  [ ] >=1 incoming internal link from a hub or related article\n"
        f"  [ ] visible breadcrumb Home -> Insights -> {args.title[:40]}...\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
