#!/usr/bin/env python3
"""Regression tests for the OG house-voice lint."""
from __future__ import annotations

import unittest

import lint_og_voice as v


class TestVoice(unittest.TestCase):
    def test_flags_bottleneck(self):
        f = v.findings({"headline": "The review bottleneck", "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f))

    def test_flags_connective_em_dash(self):
        f = v.findings({"headline": "Enforced early — before the commit",
                        "voice_ok": None})
        self.assertTrue(any("em dash" in x for x in f))

    def test_escape_suppresses_a_finding(self):
        """A quoted external report title may legitimately contain the word."""
        f = v.findings({"headline": 'On "The Bottleneck Myth" report',
                        "voice_ok": ["quoted external title"]})
        self.assertEqual(f, [])

    def test_clean_copy_passes(self):
        self.assertEqual(v.findings({"headline": "Architectural Drift",
                                     "voice_ok": None}), [])

    def test_checks_alt_and_sup_too(self):
        f = v.findings({"headline": "Fine", "sup": "A bottleneck appears",
                        "voice_ok": None})
        self.assertTrue(f)

    def test_en_dash_and_hyphen_are_not_flagged(self):
        self.assertEqual(v.findings({"headline": "Multi-agent 2024–2026 work",
                                     "voice_ok": None}), [])


if __name__ == "__main__":
    unittest.main()
