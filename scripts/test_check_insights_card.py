#!/usr/bin/env python3
"""Regression tests: check_insights honours the per-record OG card override."""
from __future__ import annotations

import unittest

import check_insights as ci


class TestExpectedCard(unittest.TestCase):
    def test_defaults_to_og_v2(self):
        self.assertEqual(ci.expected_card("a", {}), "og-v2.png")
        self.assertEqual(ci.expected_card("a", {"insights/a/": {"headline": "X"}}), "og-v2.png")

    def test_uses_manifest_override(self):
        manifest = {"insights/a/": {"headline": "X", "card": "og-v3.png"}}
        self.assertEqual(ci.expected_card("a", manifest), "og-v3.png")


if __name__ == "__main__":
    unittest.main()
