#!/usr/bin/env python3
"""Tests for sweep_governance_pillar_link.insert_pillar_link."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sweep_governance_pillar_link import CANONICAL_LI, HUB_HREF, insert_pillar_link

RELATED = (
    '<aside class="related-panel" aria-labelledby="related-essays-label">\n'
    '    <div class="related-panel-label" id="related-essays-label">Related essays</div>\n'
    '    <ul class="related-list">\n'
    '      <li><a href="/insights/other/"><div class="rel-title">Other</div></a></li>\n'
    '    </ul>\n  </aside>'
)
OLD_LI = ('      <li><a href="/insights/ai-agent-governance-two-markets/"><div class="rel-title">'
          'AI Agent Governance Is Splitting Into Two Markets</div><p class="rel-desc">x</p></a></li>\n')


def test_inserts_as_first_item():
    out, status = insert_pillar_link(RELATED)
    assert status == "inserted"
    assert out.index(CANONICAL_LI) < out.index("/insights/other/")
    assert out.count(HUB_HREF) == 1


def test_replaces_stale_entry_without_duplicating():
    src = RELATED.replace('    <ul class="related-list">\n', '    <ul class="related-list">\n' + OLD_LI)
    out, status = insert_pillar_link(src)
    assert status == "replaced"
    assert out.count(HUB_HREF) == 1
    assert "Is Splitting Into Two Markets" not in out


def test_idempotent():
    once, _ = insert_pillar_link(RELATED)
    twice, status = insert_pillar_link(once)
    assert status == "unchanged" and twice == once


def test_missing_related_list_is_reported_not_guessed():
    out, status = insert_pillar_link("<article><p>no panel</p></article>")
    assert status == "no-related-list"
    assert HUB_HREF not in out


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
