#!/usr/bin/env python3
"""Structural tests for the five OG family templates."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

TPL = Path(__file__).resolve().parent.parent / "templates" / "og"
FAMILIES = ("brand", "proof", "integration", "editorial", "comparison")
LIME = ("#c8f060", "#a8d040", "#a9d342", "200,240,96", "200, 240, 96")


class TestTemplates(unittest.TestCase):
    def test_all_families_exist(self):
        for f in FAMILIES:
            self.assertTrue((TPL / f"{f}.html").is_file(), f)
        self.assertTrue((TPL / "_base.css").is_file())

    def _all_text(self):
        return "\n".join((TPL / n).read_text(encoding="utf-8")
                         for n in [f"{f}.html" for f in FAMILIES] + ["_base.css"])

    def test_no_type_below_30px(self):
        for size in re.findall(r"font-size:\s*(\d+)px", self._all_text()):
            self.assertGreaterEqual(int(size), 30, f"{size}px is below the 30px floor")

    def test_no_lime(self):
        text = self._all_text()
        for token in LIME:
            self.assertNotIn(token, text, token)

    def test_no_google_fonts(self):
        self.assertNotIn("fonts.googleapis.com", self._all_text())

    def test_fonts_are_local_woff2(self):
        css = (TPL / "_base.css").read_text(encoding="utf-8")
        self.assertIn("assets/fonts/", css)
        self.assertIn(".woff2", css)

    def test_identity_is_mneme_hq(self):
        for f in FAMILIES:
            html = (TPL / f"{f}.html").read_text(encoding="utf-8")
            if "Mneme" in html:
                self.assertIn("Mneme HQ", html, f)

    def test_no_printed_url(self):
        self.assertNotIn("mnemehq.com/", self._all_text())

    def test_brand_has_no_category_label(self):
        """Brand cards carry the identity alone."""
        self.assertNotIn("{{family_label}}",
                         (TPL / "brand.html").read_text(encoding="utf-8"))

    def test_editorial_has_geometry_and_no_supporting_copy(self):
        html = (TPL / "editorial.html").read_text(encoding="utf-8")
        self.assertIn("{{geometry}}", html)
        self.assertNotIn("{{sup}}", html)


if __name__ == "__main__":
    unittest.main()
