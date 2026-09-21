#!/usr/bin/env python3
"""Regression tests for Editorial card geometry."""
from __future__ import annotations

import re
import unittest

import og_geometry as g
import og_manifest as m

SAGE, RED = "#b5cc7a", "#ff5c7a"


class TestGeometry(unittest.TestCase):
    def test_every_motif_renders_svg(self):
        for motif in m.MOTIFS:
            svg = g.render("any-slug", motif)
            self.assertTrue(svg.startswith("<svg"), motif)
            self.assertIn("</svg>", svg)

    def test_unknown_motif_raises(self):
        with self.assertRaises(ValueError):
            g.render("s", "spiral")

    def test_neutral_tone_never_emits_red(self):
        """The single most important rule: a governance-layer card must not
        assert that something was blocked."""
        for motif in m.MOTIFS:
            self.assertNotIn(RED, g.render("slug", motif, tone="neutral"), motif)

    def test_failure_tone_emits_red(self):
        for motif in m.MOTIFS:
            self.assertIn(RED, g.render("slug", motif, tone="failure"), motif)

    def test_sage_present_in_neutral(self):
        for motif in m.MOTIFS:
            self.assertIn(SAGE, g.render("slug", motif, tone="neutral"), motif)

    def test_no_lime_anywhere(self):
        for motif in m.MOTIFS:
            for tone in ("neutral", "failure"):
                self.assertNotIn("#c8f060", g.render("s", motif, tone))

    def test_deterministic_for_same_slug(self):
        self.assertEqual(g.render("abc", "connected"), g.render("abc", "connected"))

    def test_hash_varies_geometry_within_a_motif(self):
        """Cards sharing a motif must still differ."""
        a = g.render("alpha-slug", "connected")
        b = g.render("beta-slug", "connected")
        self.assertNotEqual(a, b)

    def test_declares_its_motif(self):
        self.assertIn('data-motif="stack"', g.render("s", "stack"))

    def test_respects_size(self):
        svg = g.render("s", "connected", size=400)
        self.assertIn('width="400"', svg)


if __name__ == "__main__":
    unittest.main()
