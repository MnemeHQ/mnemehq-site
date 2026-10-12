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


def card(slug: str, tag: str, *, link_attrs: str | None = None,
         href: str | None = None, tag_class: str = "card-tag") -> str:
    href = href or f"/insights/{slug}/"
    link_attrs = link_attrs or f'href="{href}" class="insight-card-link" data-published="2026-01-01"'
    return (
        f"<a {link_attrs}>"
        f'<div class="card-meta"><span class="{tag_class}">{tag}</span></div>'
        f"<h3>Title</h3></a>\n"
    )


CATALOG = "var TYPE_LABELS = {\n" + ",\n".join(
    f"    '{k.lower()}': '{v}'" for k, v in c.CANONICAL_TYPES.items()
) + "\n  };\n"


class SiteFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.site = Path(self.tmp.name)
        self.insights = self.site / "insights"
        (self.insights / "all").mkdir(parents=True)
        (self.insights / "topics" / "hub").mkdir(parents=True)
        self.catalog = self.site / "insights-catalog-v2.js"
        self.catalog.write_text(CATALOG, encoding="utf-8")

    def page(self, slug: str, body: str) -> None:
        (self.insights / slug).mkdir()
        (self.insights / slug / "index.html").write_text(body, encoding="utf-8")

    def surface(self, rel: str, body: str) -> None:
        path = self.site / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def errors(self) -> list[str]:
        return c.check(self.site, self.catalog)


class TestPagesAndCards(unittest.TestCase):
    def setUp(self) -> None:
        self.s = SiteFixture()
        self.addCleanup(self.s.tmp.cleanup)
        self.s.page("stanford-ai-index", article("Report Response"))

    def test_consistent_site_passes(self):
        self.s.surface("insights/all/index.html", card("stanford-ai-index", "Report Response"))
        self.s.surface("insights/topics/hub/index.html", card("stanford-ai-index", "Report Response"))
        self.s.surface("insights/index.html", card("stanford-ai-index", "Report Response"))
        self.assertEqual(self.s.errors(), [])

    def test_legacy_label_fails(self):
        self.s.page("legacy", article("Market Context"))
        self.assertTrue(any("not a canonical type" in e for e in self.s.errors()))

    def test_section_must_match_eyebrow(self):
        self.s.page("datadog-report", article("Report Response", section="Engineering"))
        self.assertTrue(any("does not match eyebrow" in e for e in self.s.errors()))

    def test_page_attribute_order_does_not_matter(self):
        self.s.page("reordered", '<meta content="Research" property="article:section">'
                                 '<span data-x="1" class="eyebrow-tag big">Research</span>')
        self.assertEqual(self.s.errors(), [])

    def test_archive_card_must_match_article(self):
        self.s.surface("insights/all/index.html", card("stanford-ai-index", "Analysis"))
        self.assertTrue(any("insights/all/index.html says 'Analysis'" in e for e in self.s.errors()))

    def test_homepage_card_is_checked(self):
        self.s.surface("insights/index.html", card("stanford-ai-index", "Analysis"))
        self.assertTrue(any("on insights/index.html" in e for e in self.s.errors()))

    def test_card_on_any_page_is_checked(self):
        self.s.surface("concepts/x/index.html", card("stanford-ai-index", "Analysis"))
        self.assertTrue(any("on concepts/x/index.html" in e for e in self.s.errors()))

    def test_reordered_card_attributes_are_read(self):
        attrs = 'class="insight-card-link" data-published="2026-01-01" href="/insights/stanford-ai-index/"'
        self.s.surface("insights/all/index.html", card("stanford-ai-index", "Analysis", link_attrs=attrs))
        self.assertTrue(any("says 'Analysis'" in e for e in self.s.errors()))

    def test_absolute_link_is_read(self):
        self.s.surface("insights/all/index.html", card(
            "stanford-ai-index", "Analysis", href="https://mnemehq.com/insights/stanford-ai-index/"))
        self.assertTrue(any("says 'Analysis'" in e for e in self.s.errors()))

    def test_extra_classes_are_read(self):
        attrs = 'href="/insights/stanford-ai-index/" class="insight-card-link featured"'
        self.s.surface("insights/all/index.html", card(
            "stanford-ai-index", "Analysis", link_attrs=attrs, tag_class="card-tag pill"))
        self.assertTrue(any("says 'Analysis'" in e for e in self.s.errors()))

    def test_card_without_readable_tag_fails(self):
        self.s.surface("insights/all/index.html", card(
            "stanford-ai-index", "Report Response", tag_class="card-label"))
        self.assertTrue(any("no readable card-tag" in e for e in self.s.errors()))

    def test_cards_to_non_article_pages_are_ignored(self):
        self.s.surface("insights/index.html", card("all", "Archive", href="/insights/all/"))
        self.assertEqual(self.s.errors(), [])

    def test_html_entities_are_compared_as_text(self):
        self.s.surface("insights/all/index.html", card("stanford-ai-index", "Report&#32;Response"))
        self.assertEqual(self.s.errors(), [])


class TestCatalog(unittest.TestCase):
    def setUp(self) -> None:
        self.s = SiteFixture()
        self.addCleanup(self.s.tmp.cleanup)

    def test_canonical_catalog_passes(self):
        self.assertEqual(c.catalog_errors(self.s.catalog), [])

    def test_single_quoted_legacy_entry_fails(self):
        self.s.catalog.write_text(
            CATALOG.replace("};", ",\n    'productivity': 'Research & reports'\n  };"), encoding="utf-8")
        self.assertTrue(c.catalog_errors(self.s.catalog))

    def test_double_quoted_legacy_entry_fails(self):
        self.s.catalog.write_text(
            CATALOG.replace("};", ',\n    "market context": "Analysis"\n  };'), encoding="utf-8")
        self.assertTrue(c.catalog_errors(self.s.catalog))

    def test_two_research_labels_share_one_public_type(self):
        self.assertEqual(c.CANONICAL_TYPES["Research"], c.CANONICAL_TYPES["Report Response"])
        self.assertEqual(len(set(c.CANONICAL_TYPES.values())), 6)


if __name__ == "__main__":
    unittest.main()
