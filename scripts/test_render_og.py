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


if __name__ == "__main__":
    unittest.main()
