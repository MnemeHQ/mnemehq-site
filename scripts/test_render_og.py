#!/usr/bin/env python3
"""Regression tests for the OG renderer."""
from __future__ import annotations

import unittest

import render_og as r


class TestFit(unittest.TestCase):
    def test_bands_match_the_spec(self):
        self.assertEqual(r.fit(["short"]), 94)                       # <=38
        self.assertEqual(r.fit(["x" * 38]), 94)
        self.assertEqual(r.fit(["x" * 39]), 78)                      # <=62
        self.assertEqual(r.fit(["x" * 62]), 78)
        self.assertEqual(r.fit(["x" * 63]), 70)                      # <=92
        self.assertEqual(r.fit(["x" * 92]), 70)
        self.assertEqual(r.fit(["x" * 93]), 61)

    def test_sizes_on_longest_line_not_total(self):
        """A deliberate break must not shrink the card."""
        one = r.fit(["The Software Factory Needs a Governance Layer"])
        two = r.fit(["The Software Factory Needs a", "Governance Layer"])
        self.assertGreater(two, one)

    def test_never_below_the_floor(self):
        self.assertGreaterEqual(r.fit(["x" * 500]), 30)


class TestBuildHtml(unittest.TestCase):
    def _rec(self, **kw):
        base = {"path": "insights/x/", "family": "editorial",
                "headline": "Architectural Drift", "lines": ["Architectural Drift"],
                "accent": "Drift", "sup": None, "rows": None,
                "tone": "neutral", "motif": "branch", "alt": "Architectural Drift",
                "variant": None, "subtitle": None}
        base.update(kw)
        return base

    def test_accent_phrase_becomes_italic_em(self):
        html = r.build_html(self._rec())
        self.assertIn("<em>Drift</em>", html)

    def test_lines_become_explicit_breaks(self):
        html = r.build_html(self._rec(
            headline="A B", lines=["A", "B"], accent=None))
        self.assertIn("<br>", html)

    def test_editorial_embeds_geometry(self):
        self.assertIn("data-motif=\"branch\"", r.build_html(self._rec()))

    def test_neutral_editorial_has_no_red(self):
        self.assertNotIn("#ff5c7a", r.build_html(self._rec()))

    def test_html_escapes_copy(self):
        html = r.build_html(self._rec(
            headline="A & B", lines=["A & B"], accent=None))
        self.assertIn("&amp;", html)

    def test_normal_editorial_still_renders_geometry_and_em(self):
        """Regression guard: hub handling must not affect article cards."""
        html = r.build_html(self._rec())
        self.assertIn("data-motif=\"branch\"", html)
        self.assertIn("<em>Drift</em>", html)


class TestHubVariant(unittest.TestCase):
    def _rec(self, **kw):
        base = {"path": "insights/all/", "family": "editorial",
                "headline": "All Insights", "lines": ["All Insights"],
                "accent": "Insights", "sup": None, "rows": None,
                "tone": "neutral", "motif": "branch", "alt": "All Insights",
                "variant": "hub", "subtitle": "Every essay, one place"}
        base.update(kw)
        return base

    def test_hub_renders_subtitle(self):
        html = r.build_html(self._rec())
        self.assertIn('<div class="hub-sub">Every essay, one place</div>', html)

    def test_hub_renders_no_geometry(self):
        html = r.build_html(self._rec())
        self.assertNotIn("data-motif", html)

    def test_hub_renders_no_em_even_with_accent(self):
        html = r.build_html(self._rec())
        self.assertNotIn("<em>", html)

    def test_hub_has_no_category_label(self):
        """Hub cards carry the identity alone -- the subtitle is the
        descriptor, so a category label in the top bar would duplicate it
        (e.g. "INSIGHT" in the top bar and "INSIGHTS" again as subtitle)."""
        self.assertEqual(r.label_for(self._rec()), "")

    def test_hub_concepts_path_also_has_no_category_label(self):
        self.assertEqual(
            r.label_for(self._rec(path="concepts/some-topic-hub/")), "")


