#!/usr/bin/env python3
"""Regression tests for the static insights catalogue synchronizer."""

from __future__ import annotations

import json
import unittest

import sync_insights_catalog as sync


def card(slug: str, published: str, title: str) -> str:
    return f'''<a href="/insights/{slug}/" class="insight-card-link" data-published="{published}">
        <div class="insight-card">
          <div class="card-meta">
            <span class="card-tag">Analysis</span>
            <span class="card-dot"></span>
            <time class="card-date" datetime="{published}">Aug 20, 2026</time>
            <span class="card-dot"></span>
            <span class="card-read-time">7 min read</span>
          </div>
          <h3>{title}</h3>
          <p>Summary.</p>
          <div class="card-footer"><span class="read-pill">Read insight</span></div>
        </div>
      </a>'''


def homepage_fixture() -> str:
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Insights",
                "hasPart": [],
            }
        ],
    }
    return f'''<script type="application/ld+json">
{json.dumps(schema, indent=2)}
</script>
<div class="cards-section" id="featured">
  {card("featured", "2026-01-01", "Featured")}
</div>
<div class="cards-section" id="latest">
  <div class="cards-grid">
      {sync.LATEST_START_MARKER}
      {card("stale", "2025-01-01", "Stale")}
      {sync.LATEST_END_MARKER}
  </div>
</div>
<div class="cards-section" id="topics"></div>
<div class="cards-section" id="start-here">
  {card("start", "2026-01-01", "Start here")}
</div>
'''


class SynchronizeHomepageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = [
            ("newest", "2026-08-20"),
            ("tie-a", "2026-08-18"),
            ("tie-b", "2026-08-18"),
            ("third", "2026-08-17"),
            ("fourth", "2026-08-16"),
            ("fifth", "2026-08-15"),
            ("excluded", "2026-08-14"),
        ]
        self.dates = {
            f"/insights/{slug}/": published for slug, published in self.articles
        }
        self.archive = "\n".join(
            card(slug, published, slug) for slug, published in self.articles
        )

    def test_latest_cards_use_dates_and_archive_order_as_tie_breaker(self) -> None:
        latest = sync.newest_archive_cards(self.archive, self.dates)
        self.assertEqual(
            [item["href"] for item in latest],
            [
                "/insights/newest/",
                "/insights/tie-a/",
                "/insights/tie-b/",
                "/insights/third/",
                "/insights/fourth/",
                "/insights/fifth/",
            ],
        )

    def test_homepage_cards_and_schema_are_synchronized_and_idempotent(self) -> None:
        synchronized, latest_urls = sync.synchronized_homepage(
            homepage_fixture(),
            self.archive,
            self.dates,
        )
        latest_section = sync.section_source(synchronized, "latest", "topics")
        visible_latest = [
            entry["url"] for entry in sync.section_article_entries(latest_section)
        ]
        expected_latest = [f"https://mnemehq.com{url}" for url in latest_urls]
        self.assertEqual(visible_latest, expected_latest)

        schema_match = sync.JSON_LD_RE.search(synchronized)
        self.assertIsNotNone(schema_match)
        schema = json.loads(schema_match.group("body"))
        has_part = schema["@graph"][0]["hasPart"]
        self.assertEqual(
            [entry["url"] for entry in has_part],
            ["https://mnemehq.com/insights/featured/"]
            + expected_latest
            + ["https://mnemehq.com/insights/start/"],
        )

        second_pass, second_latest = sync.synchronized_homepage(
            synchronized,
            self.archive,
            self.dates,
        )
        self.assertEqual(second_latest, latest_urls)
        self.assertEqual(second_pass, synchronized)

    def test_homepage_requires_sync_markers(self) -> None:
        without_markers = homepage_fixture().replace(sync.LATEST_START_MARKER, "")
        with self.assertRaisesRegex(ValueError, "sync:latest:start"):
            sync.synchronized_homepage(without_markers, self.archive, self.dates)


if __name__ == "__main__":
    unittest.main()
