#!/usr/bin/env python3
"""Synchronize insight catalogue metadata and the curated homepage latest set.

The full insights archive remains authored as static HTML so it satisfies the
publishing validator and provides a complete no-JavaScript fallback. The
catalogue enhancement uses ``data-published`` on each archive card for
deterministic sorting, while a static ``<time>`` element exposes the same date
to users and crawlers without JavaScript. The six newest archive cards are also
copied into the curated homepage and its ``CollectionPage.hasPart`` schema.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSIGHTS_DIR = ROOT / "site" / "insights"
ARCHIVE_PATH = INSIGHTS_DIR / "all" / "index.html"
HOMEPAGE_PATH = INSIGHTS_DIR / "index.html"
HOMEPAGE_LATEST_LIMIT = 6
LATEST_START_MARKER = "<!-- sync:latest:start -->"
LATEST_END_MARKER = "<!-- sync:latest:end -->"

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
H3_RE = re.compile(r"<h3\b[^>]*>(?P<title>.*?)</h3>", re.IGNORECASE | re.DOTALL)
HAS_PART_RE = re.compile(
    r'(?P<open>"hasPart"\s*:\s*\[)(?P<body>.*?)(?P<close>\])',
    re.DOTALL,
)
JSON_LD_RE = re.compile(
    r'<script\s+type="application/ld\+json">(?P<body>.*?)</script>',
    re.IGNORECASE | re.DOTALL,
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


def newline_for(source: str) -> str:
    return "\r\n" if "\r\n" in source else "\n"


def card_title(body: str, href: str) -> str:
    match = H3_RE.search(body)
    if not match:
        raise ValueError(f"{href}: insight card is missing an <h3> title")
    without_tags = re.sub(r"<[^>]+>", "", match.group("title"))
    return " ".join(html.unescape(without_tags).split())


def archive_cards(
    source: str,
    publication_dates: dict[str, str],
) -> list[dict[str, str | int]]:
    cards: list[dict[str, str | int]] = []
    seen: set[str] = set()

    for source_index, match in enumerate(CARD_RE.finditer(source)):
        attributes = match.group("attrs")
        classes = (attribute_value(attributes, "class") or "").split()
        href = attribute_value(attributes, "href")
        if "insight-card-link" not in classes or href not in publication_dates:
            continue
        if href in seen:
            raise ValueError(f"archive contains duplicate insight card: {href}")
        seen.add(href)
        cards.append(
            {
                "href": href,
                "published": publication_dates[href],
                "title": card_title(match.group("body"), href),
                "markup": match.group(0),
                "source_index": source_index,
            }
        )

    return cards


def newest_archive_cards(
    source: str,
    publication_dates: dict[str, str],
    limit: int = HOMEPAGE_LATEST_LIMIT,
) -> list[dict[str, str | int]]:
    cards = archive_cards(source, publication_dates)
    if len(cards) < limit:
        raise ValueError(
            f"archive contains {len(cards)} insight cards; need at least {limit} "
            "to populate the homepage latest section"
        )

    return sorted(
        cards,
        key=lambda card: (
            -date.fromisoformat(str(card["published"])).toordinal(),
            int(card["source_index"]),
        ),
    )[:limit]


def replace_latest_cards(
    source: str,
    cards: list[dict[str, str | int]],
) -> str:
    if source.count(LATEST_START_MARKER) != 1 or source.count(LATEST_END_MARKER) != 1:
        raise ValueError(
            "homepage must contain exactly one sync:latest:start marker and one "
            "sync:latest:end marker"
        )

    start = source.index(LATEST_START_MARKER) + len(LATEST_START_MARKER)
    end = source.index(LATEST_END_MARKER, start)
    newline = newline_for(source)
    card_markup = (newline * 2).join(
        "      " + str(card["markup"]) for card in cards
    )
    replacement = newline + card_markup + newline + "      "
    return source[:start] + replacement + source[end:]


def section_source(source: str, section_id: str, next_section_id: str | None) -> str:
    start_token = f'<div class="cards-section" id="{section_id}">'
    try:
        start = source.index(start_token)
    except ValueError as exc:
        raise ValueError(f"homepage is missing cards section #{section_id}") from exc

    if next_section_id is None:
        return source[start:]

    next_token = f'<div class="cards-section" id="{next_section_id}">'
    try:
        end = source.index(next_token, start + len(start_token))
    except ValueError as exc:
        raise ValueError(f"homepage is missing cards section #{next_section_id}") from exc
    return source[start:end]


def section_article_entries(source: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for match in CARD_RE.finditer(source):
        attributes = match.group("attrs")
        classes = (attribute_value(attributes, "class") or "").split()
        href = attribute_value(attributes, "href")
        if (
            "insight-card-link" not in classes
            or href is None
            or not href.startswith("/insights/")
            or href.startswith("/insights/topics/")
            or href == "/insights/all/"
        ):
            continue
        entries.append(
            {
                "@type": "Article",
                "name": card_title(match.group("body"), href),
                "url": f"https://mnemehq.com{href}",
            }
        )
    return entries


def synchronized_homepage_schema(source: str) -> tuple[str, list[dict[str, str]]]:
    sections = (
        section_source(source, "featured", "latest"),
        section_source(source, "latest", "topics"),
        section_source(source, "start-here", None),
    )
    entries = [entry for section in sections for entry in section_article_entries(section)]
    urls = [entry["url"] for entry in entries]
    if len(urls) != len(set(urls)):
        raise ValueError("homepage curated article sections contain duplicate card URLs")

    matches = list(HAS_PART_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError("homepage must contain exactly one CollectionPage hasPart array")

    newline = newline_for(source)
    entry_lines = []
    for index, entry in enumerate(entries):
        suffix = "," if index < len(entries) - 1 else ""
        entry_lines.append(
            "          "
            + json.dumps(entry, ensure_ascii=False, separators=(", ", ": "))
            + suffix
        )
    body = newline + newline.join(entry_lines) + newline + "        "
    match = matches[0]
    synchronized = source[: match.start("body")] + body + source[match.end("body") :]

    collection_parts: list[str] | None = None
    for block in JSON_LD_RE.finditer(synchronized):
        try:
            data = json.loads(block.group("body"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"homepage JSON-LD is invalid after synchronization: {exc}") from exc
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "CollectionPage":
                collection_parts = [
                    part.get("url")
                    for part in node.get("hasPart", [])
                    if isinstance(part, dict)
                ]

    if collection_parts != urls:
        raise ValueError("homepage CollectionPage.hasPart does not match visible curated cards")

    return synchronized, entries


def synchronized_homepage(
    source: str,
    archive_source: str,
    publication_dates: dict[str, str],
) -> tuple[str, list[str]]:
    latest = newest_archive_cards(archive_source, publication_dates)
    synchronized = replace_latest_cards(source, latest)
    synchronized, _ = synchronized_homepage_schema(synchronized)
    latest_urls = [str(card["href"]) for card in latest]
    return synchronized, latest_urls


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the archive or homepage is out of sync instead of rewriting it.",
    )
    args = parser.parse_args()

    try:
        dates = article_publication_dates()
        source_bytes = ARCHIVE_PATH.read_bytes()
        source = source_bytes.decode("utf-8")
        synchronized, synchronized_urls, static_time_urls = synchronized_archive(source, dates)
        synchronized = synchronized_catalogue_count(synchronized, len(dates))
        homepage_bytes = HOMEPAGE_PATH.read_bytes()
        homepage_source = homepage_bytes.decode("utf-8")
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

    try:
        synchronized_home, latest_urls = synchronized_homepage(
            homepage_source,
            synchronized,
            dates,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Work from raw decoded bytes above so the archive's existing CRLF layout
    # (including any legacy mixed-newline sequence) stays byte-for-byte stable.
    synchronized_bytes = synchronized.encode("utf-8")
    synchronized_home_bytes = synchronized_home.encode("utf-8")

    archive_changed = synchronized_bytes != source_bytes
    homepage_changed = synchronized_home_bytes != homepage_bytes

    if not archive_changed and not homepage_changed:
        print(
            "Insights catalogue metadata is in sync "
            f"({len(synchronized_urls)} articles; {len(latest_urls)} homepage latest)."
        )
        return 0

    if args.check:
        print(
            "ERROR: insights archive or homepage catalogue is out of sync. "
            "Run: python scripts/sync_insights_catalog.py",
            file=sys.stderr,
        )
        return 1

    updated_paths: list[str] = []
    if archive_changed:
        ARCHIVE_PATH.write_bytes(synchronized_bytes)
        updated_paths.append(str(ARCHIVE_PATH.relative_to(ROOT)))
    if homepage_changed:
        HOMEPAGE_PATH.write_bytes(synchronized_home_bytes)
        updated_paths.append(str(HOMEPAGE_PATH.relative_to(ROOT)))
    print(
        "Updated insights catalogue metadata "
        f"({len(synchronized_urls)} articles; {len(latest_urls)} homepage latest): "
        + ", ".join(updated_paths)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
