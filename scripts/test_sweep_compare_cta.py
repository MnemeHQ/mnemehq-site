"""Tests for the compare-page CTA sweep (scripts/sweep_compare_cta.py)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import sweep_compare_cta as sweep


STANDARD_BLOCK = (
    '<div class="cta-block">\n'
    '      <h3>Enforces decisions</h3>\n'
    '      <p>Open source, self-hosted, MIT licence.</p>\n'
    '      <a href="/pilot/" class="btn-primary" style="margin-right:0.5rem;">'
    'Request a pilot &rarr;</a>\n'
    '      <a href="https://github.com/MnemeHQ/mneme" class="btn-primary" '
    'style="background:transparent;border:1px solid var(--accent);'
    'color:var(--accent);">View on GitHub &rarr;</a>\n'
    '      <a href="/insights/x/" class="cta-secondary">Read: X &rarr;</a>\n'
    '    </div>'
)

CSS = ('.btn-primary { display: inline-block; background: var(--accent); '
       'color: #0c0c0d; padding: 0.65rem 1.5rem; border-radius: 8px; '
       'font-size: 0.85rem; font-weight: 600; font-family: \'DM Mono\', monospace; '
       'text-decoration: none; transition: background 0.15s; }\n'
       '.btn-primary:hover { background: var(--accent-dim); }\n')


class BridgedTests(unittest.TestCase):
    def test_bridged_page_gets_audit_primary_and_pilot_text(self):
        html = '<div class="page">' + CSS + STANDARD_BLOCK + '</div>'
        result, changes = sweep.instrument_text('cursor-rules', html)
        joined = ' '.join(changes)
        self.assertIn('bridged', joined)
        # Audit primary present and positioned end.
        self.assertIn('data-cta-intent="audit"', result)
        self.assertIn('Run the Architecture Audit', result)
        # Bridge copy inserted.
        self.assertIn('guidance to deterministic enforcement', result)
        # Pilot demoted to text link, tagged.
        self.assertIn('data-cta-intent="pilot"', result)
        self.assertIn('Request a pilot', result)
        # No lime fill left in the block or CSS.
        self.assertNotIn('background: var(--accent)', result)
        # Only one untagged anchor left (the editorial read link).
        self.assertEqual(result.count('class="cta-secondary"'), 2)

    def test_pilot_button_removed_from_primary_slot_when_bridged(self):
        result, _ = sweep.instrument_text('claude-md', STANDARD_BLOCK)
        self.assertNotIn(
            '<a href="/pilot/" class="btn-primary" style="margin-right:0.5rem;">'
            'Request a pilot &rarr;</a>', result)


class InstrumentOnlyTests(unittest.TestCase):
    def test_control_page_keeps_pilot_primary_but_gets_attributes(self):
        result, changes = sweep.instrument_text('windsurf', STANDARD_BLOCK)
        joined = ' '.join(changes)
        self.assertIn('hierarchy unchanged', joined)
        self.assertNotIn('bridged', joined)
        self.assertIn('data-cta-intent="pilot"', result)
        self.assertIn('data-cta-intent="github"', result)
        # Pilot stays the primary label.
        self.assertIn('Request a pilot &rarr;', result)
        self.assertIn('data-cta-component="end_block"', result)

    def test_variant_page_labels_are_preserved(self):
        html = ('<div class="cta-block">'
                '<a href="/pilot/" class="btn-primary" style="margin-right:0.5rem;">'
                'Request a pilot &rarr;</a>'
                '<a href="/works-with/devin/" class="btn-primary" '
                'style="background:transparent;border:1px solid var(--accent);'
                'color:var(--accent);margin-right:0.5rem;">Works with Devin &rarr;</a>'
                '<a href="https://github.com/MnemeHQ/mneme" class="btn-primary" '
                'style="background:transparent;border:1px solid var(--accent);'
                'color:var(--accent);">GitHub</a></div>' + CSS)
        result, _ = sweep.instrument_text('devin-vs-architectural-governance', html)
        self.assertIn('Works with Devin &rarr;', result)
        self.assertIn('>GitHub</a>', result)
        self.assertNotIn('View on GitHub', result)
        self.assertNotIn('var(--accent)', result)


class GeneralTests(unittest.TestCase):
    def test_idempotent_after_instrumentation(self):
        result, changes = sweep.instrument_text('windsurf', STANDARD_BLOCK)
        self.assertTrue(changes)
        again, second = sweep.instrument_text('windsurf', result)
        self.assertEqual(second, [])
        self.assertEqual(again, result)

    def test_crlf_line_endings_preserved(self):
        html = STANDARD_BLOCK.replace('\n', '\r\n')
        result, changes = sweep.instrument_text('windsurf', html)
        self.assertTrue(changes)
        self.assertNotIn('\n', result.replace('\r\n', ''))

    def test_detail_pages_skip_the_hub(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            compare = root / 'site' / 'compare'
            (compare / 'cursor-rules').mkdir(parents=True)
            (compare / 'index').mkdir()
            hub = compare / 'index' / 'index.html'
            hub.write_text('<html></html>', encoding='utf-8')
            detail = compare / 'cursor-rules' / 'index.html'
            detail.write_text('<html></html>', encoding='utf-8')
            with patch.object(sweep, 'REPO_ROOT', root), \
                 patch.object(sweep, 'COMPARE_DIR', compare):
                listed = sweep.detail_pages()
            self.assertEqual(listed, [detail])


if __name__ == '__main__':
    unittest.main()
