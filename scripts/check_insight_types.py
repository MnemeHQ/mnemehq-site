#!/usr/bin/env python3
"""
check_insight_types.py - one canonical content type per insight, everywhere.

Every insight article carries a content-type label in four places that must
agree:

  1. the visible eyebrow on the article       <span class="eyebrow-tag">
  2. the article's Open Graph section          <meta property="article:section">
  3. every card that links to it, on any page  <a class="insight-card-link">
                                                 ... <span class="card-tag">
  4. the archive catalogue's type filter       TYPE_LABELS in
     site/assets/js/insights-catalog-v2.js

The label must be one of CANONICAL_TYPES. Each label belongs to exactly one
of the six public content types shown in the archive filter. Research &
reports has two labels:

  Research         primarily interprets an academic paper, empirical study,
                   benchmark or experiment
  Report Response  primarily interprets or responds to a named industry
                   report, survey, whitepaper or decision brief

What this check does NOT do: it proves the label is consistent and
canonical. It cannot tell whether the label is editorially right for the
article. That stays a manual review (see the content-type rule in
docs/site/insight-publishing-contract.md).

Pages are read with an HTML parser, so attribute order, extra classes and
absolute https://mnemehq.com links do not hide a card. A card linking to an
article that carries no readable card-tag is itself an error.

Usage:
  python scripts/check_insight_types.py

Exit codes:  0 = consistent   1 = errors found
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
CATALOG_JS = SITE / "assets" / "js" / "insights-catalog-v2.js"

# Stored label -> public content type.
CANONICAL_TYPES: dict[str, str] = {
    "Analysis": "Analysis",
    "Research": "Research & reports",
    "Report Response": "Research & reports",
    "Guide": "Guides",
    "Concept": "Concepts & reference",
    "Perspective": "Perspective",
    "Comparison": "Product & comparison",
    "Integration": "Product & comparison",
}

INDEX_DIRS = {"all", "topics"}
ARTICLE_HREF_RE = re.compile(r"^(?:https?://(?:www\.)?mnemehq\.com)?/insights/([a-z0-9-]+)/?(?:[?#].*)?$")
JS_BLOCK_RE = re.compile(r"var TYPE_LABELS = \{(.*?)\};", re.S)
JS_ENTRY_RE = re.compile(r"""(['"])(.+?)\1\s*:\s*(['"])(.+?)\3""")


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _classes(attrs: dict[str, str | None]) -> set[str]:
    return set((attrs.get("class") or "").split())


class _ArticleParser(HTMLParser):
    """Collect article:section values and eyebrow-tag texts from one page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[str] = []
        self.eyebrows: list[str] = []
        self._eyebrow: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("property") == "article:section":
            self.sections.append(_norm(a.get("content") or ""))
        elif tag == "span" and "eyebrow-tag" in _classes(a):
            self._eyebrow = []

    def handle_endtag(self, tag):
        if tag == "span" and self._eyebrow is not None:
            self.eyebrows.append(_norm("".join(self._eyebrow)))
            self._eyebrow = None

    def handle_data(self, data):
        if self._eyebrow is not None:
            self._eyebrow.append(data)


class _CardParser(HTMLParser):
    """Collect (href, card-tag text or None) for every insight-card-link."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[tuple[str, str | None]] = []
        self._href: str | None = None
        self._depth = 0
        self._tag: list[str] | None = None
        self._tag_text: str | None = None
        self._in_tag = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._href is None:
            if tag == "a" and "insight-card-link" in _classes(a):
                self._href, self._depth, self._tag_text = a.get("href") or "", 1, None
            return
        if tag == "a":
            self._depth += 1
        elif tag == "span" and "card-tag" in _classes(a) and self._tag_text is None:
            self._tag, self._in_tag = [], True

    def handle_endtag(self, tag):
        if self._href is None:
            return
        if tag == "span" and self._in_tag:
            self._tag_text, self._in_tag = _norm("".join(self._tag or [])), False
        elif tag == "a":
            self._depth -= 1
            if self._depth == 0:
                self.cards.append((self._href, self._tag_text))
                self._href = None

    def handle_data(self, data):
        if self._in_tag and self._tag is not None:
            self._tag.append(data)


def article_labels(insights: Path) -> tuple[dict[str, str], list[str]]:
    """Return {slug: label} for every article, plus page-level errors."""
    labels: dict[str, str] = {}
    errors: list[str] = []
    for page in sorted(insights.glob("*/index.html")):
        slug = page.parent.name
        if slug in INDEX_DIRS:
            continue
        parser = _ArticleParser()
        parser.feed(page.read_text(encoding="utf-8"))
        sections, eyebrows = parser.sections, parser.eyebrows
        if len(sections) != 1:
            errors.append(f"{slug}: expected one article:section meta, found {len(sections)}")
        if len(eyebrows) != 1:
            errors.append(f"{slug}: expected one eyebrow-tag, found {len(eyebrows)}")
        if len(sections) != 1 or len(eyebrows) != 1:
            continue
        section, eyebrow = sections[0], eyebrows[0]
        if eyebrow not in CANONICAL_TYPES:
            errors.append(
                f"{slug}: eyebrow {eyebrow!r} is not a canonical type "
                f"(one of: {', '.join(CANONICAL_TYPES)})"
            )
        if section != eyebrow:
            errors.append(f"{slug}: article:section {section!r} does not match eyebrow {eyebrow!r}")
        labels[slug] = eyebrow
    return labels, errors


def card_errors(site: Path, labels: dict[str, str]) -> list[str]:
    """Check every insight card on every HTML page under ``site``."""
    errors: list[str] = []
    for page in sorted(site.rglob("*.html")):
        parser = _CardParser()
        parser.feed(page.read_text(encoding="utf-8"))
        where = page.relative_to(site).as_posix()
        for href, tag in parser.cards:
            match = ARTICLE_HREF_RE.match(href)
            slug = match.group(1) if match else None
            if slug not in labels:
                continue  # hubs, the archive itself, or unregistered: check_insights.py owns those
            if tag is None:
                errors.append(f"{slug}: card on {where} has no readable card-tag")
            elif tag != labels[slug]:
                errors.append(f"{slug}: card on {where} says {tag!r}, article says {labels[slug]!r}")
    return errors


def catalog_errors(catalog_js: Path) -> list[str]:
    if not catalog_js.is_file():
        return [f"catalogue script missing: {catalog_js.name}"]
    block = JS_BLOCK_RE.search(catalog_js.read_text(encoding="utf-8"))
    if not block:
        return [f"{catalog_js.name}: TYPE_LABELS not found"]
    found = {m.group(2): m.group(4) for m in JS_ENTRY_RE.finditer(block.group(1))}
    expected = {label.lower(): public for label, public in CANONICAL_TYPES.items()}
    if found != expected:
        return [
            f"{catalog_js.name}: TYPE_LABELS {found!r} does not match "
            f"CANONICAL_TYPES {expected!r}"
        ]
    return []


def check(site: Path = SITE, catalog_js: Path = CATALOG_JS) -> list[str]:
    labels, errors = article_labels(site / "insights")
    errors += card_errors(site, labels)
    errors += catalog_errors(catalog_js)
    return errors


def main() -> int:
    errors = check()
    if errors:
        print(f"FAIL  {len(errors)} content-type inconsistenc{'y' if len(errors) == 1 else 'ies'}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    labels, _ = article_labels(SITE / "insights")
    counts: dict[str, int] = {}
    for label in labels.values():
        public = CANONICAL_TYPES[label]
        counts[public] = counts.get(public, 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    print(
        f"OK  {len(labels)} insight articles carry one canonical content type ({summary}). "
        "Consistency only: whether each label fits its article is a manual editorial review."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
