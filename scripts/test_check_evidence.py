#!/usr/bin/env python3
"""Regression tests for the evidence-contract checker."""

from __future__ import annotations

import re
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


class CheckGovernedPageTests(unittest.TestCase):
    """Fail-closed page-level tests: a governed page must carry its required
    evidence ID exactly once. These do not depend on any block being found,
    which is the property that closes the fail-open gap a deleted or
    swapped-out evidence block would otherwise slip through as."""

    def check_page(self, html: str, required_ids: list, registry: dict = REGISTRY):
        errors: list = []
        ce.check_governed_page(ce.Path("dummy.html"), required_ids, html, registry, errors)
        return errors

    def test_page_with_required_block_has_no_presence_error(self):
        errors = self.check_page(valid_e1_block(), ["E1"])
        self.assertFalse(any("requires exactly one evidence block" in e for e in errors))

    def test_deleted_block_fails(self):
        html = "<p>The evidence block used to be here but was removed.</p>"
        errors = self.check_page(html, ["E1"])
        self.assertTrue(
            any("requires exactly one evidence block for 'E1', found 0" in e for e in errors)
        )

    def test_wrong_evidence_id_on_page_fails(self):
        # Page carries a real, valid block -- just not the one this page requires.
        wrong_block = valid_e1_block().replace('data-evidence-id="E1"', 'data-evidence-id="E2"')
        wrong_block = wrong_block.replace(
            "https://example.com/e1-results.md", "https://example.com/e2-results.md"
        ).replace("7/7", "3/3").replace("0.33", "0/4")
        verified_registry = {**REGISTRY, "E2": {**REGISTRY["E2"], "status": "verified"}}
        errors = self.check_page(wrong_block, ["E1"], registry=verified_registry)
        self.assertTrue(
            any("requires exactly one evidence block for 'E1', found 0" in e for e in errors)
        )

    def test_duplicated_block_fails(self):
        html = valid_e1_block() + valid_e1_block()
        errors = self.check_page(html, ["E1"])
        self.assertTrue(
            any("requires exactly one evidence block for 'E1', found 2" in e for e in errors)
        )


class RealRegistryTests(unittest.TestCase):
    """Sanity checks against the actual docs/site/evidence-contract.json,
    not the synthetic fixture registry above."""

    def test_all_source_urls_are_pinned_to_a_commit_not_a_branch(self):
        # A `blob/main` URL can change after this PR merges while the
        # checker stays green -- ADR-004 exists to prevent exactly that.
        # Every registry entry must pin to a 40-hex commit SHA instead.
        commit_sha_re = re.compile(r"^https://github\.com/[^/]+/[^/]+/blob/[0-9a-f]{40}/")
        registry = ce.load_registry()
        for evidence_id, entry in registry.items():
            url = entry["source_artifact_url"]
            self.assertRegex(
                url, commit_sha_re,
                f"{evidence_id} source_artifact_url is not pinned to a commit SHA: {url!r}",
            )


if __name__ == "__main__":
    unittest.main()