class TestStructuredBuilders(unittest.TestCase):
    """Anti-regression: this is the test whose absence let 85 cards ship
    with literal {{token}} text on the card face (Gate A visual review).
    Every family, with a fully-populated record, must render with no
    leftover template tokens."""

    def _base(self, **kw):
        base = {"path": "x/", "family": "brand", "headline": "H", "lines": ["H"],
                "accent": None, "sup": "Some sup.", "rows": None, "boxes": None,
                "badge": None, "name": None, "chain": None,
                "tone": "neutral", "motif": "connected", "alt": "H",
                "variant": None, "subtitle": None}
        base.update(kw)
        return base

    def test_brand_has_no_leftover_tokens(self):
        html = r.build_html(self._base(family="brand"))
        self.assertNotIn("{{", html)

    def test_editorial_has_no_leftover_tokens(self):
        html = r.build_html(self._base(
            family="editorial", path="insights/x/", accent="Drift"))
        self.assertNotIn("{{", html)

    def test_proof_has_no_leftover_tokens(self):
        rows = [
            ["ADR-014", "Postgres is the record.", "held"],
            ["AGENT", "Add MongoDB.", "neutral"],
            ["BLOCKED", "Before the commit.", "denied"],
        ]
        html = r.build_html(self._base(family="proof", path="demo/x/", rows=rows))
        self.assertNotIn("{{", html)
        self.assertIn("ADR-014", html)
        self.assertIn("Postgres is the record.", html)
        self.assertIn("Before the commit.", html)

    def test_comparison_has_no_leftover_tokens(self):
        boxes = [
            {"label": "CURSOR RULES", "value": "Advisory",
             "verdict": "MAY BE IGNORED", "kind": "warn"},
            {"label": "MNEME", "value": "Enforced",
             "verdict": "CANNOT BE SKIPPED", "kind": "accent"},
        ]
        html = r.build_html(self._base(family="comparison", path="compare/x/", boxes=boxes))
        self.assertNotIn("{{", html)
        self.assertIn("CURSOR RULES", html)
        self.assertIn("CANNOT BE SKIPPED", html)

    def test_integration_has_no_leftover_tokens(self):
        chain = [{"text": "DECISION", "kind": "plain"},
                 {"text": "MNEME", "kind": "accent"},
                 {"text": "CLAUDE CODE", "kind": "plain"}]
        html = r.build_html(self._base(
            family="integration", path="integrations/x/",
            badge="NATIVE SUPPORT", name="Claude Code", chain=chain))
        self.assertNotIn("{{", html)
        self.assertIn("NATIVE SUPPORT", html)
        self.assertIn("Claude Code", html)

    def test_proof_missing_rows_falls_back_with_no_leftover_tokens(self):
        """Dev-only fallback: non-strict local preview must never leak a
        literal {{token}} even when the structured data is absent."""
        html = r.build_html(self._base(family="proof", path="demo/x/", rows=None))
        self.assertNotIn("{{", html)

    def test_comparison_missing_boxes_falls_back_with_no_leftover_tokens(self):
        html = r.build_html(self._base(family="comparison", path="compare/x/", boxes=None))
        self.assertNotIn("{{", html)

    def test_integration_missing_fields_falls_back_with_no_leftover_tokens(self):
        html = r.build_html(self._base(family="integration", path="integrations/x/"))
        self.assertNotIn("{{", html)

    def test_proof_row_kinds_map_to_distinct_accent_colors(self):
        rows = [["A", "1", "held"], ["B", "2", "neutral"], ["C", "3", "denied"]]
        html = r.build_html(self._base(family="proof", path="demo/x/", rows=rows))
        self.assertIn("var(--accent)", html)
        self.assertIn("var(--quiet)", html)
        self.assertIn("var(--error)", html)

    def test_comparison_copy_is_escaped(self):
        boxes = [
            {"label": "A & B", "value": "1", "verdict": "V", "kind": "warn"},
            {"label": "C", "value": "2", "verdict": "V", "kind": "accent"},
        ]
        html = r.build_html(self._base(family="comparison", path="compare/x/", boxes=boxes))
        self.assertIn("A &amp; B", html)

    def test_integration_copy_is_escaped(self):
        chain = [{"text": "A & B", "kind": "plain"}, {"text": "C", "kind": "accent"}]
        html = r.build_html(self._base(
            family="integration", path="integrations/x/",
            badge="B & B", name="N & N", chain=chain))
        self.assertIn("A &amp; B", html)
        self.assertIn("B &amp; B", html)
        self.assertIn("N &amp; N", html)


class TestLabelFor(unittest.TestCase):
    def test_normal_editorial_insight_gets_label(self):
        rec = {"family": "editorial", "path": "insights/rag-is-not-memory/",
               "variant": None}
        self.assertEqual(r.label_for(rec), "Insight")

    def test_normal_editorial_concept_gets_label(self):
        rec = {"family": "editorial", "path": "concepts/architectural-drift/",
               "variant": None}
        self.assertEqual(r.label_for(rec), "Concept")


if __name__ == "__main__":
    unittest.main()
