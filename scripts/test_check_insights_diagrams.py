#!/usr/bin/env python3
"""Regression tests for the insight diagram guardrail in check_insights.py.

An inline <svg> diagram in an article body must reuse a canonical primitive
(site/assets/css/diagrams.css) or be a documented exception in
docs/site/insight-diagram-exceptions.json.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_insights as ci

NAV_ICON = '<nav><svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16"><path d="M0 0"/></svg></nav>'
# Labelled and not aria-hidden: only its position outside the article excludes it.
FOOTER_ICON = '<footer style="padding:0"><svg viewBox="0 0 24 24" aria-label="GitHub"></svg></footer>'
DIAGRAMS_LINK = '<link rel="stylesheet" href="/assets/css/diagrams.css">'
PRIMITIVE = '<div class="mneme-diagram mneme-diagram--checkpoints" role="img"></div>'


def page(body: str, head: str = "") -> str:
    """A minimal insight page with icons in the nav and footer and ``body`` in <article>."""
    return f"<html><head>{head}</head><body>{NAV_ICON}<article>{body}</article>{FOOTER_ICON}</body></html>"


def diagram(label: str | None) -> str:
    attr = f' aria-label="{label}"' if label is not None else ""
    return f'<svg viewBox="0 0 700 300" role="img"{attr}><rect/><text>x</text></svg>'


class TestArticleDiagrams(unittest.TestCase):
    def test_reads_the_label_of_a_body_diagram(self):
        html = page(diagram("A flow\n   of decisions"))
        self.assertEqual(ci.article_diagrams(html), ["A flow of decisions"])

    def test_skips_aria_hidden_icons_in_the_body(self):
        html = page('<p>x</p><svg aria-hidden="true" viewBox="0 0 24 24"><path/></svg>')
        self.assertEqual(ci.article_diagrams(html), [])

    def test_skips_svgs_outside_the_article_body(self):
        self.assertEqual(ci.article_diagrams(page("<p>no diagrams</p>")), [])

    def test_unlabelled_diagram_is_none(self):
        self.assertEqual(ci.article_diagrams(page(diagram(None))), [None])

    def test_decodes_entities_in_the_label(self):
        html = page(diagram("approval &amp; permission gates"))
        self.assertEqual(ci.article_diagrams(html), ["approval & permission gates"])

    def test_reads_the_older_article_wrap_template(self):
        html = (f'<html><body>{NAV_ICON}<div class="article-wrap">{diagram("Old layout")}</div>'
                f"{FOOTER_ICON}</body></html>")
        self.assertEqual(ci.article_diagrams(html), ["Old layout"])


class TestCheckDiagrams(unittest.TestCase):
    def test_registered_diagram_passes(self):
        self.assertEqual(ci.check_diagrams("a", page(diagram("Layer stack")), ["Layer stack"]), [])

    def test_unregistered_diagram_fails_and_names_it(self):
        errors = ci.check_diagrams("a", page(diagram("Layer stack")), [])
        self.assertEqual(len(errors), 1)
        self.assertIn("Layer stack", errors[0])

    def test_unlabelled_diagram_fails(self):
        self.assertEqual(len(ci.check_diagrams("a", page(diagram(None)), [])), 1)

    def test_registry_whitespace_does_not_matter(self):
        self.assertEqual(ci.check_diagrams("a", page(diagram("Layer stack")), ["  Layer   stack "]), [])

    def test_exception_for_a_removed_diagram_is_stale(self):
        errors = ci.check_diagrams("a", page(diagram("Kept")), ["Kept", "Removed"])
        self.assertEqual(len(errors), 1)
        self.assertIn("Removed", errors[0])

    def test_second_copy_of_a_registered_diagram_fails(self):
        html = page(diagram("Layer stack") + diagram("Layer stack"))
        self.assertEqual(len(ci.check_diagrams("a", html, ["Layer stack"])), 1)

    def test_primitive_with_its_stylesheet_needs_no_exception(self):
        self.assertEqual(ci.check_diagrams("a", page(PRIMITIVE, head=DIAGRAMS_LINK), []), [])

    def test_versioned_stylesheet_link_counts(self):
        head = '<link rel="stylesheet" href="/assets/css/diagrams.css?v=20261113">'
        self.assertEqual(ci.check_diagrams("a", page(PRIMITIVE, head=head), []), [])

    def test_primitive_without_its_stylesheet_fails(self):
        self.assertEqual(len(ci.check_diagrams("a", page(PRIMITIVE), [])), 1)


def registry(**overrides) -> dict:
    reg = {
        "patterns": {
            "bespoke": {"reuse": "bespoke", "note": "Specific to one article."},
            "checkpoints": {
                "reuse": "existing-primitive",
                "primitive": "mneme-diagram--checkpoints",
                "priority": 1,
                "note": "Redraws the enforcement checkpoints primitive.",
            },
        },
        "exceptions": [
            {
                "page": "a",
                "label": "Report chart",
                "pattern": "bespoke",
                "rationale": "Plots report figures that no primitive can show.",
            },
        ],
    }
    reg.update(overrides)
    return reg


ENTRY = {"page": "a", "label": "Report chart", "pattern": "bespoke",
         "rationale": "Plots report figures that no primitive can show."}


class TestCheckDiagramRegistry(unittest.TestCase):
    def test_valid_registry_passes(self):
        self.assertEqual(ci.check_diagram_registry(registry(), {"a"}), [])

    def test_entry_for_a_missing_page_fails(self):
        self.assertEqual(len(ci.check_diagram_registry(registry(), set())), 1)

    def test_unknown_pattern_fails(self):
        reg = registry(exceptions=[dict(ENTRY, pattern="spiral")])
        self.assertEqual(len(ci.check_diagram_registry(reg, {"a"})), 1)

    def test_token_rationale_fails(self):
        reg = registry(exceptions=[dict(ENTRY, rationale="custom")])
        self.assertEqual(len(ci.check_diagram_registry(reg, {"a"})), 1)

    def test_empty_label_fails(self):
        reg = registry(exceptions=[dict(ENTRY, label="  ")])
        self.assertEqual(len(ci.check_diagram_registry(reg, {"a"})), 1)

    def test_duplicate_entry_fails_even_with_different_spacing(self):
        reg = registry(exceptions=[ENTRY, dict(ENTRY, label="Report   chart")])
        self.assertEqual(len(ci.check_diagram_registry(reg, {"a"})), 1)

    def test_unknown_reuse_class_fails(self):
        reg = registry(patterns={"bespoke": {"reuse": "maybe", "note": "Specific to one article."}})
        self.assertEqual(len(ci.check_diagram_registry(reg, {"a"})), 1)

    def test_existing_primitive_pattern_must_name_the_primitive(self):
        pats = registry()["patterns"]
        pats["checkpoints"] = {"reuse": "existing-primitive", "note": "Redraws a primitive."}
        self.assertEqual(len(ci.check_diagram_registry(registry(patterns=pats), {"a"})), 1)

    def test_wrong_top_level_shape_fails(self):
        self.assertTrue(ci.check_diagram_registry([], {"a"}))


class TestRegisteredDiagramLabels(unittest.TestCase):
    def test_groups_labels_by_page(self):
        reg = registry(exceptions=[ENTRY, dict(ENTRY, label="Second"), dict(ENTRY, page="b", label="Other")])
        self.assertEqual(ci.registered_diagram_labels(reg), {"a": ["Report chart", "Second"], "b": ["Other"]})

    def test_malformed_registry_yields_no_labels_instead_of_crashing(self):
        self.assertEqual(ci.registered_diagram_labels([]), {})
        self.assertEqual(ci.registered_diagram_labels({"exceptions": [None, {"page": 1, "label": "x"}]}), {})


class TestLoadDiagramExceptions(unittest.TestCase):
    def test_reads_the_registry(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "registry.json"
            path.write_text('{"patterns": {}, "exceptions": []}', encoding="utf-8")
            self.assertEqual(ci.load_diagram_exceptions(path), {"patterns": {}, "exceptions": []})

    def test_invalid_json_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "registry.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                ci.load_diagram_exceptions(path)

    def test_missing_file_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                ci.load_diagram_exceptions(Path(d) / "absent.json")


if __name__ == "__main__":
    unittest.main()
