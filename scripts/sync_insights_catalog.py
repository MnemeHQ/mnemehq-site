#!/usr/bin/env python3
"""Synchronize archive-card metadata with canonical insight article data.

The full insights archive remains authored as static HTML so it satisfies the
publishing validator and provides a complete no-JavaScript fallback. The
catalogue enhancement uses ``data-published`` on each archive card for
deterministic sorting, while a static ``<time>`` element exposes the same date
to users and crawlers without JavaScript. This script keeps both derived date
values and the visible catalogue count in sync with the article collection.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSIGHTS_DIR = ROOT / "site" / "insights"
ARCHIVE_PATH = INSIGHTS_DIR / "all" / "index.html"

CARD_RE = re.compile(
    r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
CARD_META_RE = re.compile(
    r'(?P<open><div\s+class="card-meta">)(?P<content>.*?)(?P<close></div>)',
    re.IGNORECASE | re.DOTALL,
)
STATIC_TIME_RE = re.compile(
    r'<time\s+class="card-date"\s+datetime=(["\'])(?P<value>.*?)\1>.*?</time>',
    re.IGNORECASE | re.DOTALL,
)
READ_TIME_SLOT_RE = re.compile(
    r'(?P<dot><span\s+class="card-dot"></span>)(?P<space>\s*)'
    r'(?P<read><span\s+class="card-read-time">)',
    re.IGNORECASE,
)
ATTRIBUTE_RE_TEMPLATE = r"\b{attribute}\s*=\s*([\"'])(?P<value>.*?)\1"
PUBLISHED_RE = re.compile(
    r"<meta\s+property=([\"'])article:published_time\1\s+content=([\"'])(?P<value>.*?)\2\s*/?>",
    re.IGNORECASE,
)
CATALOG_COUNT_RE = re.compile(
    r'(?P<open><p\s+class="catalog-count">)\d+(?P<close>\s+articles</p>)',
    re.IGNORECASE,
)


def attribute_value(attributes: str, name: str) -> str | None:
    match = re.search(
        ATTRIBUTE_RE_TEMPLATE.format(attribute=re.escape(name)),
        attributes,
        re.IGNORECASE,
    )
    return match.group("value") if match else None


def article_publication_dates() -> dict[str, str]:
    dates: dict[str, str] = {}
    errors: list[str] = []

    for directory in sorted(INSIGHTS_DIR.iterdir()):
        if not directory.is_dir() or directory.name in {"all", "topics"}:
            continue

        article_path = directory / "index.html"
        if not article_path.exists():
            continue

        source = article_path.read_text(encoding="utf-8")
        match = PUBLISHED_RE.search(source)
        if not match:
            errors.append(f"{article_path.relative_to(ROOT)}: missing article:published_time")
            continue

        published = match.group("value")[:10]
        try:
            date.fromisoformat(published)
        except ValueError:
            errors.append(
                f"{article_path.relative_to(ROOT)}: invalid article:published_time {published!r}"
            )
            continue

        dates[f"/insights/{directory.name}/"] = published

    if errors:
        raise ValueError("\n".join(errors))

    return dates


def display_date(value: str) -> str:
    published = date.fromisoformat(value)
    month = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )[published.month - 1]
    return f"{month} {published.day}, {published.year}"


def synchronized_catalogue_count(source: str, article_count: int) -> str:
    matches = list(CATALOG_COUNT_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError(
            "archive must contain exactly one <p class=\"catalog-count\"> element"
        )

    return CATALOG_COUNT_RE.sub(
        rf"\g<open>{article_count}\g<close>",
        source,
        count=1,
    )


def synchronized_archive(
    source: str,
    publication_dates: dict[str, str],
) -> tuple[str, set[str], set[str]]:
    synchronized_urls: set[str] = set()
    static_time_urls: set[str] = set()
    errors: list[str] = []

    def replace_card(match: re.Match[str]) -> str:
        attributes = match.group("attrs")
        body = match.group("body")
        classes = (attribute_value(attributes, "class") or "").split()
        href = attribute_value(attributes, "href")

        if "insight-card-link" not in classes or href not in publication_dates:
            return match.group(0)

        synchronized_urls.add(href)
        published = publication_dates[href]
        existing = re.search(
            ATTRIBUTE_RE_TEMPLATE.format(attribute="data-published"),
            attributes,
            re.IGNORECASE,
        )

        if existing:
            start, end = existing.span("value")
            attributes = attributes[:start] + published + attributes[end:]
        else:
            attributes = attributes.rstrip() + f' data-published="{published}"'

        meta = CARD_META_RE.search(body)
        if not meta:
            errors.append(f"{href}: missing card-meta block")
            return f"<a{attributes}>{body}</a>"

        time_html = (
            f'<time class="card-date" datetime="{published}">'
            f"{display_date(published)}</time>"
        )
        meta_content = meta.group("content")

        if STATIC_TIME_RE.search(meta_content):
            meta_content = STATIC_TIME_RE.sub(time_html, meta_content, count=1)
        elif READ_TIME_SLOT_RE.search(meta_content):
            def insert_time(slot: re.Match[str]) -> str:
                space = slot.group("space")
                return (
                    slot.group("dot")
                    + space
                    + time_html
                    + space
                    + '<span class="card-dot"></span>'
                    + space
                    + slot.group("read")
                )

            meta_content = READ_TIME_SLOT_RE.sub(insert_time, meta_content, count=1)
        else:
            errors.append(f"{href}: card-meta missing card-read-time date slot")
            return f"<a{attributes}>{body}</a>"

        updated_meta = meta.group("open") + meta_content + meta.group("close")
        body = body[: meta.start()] + updated_meta + body[meta.end() :]
        static_time_urls.add(href)
        return f"<a{attributes}>{body}</a>"

    synchronized = CARD_RE.sub(replace_card, source)
    if errors:
        raise ValueError("\n".join(errors))

    return synchronized, synchronized_urls, static_time_urls


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the archive is out of sync instead of rewriting it.",
    )
    args = parser.parse_args()

    try:
        dates = article_publication_dates()
        source_bytes = ARCHIVE_PATH.read_bytes()
        source = source_bytes.decode("utf-8")
        synchronized, synchronized_urls, static_time_urls = synchronized_archive(source, dates)
        synchronized = synchronized_catalogue_count(synchronized, len(dates))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    missing_cards = sorted(set(dates) - synchronized_urls)
    if missing_cards:
        print("ERROR: article pages missing archive catalogue cards:", file=sys.stderr)
        for url in missing_cards:
            print(f"  - {url}", file=sys.stderr)
        return 1

    missing_static_times = sorted(set(dates) - static_time_urls)
    if missing_static_times:
        print("ERROR: archive cards missing static publication dates:", file=sys.stderr)
        for url in missing_static_times:
            print(f"  - {url}", file=sys.stderr)
        return 1

    # Work from raw decoded bytes above so the archive's existing CRLF layout
    # (including any legacy mixed-newline sequence) stays byte-for-byte stable.
    synchronized_bytes = synchronized.encode("utf-8")

    if synchronized_bytes == source_bytes:
        print(f"Insights catalogue metadata is in sync ({len(synchronized_urls)} articles).")
        return 0

    if args.check:
        print(
            "ERROR: insights catalogue metadata is out of sync. "
            "Run: python scripts/sync_insights_catalog.py",
            file=sys.stderr,
        )
        return 1

    ARCHIVE_PATH.write_bytes(synchronized_bytes)
    print(f"Updated insights catalogue metadata ({len(synchronized_urls)} articles).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
