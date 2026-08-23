#!/usr/bin/env python3
"""new_article.py - create an insight article from the canonical template.

Emits site/insights/<slug>/index.html from site/_templates/article.html,
composing the JSON-LD @graph (BreadcrumbList + TechArticle [+ FAQPage])
from structured arguments. The emitted page is already on the shared
base.css system; sync_shared.py remains a safety net, not a requirement.

Registration is still manual per PUBLISHING.md: sitemap entry, archive /
topic-hub card (scripts/sync_insights_catalog.py), OG image
(scripts/ensure_og_coverage.py + scripts/generate_og_images.py), and at
least one incoming internal link. This script prints that checklist.

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
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

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
    og_image = slug_url + "og.png"
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

    print(
        "\nRegistration checklist (PUBLISHING.md):\n"
        f"  [ ] sitemap.xml entry for {slug_url}\n"
        "  [ ] archive/topic-hub card -> python scripts/sync_insights_catalog.py\n"
        "      then verify with: python scripts/sync_insights_catalog.py --check\n"
        f"  [ ] OG image mapping -> python scripts/ensure_og_coverage.py\n"
        f"      then generate -> python scripts/generate_og_images.py\n"
        f"  [ ] >=1 incoming internal link from a hub or related article\n"
        f"  [ ] visible breadcrumb Home -> Insights -> {args.title[:40]}...\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
