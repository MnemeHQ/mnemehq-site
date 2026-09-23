#!/usr/bin/env python3
"""Regression tests for the OG metadata sync."""
from __future__ import annotations

import unittest

import sync_og_meta as s

HEAD = ('<head>\n'
        '<meta property="og:image" content="https://mnemehq.com/insights/a/og.png" />\n'
        '<meta name="twitter:image" content="https://mnemehq.com/insights/a/og.png" />\n'
        '</head>')


class TestRewrite(unittest.TestCase):
    def test_repoints_to_og_v2(self):
        out = s.rewrite(HEAD, "insights/a/", "Alt text")
        self.assertIn("https://mnemehq.com/insights/a/og-v2.png", out)
        self.assertNotIn("/og.png", out)

    def test_adds_all_four_tags(self):
        out = s.rewrite(HEAD, "insights/a/", "Alt text")
        for tag in ('og:image:width" content="1200',
                    'og:image:height" content="630',
                    'og:image:alt" content="Alt text',
                    'twitter:image:alt" content="Alt text'):
            self.assertIn(tag, out)

    def test_is_idempotent(self):
        once = s.rewrite(HEAD, "insights/a/", "Alt text")
        twice = s.rewrite(once, "insights/a/", "Alt text")
        self.assertEqual(once, twice)

    def test_escapes_alt_text(self):
        out = s.rewrite(HEAD, "insights/a/", 'He said "no" & left')
        self.assertIn("&quot;", out)
        self.assertNotIn('content="He said "no"', out)

    def test_leaves_other_markup_untouched(self):
        src = HEAD.replace("</head>", '<title>Keep me</title>\n</head>')
        self.assertIn("<title>Keep me</title>", s.rewrite(src, "insights/a/", "A"))


if __name__ == "__main__":
    unittest.main()
