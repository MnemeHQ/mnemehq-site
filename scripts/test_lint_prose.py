#!/usr/bin/env python3
"""Regression tests for the comprehension and AI-slop filter."""
from __future__ import annotations

import unittest

import lint_prose as lp


def run(html_body: str):
    return lp.lint(lp.extract_paragraphs(f"<article>{html_body}</article>", True))


class TestHouseVoice(unittest.TestCase):
    def test_bottleneck_is_an_error(self):
        errors, _, _ = run("<p>Review is the bottleneck now.</p>")
        self.assertTrue(any("bottleneck" in e for e in errors))

    def test_em_dash_is_an_error(self):
        errors, _, _ = run("<p>Agents act fast — reviewers do not.</p>")
        self.assertTrue(any("em dash" in e for e in errors))

    def test_en_dash_range_is_fine(self):
        errors, _, _ = run("<p>Adoption rose in 2024–2026.</p>")
        self.assertEqual(errors, [])

    def test_voice_ok_comment_suppresses_errors(self):
        body = '<!-- voice-ok: quoted report title --><p>"The Bottleneck Myth" report says so.</p>'
        errors, _, _ = run(body)
        self.assertEqual(errors, [])

    def test_aside_components_are_skipped(self):
        errors, _, _ = run('<aside class="cta-band"><p>No signup — MIT.</p></aside><p>Plain.</p>')
        self.assertEqual(errors, [])


class TestSlop(unittest.TestCase):
    def test_flags_throat_clearing_and_contrast(self):
        _, warnings, _ = run("<p>Here's the thing: it's not speed, it's control.</p>")
        kinds = " ".join(warnings)
        self.assertIn("throat-clearing", kinds)
        self.assertIn("binary contrast", kinds)

    def test_clean_sentence_has_no_slop(self):
        _, warnings, _ = run("<p>The team blocked the change before it reached review.</p>")
        self.assertFalse(any("slop/" in w for w in warnings))


class TestSiteMarkup(unittest.TestCase):
    """Cases from the 2026-10-12 audit: built pages were partly invisible."""

    def test_typographic_apostrophes_are_matched(self):
        _, warnings, _ = run("<p>Here&rsquo;s the thing: it&rsquo;s not speed, it&rsquo;s control.</p>")
        kinds = " ".join(warnings)
        self.assertIn("throat-clearing", kinds)
        self.assertIn("binary contrast", kinds)

    def test_contraction_is_one_word(self):
        self.assertEqual(lp.words("Don’t".translate(lp.QUOTES)), ["Don't"])

    def test_article_header_title_and_lede_are_linted(self):
        page = ("<article><header><span class=\"eyebrow-tag\">Analysis</span>"
                "<h1>The bottleneck moved</h1>"
                "<p class=\"article-lede\">Here&rsquo;s the thing about review.</p></header>"
                "<p>Body.</p></article>")
        errors, warnings, _ = lp.lint(lp.extract_paragraphs(page, True))
        self.assertTrue(any("bottleneck" in e for e in errors))
        self.assertTrue(any("throat-clearing" in w for w in warnings))

    def test_markdown_fence_with_blank_line_is_skipped(self):
        md = "Plain prose.\n\n```\nfirst — line\n\nsecond bottleneck line\n```\n\nMore prose.\n"
        errors, _, _ = lp.lint(lp.extract_paragraphs(md, False))
        self.assertEqual(errors, [])

    def test_voice_ok_covers_only_the_next_block(self):
        body = ('<!-- voice-ok: verbatim EY quote --><p>"AI pushed the bottleneck downstream."</p>'
                "<p>Our bottleneck is review.</p>")
        errors, _, _ = run(body)
        self.assertEqual(len(errors), 1)
        self.assertIn("para 2", errors[0])


class TestComprehension(unittest.TestCase):
    def test_flags_unexpanded_acronym(self):
        _, warnings, _ = run("<p>The OKF spec adds trust fields.</p>")
        self.assertTrue(any("'OKF'" in w for w in warnings))

    def test_expanded_acronym_passes(self):
        _, warnings, _ = run("<p>The Open Knowledge Format (OKF) adds trust fields. OKF is open.</p>")
        self.assertFalse(any("'OKF'" in w for w in warnings))

    def test_flags_long_sentences(self):
        long = " ".join(["word"] * 40) + "."
        _, warnings, stats = run(f"<p>{long}</p>")
        self.assertGreater(stats["avg_sentence"], lp.MAX_AVG_SENTENCE)
        self.assertTrue(any("average sentence" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
