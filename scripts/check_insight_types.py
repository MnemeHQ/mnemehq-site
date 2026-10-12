#!/usr/bin/env python3
"""
check_insight_types.py - one canonical content type per insight, everywhere.

Every insight article carries a content-type label in four places that must
agree:

  1. the visible eyebrow on the article       <span class="eyebrow-tag">
  2. the article's Open Graph section          <meta property="article:section">
  3. every index card that links to it         <span class="card-tag"> on the
     archive (/insights/all/), the homepage (/insights/) and each topic hub
  4. the archive catalogue's type filter       TYPE_LABELS in
     site/assets/js/insights-catalog-v2.js

The label must be one of CANONICAL_TYPES. Each label belongs to exactly one
of the six public content types shown in the archive filter. Research &
reports has two labels:

  Research         primarily interprets an academic paper, empirical study,
                   benchmark or experiment
  Report Response  primarily interprets or responds to a named industry
                   report, survey, whitepaper or decision brief

Topic and collection are separate from content type and are not checked here.

Usage:
  python scripts/check_insight_types.py

Exit codes:  0 = consistent   1 = errors found
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
INSIGHTS = SITE / "insights"
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
SECTION_RE = re.compile(r'<meta property="article:section" content="([^"]*)"')
EYEBROW_RE = re.compile(r'<span class="eyebrow-tag">([^<]*)</span>')
CARD_RE = re.compile(
    r'<a href="/insights/([^/"]+)/" class="insight-card-link"'
    r'(?:(?!</a>).)*?<span class="card-tag">([^<]*)</span>',
    re.S,
)
JS_BLOCK_RE = re.compile(r"var TYPE_LABELS = \{(.*?)\};", re.S)
JS_ENTRY_RE = re.compile(r"'([^']+)'\s*:\s*'([^']+)'")


def _text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def index_surfaces(insights: Path) -> list[Path]:
    surfaces = [insights / "all" / "index.html", insights / "index.html"]
    surfaces += sorted((insights / "topics").glob("*/index.html"))
    return [p for p in surfaces if p.is_file()]


def article_labels(insights: Path) -> tuple[dict[str, str], list[str]]:
    """Return {slug: label} for every article, plus page-level errors."""
    labels: dict[str, str] = {}
    errors: list[str] = []
    for page in sorted(insights.glob("*/index.html")):
        slug = page.parent.name
        if slug in INDEX_DIRS:
            continue
        source = page.read_text(encoding="utf-8")
        sections = [_text(v) for v in SECTION_RE.findall(source)]
        eyebrows = [_text(v) for v in EYEBROW_RE.findall(source)]
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


def card_errors(insights: Path, labels: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for surface in index_surfaces(insights):
        where = surface.relative_to(insights.parent).as_posix()
        for slug, tag in CARD_RE.findall(surface.read_text(encoding="utf-8")):
            tag = _text(tag)
            expected = labels.get(slug)
            if expected is None:
                continue  # unregistered or missing article: check_insights.py owns that
            if tag != expected:
                errors.append(f"{slug}: card on {where} says {tag!r}, article says {expected!r}")
    return errors


def catalog_errors(catalog_js: Path) -> list[str]:
    if not catalog_js.is_file():
        return [f"catalogue script missing: {catalog_js.relative_to(REPO).as_posix()}"]
    block = JS_BLOCK_RE.search(catalog_js.read_text(encoding="utf-8"))
    if not block:
        return [f"{catalog_js.name}: TYPE_LABELS not found"]
    found = dict(JS_ENTRY_RE.findall(block.group(1)))
    expected = {label.lower(): public for label, public in CANONICAL_TYPES.items()}
    if found != expected:
        return [
            f"{catalog_js.name}: TYPE_LABELS {found!r} does not match "
            f"CANONICAL_TYPES {expected!r}"
        ]
    return []


def check(insights: Path = INSIGHTS, catalog_js: Path = CATALOG_JS) -> list[str]:
    labels, errors = article_labels(insights)
    errors += card_errors(insights, labels)
    errors += catalog_errors(catalog_js)
    return errors


def main() -> int:
    errors = check()
    if errors:
        print(f"FAIL  {len(errors)} content-type inconsistenc{'y' if len(errors) == 1 else 'ies'}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    labels, _ = article_labels(INSIGHTS)
    counts: dict[str, int] = {}
    for label in labels.values():
        public = CANONICAL_TYPES[label]
        counts[public] = counts.get(public, 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    print(f"OK  {len(labels)} insight articles carry one canonical content type ({summary}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
