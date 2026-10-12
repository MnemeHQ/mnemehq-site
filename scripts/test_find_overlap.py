#!/usr/bin/env python3
"""Regression tests for the cannibalisation screen."""
from __future__ import annotations

import unittest

import find_overlap as f


def page(path: str, title: str, description: str = "") -> dict:
    slug = path.strip("/").rsplit("/", 1)[-1].replace("-", " ")
    return {"path": path, "title": title, "h1": title,
            "description": description, "slug": slug}


class TestTerms(unittest.TestCase):
    def test_drops_stopwords_and_brand(self):
        self.assertEqual(f.terms("What is the Mneme HQ view"), ["view"])

    def test_plural_ies_stems_to_y(self):
        self.assertEqual(f.terms("factories"), f.terms("factory"))

    def test_strips_site_suffix(self):
        self.assertEqual(f.clean("Multi-Agent Continuity — Mneme HQ Concepts"),
                         "Multi-Agent Continuity")


class TestScore(unittest.TestCase):
    def setUp(self):
        self.pages = [
            page("/insights/open-knowledge-format-vs-governance/",
                 "Open Knowledge Format vs Governance"),
            page("/insights/ai-coding-governance/", "AI Coding Governance"),
            page("/insights/ai-coding-review/", "AI Coding Review"),
            page("/insights/ai-coding-roi/", "AI Coding ROI"),
        ]
        self.idf = f.rarity(self.pages)

    def rank(self, title: str) -> list[str]:
        q = set(f.terms(title))
        qp = f.phrases(f.terms(title))
        scored = [(f.score(p, q, qp, self.idf)[0], p["path"]) for p in self.pages]
        return [path for s, path in sorted(scored, reverse=True) if s > 0]

    def test_same_entity_ranks_first(self):
        self.assertEqual(self.rank("Open Knowledge Format v0.2")[0],
                         "/insights/open-knowledge-format-vs-governance/")

    def test_rare_terms_outweigh_common_ones(self):
        """'roi' is on one page, 'ai coding' on three: the ROI page must win."""
        self.assertEqual(self.rank("AI coding ROI scorecard")[0], "/insights/ai-coding-roi/")


if __name__ == "__main__":
    unittest.main()
