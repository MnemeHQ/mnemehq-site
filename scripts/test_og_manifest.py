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


class TestResolve(unittest.TestCase):
    def test_fills_family_and_motif_from_derivation(self):
        r = m.resolve("insights/architectural-drift/",
                      {"headline": "Architectural Drift"})
        self.assertEqual(r["family"], "editorial")
        self.assertEqual(r["motif"], "branch")

    def test_explicit_fields_win_over_derivation(self):
        r = m.resolve("insights/architectural-drift/",
                      {"headline": "X", "family": "brand", "motif": "stack"})
        self.assertEqual(r["family"], "brand")
        self.assertEqual(r["motif"], "stack")

    def test_tone_defaults_to_neutral_and_is_never_derived(self):
        r = m.resolve("insights/architectural-drift/", {"headline": "X"})
        self.assertEqual(r["tone"], "neutral")

    def test_tone_failure_is_honoured(self):
        r = m.resolve("insights/x/", {"headline": "X", "tone": "failure"})
        self.assertEqual(r["tone"], "failure")

    def test_invalid_tone_raises(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", {"headline": "X", "tone": "broken"})

    def test_alt_defaults_to_headline(self):
        r = m.resolve("insights/x/", {"headline": "Hello There"})
        self.assertEqual(r["alt"], "Hello There")

    def test_alt_override_is_kept(self):
        r = m.resolve("demo/x/", {"headline": "H", "alt": "A blocked change."})
        self.assertEqual(r["alt"], "A blocked change.")

    def test_lines_absent_yields_single_line(self):
        r = m.resolve("insights/x/", {"headline": "One Two Three"})
        self.assertEqual(r["lines"], ["One Two Three"])

    def test_lines_must_rejoin_to_headline(self):
        good = {"headline": "The Software Factory Needs a Governance Layer",
                "lines": ["The Software Factory Needs a", "Governance Layer"]}
        r = m.resolve("insights/x/", good)
        self.assertEqual(len(r["lines"]), 2)

    def test_lines_that_do_not_rejoin_raise(self):
        bad = {"headline": "The Software Factory Needs a Governance Layer",
               "lines": ["The Software Factory", "Something Else"]}
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", bad)

    def test_strict_mode_rejects_missing_record(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", None, strict=True)

    def test_non_strict_derives_a_bootstrap_record(self):
        r = m.resolve("insights/why-rag-fails/", None, strict=False)
        self.assertEqual(r["family"], "editorial")
        self.assertTrue(r["headline"])

    def test_strict_mode_rejects_unresolvable_family(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("qa-glossary/", {"headline": "X"}, strict=True)


class TestVariant(unittest.TestCase):
    def test_variant_defaults_to_none(self):
        r = m.resolve("insights/x/", {"headline": "X"})
        self.assertIsNone(r["variant"])

    def test_variant_hub_is_accepted_on_editorial(self):
        r = m.resolve("insights/all/", {"headline": "X", "variant": "hub"})
        self.assertEqual(r["variant"], "hub")

    def test_invalid_variant_raises(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("insights/x/", {"headline": "X", "variant": "bogus"})

    def test_variant_hub_on_non_editorial_family_raises(self):
        with self.assertRaises(m.ManifestError):
            m.resolve("demo/x/", {"headline": "X", "variant": "hub"})

    def test_subtitle_defaults_to_none(self):
        r = m.resolve("insights/x/", {"headline": "X"})
        self.assertIsNone(r["subtitle"])

    def test_subtitle_is_carried_when_present(self):
        r = m.resolve("insights/all/", {
            "headline": "X", "variant": "hub", "subtitle": "Every essay, one place"})
        self.assertEqual(r["subtitle"], "Every essay, one place")


if __name__ == "__main__":
    unittest.main()
