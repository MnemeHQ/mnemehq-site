#!/usr/bin/env python3
"""Regression tests for the cannibalisation screen."""
from __future__ import annotations

import unittest

import find_overlap as f


def page(path: str, title: str, description: str = "", lede: str = "",
         image_alt: str = "") -> dict:
    slug = path.strip("/").rsplit("/", 1)[-1].replace("-", " ")
    return {"path": path, "title": title, "h1": title, "description": description,
            "lede": lede, "image_alt": image_alt, "slug": slug}


class TestTerms(unittest.TestCase):
    def test_drops_stopwords_and_brand(self):
        self.assertEqual(f.terms("What is the Mneme HQ view"), ["view"])

    def test_plural_ies_stems_to_y(self):
        self.assertEqual(f.terms("factories"), f.terms("factory"))

    def test_plurals_of_words_ending_in_e_keep_the_e(self):
        for plural, singular in [("pipelines", "pipeline"), ("releases", "release"),
                                 ("changes", "change"), ("services", "service")]:
            self.assertEqual(f.terms(plural), f.terms(singular), plural)

    def test_es_plurals_after_sibilants(self):
        for plural, singular in [("boxes", "box"), ("branches", "branch"),
                                 ("classes", "class"), ("fixes", "fix")]:
            self.assertEqual(f.terms(plural), f.terms(singular), plural)

    def test_words_ending_in_s_are_not_truncated(self):
        self.assertEqual(f.terms("status analysis"), ["status", "analysis"])

    def test_strips_site_suffix(self):
        self.assertEqual(f.clean("Multi-Agent Continuity — Mneme HQ Concepts"),
                         "Multi-Agent Continuity")

    def test_lede_is_read_from_the_page(self):
        source = '<p class="article-lede">Coding activity rose <em>240%</em>.</p>'
        self.assertEqual(f.first(f.LEDE_RE, source), "Coding activity rose 240% .")


class TestScore(unittest.TestCase):
    def setUp(self):
        self.pages = [
            page("/insights/open-knowledge-format-vs-governance/",
                 "Open Knowledge Format vs Governance"),
            page("/insights/ai-coding-governance/", "AI Coding Governance"),
            page("/insights/ai-coding-review/", "AI Coding Review"),
            page("/insights/ai-coding-roi/", "AI Coding ROI"),
        ]

    def rank(self, title: str, pages: list[dict] | None = None) -> list[tuple[float, str]]:
        pages = pages or self.pages
        idf = f.rarity(pages)
        q = set(f.terms(title))
        qp = f.phrases(f.terms(title))
        scored = [(f.score(p, q, qp, idf)[0], p["path"]) for p in pages]
        return [(s, path) for s, path in sorted(scored, reverse=True) if s > 0]

    def test_same_entity_ranks_first(self):
        self.assertEqual(self.rank("Open Knowledge Format v0.2")[0][1],
                         "/insights/open-knowledge-format-vs-governance/")

    def test_rare_terms_outweigh_common_ones(self):
        """'roi' is on one page, 'ai coding' on three: the ROI page must win."""
        self.assertEqual(self.rank("AI coding ROI scorecard")[0][1], "/insights/ai-coding-roi/")

    def test_finding_stated_only_in_the_lede_is_found(self):
        """The NBER miss (2026-10-12): an article whose title is a thesis carries
        its headline numbers only in the lede and image alt text. A proposal
        built on the same numbers must rank it first."""
        pages = self.pages + [
            page("/insights/ai-throughput-is-not-engineering-throughput/",
                 "AI Throughput Is Not Engineering Throughput",
                 description="Generation speed and delivery speed are different things.",
                 lede="NBER found coding activity up 240% while releases rose 30%.",
                 image_alt="Coding activity up 240%, releases up 30%"),
            page("/insights/ai-productivity-studies/", "AI Productivity Studies"),
        ]
        ranked = self.rank("AI Can Raise Coding Activity 240%. Why Do Releases Rise Only 30%?", pages)
        self.assertEqual(ranked[0][1], "/insights/ai-throughput-is-not-engineering-throughput/")


if __name__ == "__main__":
    unittest.main()
