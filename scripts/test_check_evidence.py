#!/usr/bin/env python3
"""Regression tests for the evidence-contract checker."""

from __future__ import annotations

import unittest

import check_evidence as ce

REGISTRY = {
    "E1": {
        "source_artifact_url": "https://example.com/e1-results.md",
        "required_result_tokens": ["7/7", "0.33"],
        "forbidden_claims": ["guarantees", "eliminates", "always", "prevents"],
        "status": "verified",
    },
    "E2": {
        "source_artifact_url": "https://example.com/e2-results.md",
        "required_result_tokens": ["3/3", "0/4"],
        "forbidden_claims": ["guarantees", "eliminates", "always", "prevents"],
        "status": "pending-upstream-merge",
    },
}


def valid_e1_block() -> str:
    return (
        '<div class="callout callout-evidence" data-evidence-id="E1">'
        '<p class="evidence-claim"><strong>First-party validation.</strong> '
        "Mneme's frozen enforcement benchmark produced the expected verdict "
        "in 7/7 governed cases.</p>"
        '<p class="evidence-limitation">This validates the deterministic '
        "enforcement path under fixed benchmark scenarios; it does not "
        "establish production-team impact. The same suite's retrieval "
        "precision@3 is 0.33.</p>"
        '<a class="evidence-source" href="https://example.com/e1-results.md">'
        "Method and artifacts &rarr;</a>"
        "</div>"
    )


class CheckEvidenceTests(unittest.TestCase):
    def check(self, html: str, registry: dict = REGISTRY):
        errors: list = []
        for evidence_id, block_html in ce.find_evidence_blocks(html):
            ce.check_block(
                ce.Path("dummy.html"), evidence_id, block_html, registry, errors
            )
        return errors

    def test_valid_block_has_no_errors(self):
        self.assertEqual(self.check(valid_e1_block()), [])

    def test_unknown_evidence_id(self):
        html = valid_e1_block().replace('data-evidence-id="E1"', 'data-evidence-id="E9"')
        errors = self.check(html)
        self.assertTrue(any("unknown evidence ID" in e for e in errors))

    def test_pending_status_rejected(self):
        html = valid_e1_block().replace('data-evidence-id="E1"', 'data-evidence-id="E2"')
        html = html.replace("https://example.com/e1-results.md", "https://example.com/e2-results.md")
        html = html.replace("7/7", "3/3").replace("0.33", "0/4")
        errors = self.check(html)
        self.assertTrue(any("not eligible to cite" in e for e in errors))

    def test_mismatched_source(self):
        html = valid_e1_block().replace(
            "https://example.com/e1-results.md", "https://example.com/wrong.md"
        )
        errors = self.check(html)
        self.assertTrue(any("source mismatch" in e for e in errors))

    def test_missing_limitation(self):
        html = valid_e1_block()
        html = html.replace(
            '<p class="evidence-limitation">This validates the deterministic '
            "enforcement path under fixed benchmark scenarios; it does not "
            "establish production-team impact. The same suite's retrieval "
            "precision@3 is 0.33.</p>",
            "",
        )
        errors = self.check(html)
        self.assertTrue(any("evidence-limitation is missing" in e for e in errors))

    def test_missing_required_token(self):
        html = valid_e1_block().replace("7/7", "seven of seven")
        errors = self.check(html)
        self.assertTrue(any("missing required result token '7/7'" in e for e in errors))

    def test_forbidden_claim_present(self):
        html = valid_e1_block().replace(
            "produced the expected verdict",
            "guarantees the expected verdict",
        )
        errors = self.check(html)
        self.assertTrue(any("forbidden claim language present: 'guarantees'" in e for e in errors))

    def test_find_evidence_blocks_ignores_non_evidence_callouts(self):
        html = '<div class="callout"><p>Just a regular callout.</p></div>'
        self.assertEqual(list(ce.find_evidence_blocks(html)), [])


if __name__ == "__main__":
    unittest.main()
