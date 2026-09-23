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


class TestStructuredFields(unittest.TestCase):
    """Anti-regression: rows/boxes/chain render copy directly on the card
    face, so the lint must walk into them -- one test per container proves
    each is actually inspected, not just that findings() returns a list."""

    def test_flags_bottleneck_inside_a_rows_triple(self):
        f = v.findings({"rows": [["LABEL", "A bottleneck forms.", "neutral"]],
                        "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f), f)

    def test_flags_em_dash_inside_a_boxes_entry(self):
        f = v.findings({"boxes": [
            {"label": "A", "value": "1", "verdict": "Blocked — always", "kind": "warn"},
            {"label": "B", "value": "2", "verdict": "V", "kind": "accent"}],
            "voice_ok": None})
        self.assertTrue(any("em dash" in x for x in f), f)

    def test_flags_bottleneck_inside_a_chain_pill(self):
        f = v.findings({"chain": [{"text": "The bottleneck", "kind": "plain"}],
                        "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f), f)

    def test_badge_is_checked(self):
        f = v.findings({"badge": "A bottleneck", "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f), f)

    def test_name_is_checked(self):
        f = v.findings({"name": "A bottleneck", "voice_ok": None})
        self.assertTrue(any("bottleneck" in x for x in f), f)

    def test_kind_discriminators_are_never_checked_as_prose(self):
        """kind is an enum value, not prose -- index [2] of a row triple,
        and the 'kind' key of a box/chain entry, must never be inspected."""
        f = v.findings({
            "rows": [["LABEL", "Fine copy.", "denied"]],
            "boxes": [{"label": "A", "value": "1", "verdict": "V", "kind": "accent"},
                      {"label": "B", "value": "2", "verdict": "V", "kind": "accent"}],
            "chain": [{"text": "Fine.", "kind": "accent"}],
            "voice_ok": None,
        })
        self.assertEqual(f, [])

    def test_clean_structured_fields_pass(self):
        rec = {
            "rows": [["ADR-014", "Postgres is the record.", "held"]],
            "boxes": [{"label": "A", "value": "1", "verdict": "V", "kind": "warn"},
                      {"label": "B", "value": "2", "verdict": "V", "kind": "accent"}],
            "chain": [{"text": "DECISION", "kind": "plain"}],
            "badge": "NATIVE SUPPORT", "name": "Claude Code",
            "voice_ok": None,
        }
        self.assertEqual(v.findings(rec), [])

    def test_voice_ok_still_suppresses_structured_findings(self):
        f = v.findings({
            "rows": [["LABEL", "A bottleneck forms.", "neutral"]],
            "voice_ok": ["quoted external title"],
        })
        self.assertEqual(f, [])


if __name__ == "__main__":
    unittest.main()
