"""Tests for the retired-label sweep (scripts/sweep_drift_audit_cta.py)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import sweep_drift_audit_cta as sweep


class SweepTextTests(unittest.TestCase):
    def test_replaces_the_retired_label(self):
        html = '<a href="/pilot/" data-cta-intent="pilot">Request a drift audit</a>'
        result, count = sweep.sweep_text(html)
        self.assertEqual(count, 1)
        self.assertEqual(result,
                         '<a href="/pilot/" data-cta-intent="pilot">Request a pilot</a>')

    def test_replaces_every_occurrence_including_inline_text(self):
        html = ('<a href="/pilot/">Request a drift audit</a>'
                '<p>Evaluating for your team? Request a drift audit &rarr;</p>')
        result, count = sweep.sweep_text(html)
        self.assertEqual(count, 2)
        self.assertNotIn(sweep.OLD_LABEL, result)

    def test_idempotent_when_no_retired_label_present(self):
        html = '<a href="/pilot/" data-cta-intent="pilot">Request a pilot</a>'
        result, count = sweep.sweep_text(html)
        self.assertEqual(count, 0)
        self.assertEqual(result, html)

    def test_crlf_line_endings_are_preserved(self):
        html = '<html>\r\n<body>\r\n<p>Request a drift audit</p>\r\n</body>\r\n</html>'
        result, count = sweep.sweep_text(html)
        self.assertEqual(count, 1)
        self.assertIn('\r\n', result)
        self.assertNotIn('\n', result.replace('\r\n', ''))


class TargetTests(unittest.TestCase):
    def test_og_templates_are_excluded(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'site').mkdir()
            (root / 'templates').mkdir()
            og = root / 'site' / 'og-pilot.html'
            og.write_text('<p>Request a drift audit</p>', encoding='utf-8')
            page = root / 'templates' / 'cta-components.html'
            page.write_text('<a>Request a drift audit</a>', encoding='utf-8')
            with patch.object(sweep, 'REPO_ROOT', root):
                listed = list(sweep.targets())
            self.assertIn(page, listed)
            self.assertNotIn(og, listed)


if __name__ == '__main__':
    unittest.main()
