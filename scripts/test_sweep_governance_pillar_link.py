#!/usr/bin/env python3
"""Tests for sweep_governance_pillar_link.insert_pillar_link."""
import contextlib
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sweep_governance_pillar_link as sweep
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


BODY_LIST = (
    '<ul>\n'
    '      <li><a href="/insights/ai-agent-governance-two-markets/">An in-body mention</a></li>\n'
    '</ul>\n'
)


def test_in_body_pillar_link_survives():
    out, status = insert_pillar_link(BODY_LIST + RELATED)
    assert status == "inserted"
    assert "An in-body mention" in out
    assert out.count(HUB_HREF) == 2


def test_canonical_plus_stale_duplicate_is_replaced():
    src = RELATED.replace('    <ul class="related-list">\n',
                          '    <ul class="related-list">\n' + CANONICAL_LI + OLD_LI)
    out, status = insert_pillar_link(src)
    assert status == "replaced"
    assert out.count(HUB_HREF) == 1
    assert "Is Splitting Into Two Markets" not in out


def test_check_mode_reports_pending_changes_without_writing():
    saved_root, saved_targets = sweep.ROOT, sweep.TARGETS
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "site" / "insights" / "demo-slug" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_bytes(RELATED.encode("utf-8"))
        sweep.ROOT, sweep.TARGETS = Path(tmp), ["demo-slug"]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                assert sweep.main(["--check"]) == 1
                assert page.read_bytes().decode("utf-8") == RELATED
                assert sweep.main(["--write"]) == 0
                assert sweep.main(["--check"]) == 0
        finally:
            sweep.ROOT, sweep.TARGETS = saved_root, saved_targets


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
