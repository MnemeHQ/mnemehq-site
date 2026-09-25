#!/usr/bin/env python3
"""Regression tests for the OG coverage gate."""
from __future__ import annotations

import unittest

import check_og_coverage as c
import og_manifest as m


class TestCoverage(unittest.TestCase):
    def test_flags_page_without_record(self):
        errs = c.audit(pages=["insights/a/"], manifest={}, advertised={})
        self.assertTrue(any("no manifest record" in e for e in errs))

    def test_flags_record_without_page(self):
        errs = c.audit(pages=[], manifest={"insights/ghost/": {"headline": "X"}},
                       advertised={})
        self.assertTrue(any("ghost" in e for e in errs))

    def test_flags_lines_headline_mismatch(self):
        errs = c.audit(
            pages=["insights/a/"],
            manifest={"insights/a/": {"headline": "A B C", "lines": ["A", "Z"]}},
            advertised={})
        self.assertTrue(any("rejoin" in e for e in errs))

    def test_flags_advertised_image_with_no_source(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X"}},
                       advertised={"insights/a/": "legacy/og.png"})
        self.assertTrue(any("not reproducible" in e for e in errs))

    def test_clean_manifest_passes(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X"}},
                       advertised={"insights/a/": "insights/a/og-v2.png"})
        self.assertEqual(errs, [])


class TestCardOverride(unittest.TestCase):
    def test_override_is_the_expected_image(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X", "card": "og-v3.png"}},
                       advertised={"insights/a/": "insights/a/og-v3.png"})
        self.assertEqual(errs, [])

    def test_stale_advertised_card_is_flagged(self):
        errs = c.audit(pages=["insights/a/"],
                       manifest={"insights/a/": {"headline": "X", "card": "og-v3.png"}},
                       advertised={"insights/a/": "insights/a/og-v2.png"})
        self.assertTrue(any("not reproducible" in e for e in errs))

if __name__ == "__main__":
    unittest.main()
