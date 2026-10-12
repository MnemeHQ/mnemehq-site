#!/usr/bin/env python3
"""Regression tests for the canonical insight content-type check."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_insight_types as c


def article(label: str, section: str | None = None) -> str:
    section = label if section is None else section
    return (
        f'<meta property="article:section" content="{section}" />\n'
        f'<div class="article-eyebrow"><span class="eyebrow-tag">{label}</span></div>\n'
    )


def card(slug: str, tag: str) -> str:
    return (
        f'<a href="/insights/{slug}/" class="insight-card-link" data-published="2026-01-01">'
        f'<div class="card-meta"><span class="card-tag">{tag}</span></div></a>\n'
    )


CATALOG = "var TYPE_LABELS = {\n" + ",\n".join(
    f"    '{k.lower()}': '{v}'" for k, v in c.CANONICAL_TYPES.items()
) + "\n  };\n"


class SiteFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.insights = self.root / "insights"
        (self.insights / "all").mkdir(parents=True)
        (self.insights / "topics" / "hub").mkdir(parents=True)
        self.catalog = self.root / "insights-catalog-v2.js"
        self.catalog.write_text(CATALOG, encoding="utf-8")

    def page(self, slug: str, body: str) -> None:
        (self.insights / slug).mkdir()
        (self.insights / slug / "index.html").write_text(body, encoding="utf-8")

    def surface(self, rel: str, body: str) -> None:
        (self.insights / rel).write_text(body, encoding="utf-8")

    def errors(self) -> list[str]:
        return c.check(self.insights, self.catalog)


class TestInsightTypes(unittest.TestCase):
    def setUp(self) -> None:
        self.site = SiteFixture()
        self.addCleanup(self.site.tmp.cleanup)

    def test_consistent_site_passes(self):
        self.site.page("stanford-ai-index", article("Report Response"))
        self.site.surface("all/index.html", card("stanford-ai-index", "Report Response"))
        self.site.surface("topics/hub/index.html", card("stanford-ai-index", "Report Response"))
        self.assertEqual(self.site.errors(), [])

    def test_legacy_label_fails(self):
        self.site.page("stanford-ai-index", article("Market Context"))
        self.site.surface("all/index.html", card("stanford-ai-index", "Market Context"))
        self.assertTrue(any("not a canonical type" in e for e in self.site.errors()))

    def test_section_must_match_eyebrow(self):
        self.site.page("datadog-report", article("Report Response", section="Engineering"))
        self.site.surface("all/index.html", card("datadog-report", "Report Response"))
        self.assertTrue(any("does not match eyebrow" in e for e in self.site.errors()))

    def test_archive_card_must_match_article(self):
        """The agent-formation case: archive said Research, the page said otherwise."""
        self.site.page("agent-formation", article("Analysis"))
        self.site.surface("all/index.html", card("agent-formation", "Research"))
        errors = self.site.errors()
        self.assertTrue(any("card on insights/all/index.html says 'Research'" in e for e in errors))

    def test_hub_card_must_match_article(self):
        self.site.page("how-agents-use-adrs", article("Guide"))
        self.site.surface("all/index.html", card("how-agents-use-adrs", "Guide"))
        self.site.surface("topics/hub/index.html", card("how-agents-use-adrs", "Concept"))
        self.assertTrue(any("topics/hub/index.html" in e for e in self.site.errors()))

    def test_html_entities_are_compared_as_text(self):
        self.site.page("report-response", article("Report Response"))
        self.site.surface("all/index.html", card("report-response", "Report&#32;Response"))
        self.assertEqual(self.site.errors(), [])

    def test_catalog_mapping_must_match(self):
        self.assertEqual(c.catalog_errors(self.site.catalog), [])
        # A legacy label creeping back into the catalogue is a mismatch.
        self.site.catalog.write_text(
            CATALOG.replace("};", ",\n    'productivity': 'Research & reports'\n  };"),
            encoding="utf-8",
        )
        self.assertTrue(c.catalog_errors(self.site.catalog))

    def test_two_research_labels_share_one_public_type(self):
        self.assertEqual(c.CANONICAL_TYPES["Research"], c.CANONICAL_TYPES["Report Response"])
        self.assertEqual(len(set(c.CANONICAL_TYPES.values())), 6)


if __name__ == "__main__":
    unittest.main()
