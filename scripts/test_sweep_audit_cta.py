"""Regression checks for browser-visible CTA segmentation and repeatable sweeps."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import sweep_audit_cta as sweep


class SegmentTags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_head = False
        self.values = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        attrs = dict(attrs)
        if self.in_head and tag == 'meta' and attrs.get('name') == sweep.SEGMENT_META:
            self.values.append(attrs.get('content'))

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False


class SweepTests(unittest.TestCase):
    def test_examples_do_not_replace_browser_visible_metadata(self):
        example = '<meta name="mneme:content-segment" content="developer_evaluation">'
        for nl in ('\n', '\r\n'):
            with self.subTest(newline=repr(nl)):
                html = (f'<html><head>{nl}<!-- {example} -->{nl}'
                        f'<script>/* {example} */</script>{nl}</head><body>'
                        f'<script>/* {example} */</script></body></html>')
                result, changed = sweep.ensure_segment_meta(html, sweep.SEGMENT_PROBLEM, nl)
                self.assertTrue(changed)
                self.assertEqual(SegmentTags(result).values, [sweep.SEGMENT_PROBLEM])
                self.assertEqual(result.count(example), 3)
                self.assertEqual(sweep.ensure_segment_meta(result, sweep.SEGMENT_PROBLEM, nl),
                                 (result, False))

    def test_existing_real_tag_is_updated_once(self):
        html = '<head><meta name="mneme:content-segment" content="old" /></head>'
        result, changed = sweep.ensure_segment_meta(html, sweep.SEGMENT_DEV, '\n')
        self.assertTrue(changed)
        self.assertEqual(SegmentTags(result).values, [sweep.SEGMENT_DEV])

    def test_already_routed_end_block_still_receives_segment(self):
        slug = 'how-ai-coding-agents-use-adrs'
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / slug / 'index.html'
            page.parent.mkdir()
            page.write_text('<head></head><body><aside class="cta-block-end" '
                            'data-mneme-cta="context"><a href="/audit/">Audit</a>'
                            '</aside></body>', encoding='utf-8')
            with patch.object(sweep, 'INSIGHTS_DIR', root):
                self.assertEqual(sweep.process(slug, sweep.SEGMENT_DEV, True)['status'], 'written')
                self.assertEqual(SegmentTags(page.read_text()).values, [sweep.SEGMENT_DEV])
                self.assertEqual(sweep.process(slug, sweep.SEGMENT_DEV, True)['status'], 'skip-current')

    def test_problem_routing_keeps_previous_primary_on_repeat(self):
        block = ('<aside class="context-cta" data-mneme-cta="context">'
                 '<p class="context-cta-copy">Original copy</p>'
                 '<a href="/demo/" class="context-cta-primary">Demo &rarr;</a>'
                 '<a href="/pilot/" class="context-cta-secondary">Pilot &rarr;</a></aside>')
        slug = next(iter(sweep.SEGMENT_PROBLEM_SLUGS))
        result, _ = sweep.rewrite_block(block, sweep.SEGMENT_PROBLEM, slug)
        self.assertEqual(sweep.rewrite_block(result, sweep.SEGMENT_PROBLEM, slug)[0], result)
        self.assertIn('href="/demo/" class="context-cta-secondary"', result)


if __name__ == '__main__':
    unittest.main()
