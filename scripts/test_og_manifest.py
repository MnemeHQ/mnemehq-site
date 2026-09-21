#!/usr/bin/env python3
"""Regression tests for the OG manifest loader."""
from __future__ import annotations

import unittest

import og_manifest as m


class TestFamilyForPath(unittest.TestCase):
    def test_editorial_prefixes(self):
        self.assertEqual(m.family_for_path("insights/rag-is-not-memory/"), "editorial")
        self.assertEqual(m.family_for_path("concepts/architectural-drift/"), "editorial")

    def test_integration_prefixes(self):
        self.assertEqual(m.family_for_path("integrations/claude-code/"), "integration")
        self.assertEqual(m.family_for_path("works-with/devin/"), "integration")
        self.assertEqual(m.family_for_path("supported-languages/python-governance/"), "integration")

    def test_proof_prefixes(self):
        self.assertEqual(m.family_for_path("demo/storage-decision/"), "proof")
        self.assertEqual(m.family_for_path("benchmark/"), "proof")
        self.assertEqual(m.family_for_path("architecture/how-retrieval-works/"), "proof")
        self.assertEqual(m.family_for_path("audit/methodology/"), "proof")

    def test_comparison_prefixes(self):
        self.assertEqual(m.family_for_path("compare/coderabbit/"), "comparison")
        self.assertEqual(m.family_for_path("use-cases/design-system-governance/"), "comparison")

    def test_brand_exact_paths(self):
        self.assertEqual(m.family_for_path(""), "brand")
        self.assertEqual(m.family_for_path("about/"), "brand")
        self.assertEqual(m.family_for_path("founder/"), "brand")
        self.assertEqual(m.family_for_path("pilot/"), "brand")

    def test_unresolved_paths_return_none(self):
        """These seven need an explicit family: in the manifest."""
        for rel in ("enterprise/trust/", "for/cto/", "for/platform/",
                    "for/principal-engineer/", "qa-glossary/",
                    "security/data-handling/",
                    "open-source-ai-coding-agent-governance/"):
            self.assertIsNone(m.family_for_path(rel), rel)

    def test_brand_exact_does_not_swallow_children(self):
        """'for/' is brand, but 'for/cto/' is deliberately unresolved."""
        self.assertEqual(m.family_for_path("for/"), "brand")
        self.assertIsNone(m.family_for_path("for/cto/"))


class TestMotifForSlug(unittest.TestCase):
    def test_topic_signals_select_motif(self):
        cases = {
            "architectural-drift-prevention": "branch",
            "constraint-decay-coding-agents": "branch",
            "software-factory-governance-layer": "stack",
            "emerging-ai-agent-infrastructure-stack": "stack",
            "zero-trust-for-ai-agents": "boundary",
            "migration-guardrails-for-ai-coding-agents": "boundary",
            "coordination-governance-multi-agent-systems": "connected",
            "governance-propagation": "propagation",
            "architecture-cannot-be-a-prompt-context-compaction": "broken",
            "runtime-verification-is-not-architectural-verification": "intersection",
            "why-observability-is-not-governance": "intersection",
        }
        for slug, expected in cases.items():
            self.assertEqual(m.motif_for_slug(slug), expected, slug)

    def test_no_signal_defaults_to_connected(self):
        self.assertEqual(m.motif_for_slug("what-is-the-ai-sdlc"), "connected")

    def test_result_is_always_a_known_motif(self):
        for slug in ("a", "zzz", "", "multi-agent-drift-stack"):
            self.assertIn(m.motif_for_slug(slug), m.MOTIFS)

    def test_is_deterministic(self):
        self.assertEqual(m.motif_for_slug("architectural-drift"),
                         m.motif_for_slug("architectural-drift"))

    def test_earlier_signal_wins_when_several_match(self):
        """drift beats stack, so the rule is order-defined not arbitrary."""
        self.assertEqual(m.motif_for_slug("drift-in-the-platform-stack"), "branch")


if __name__ == "__main__":
    unittest.main()
