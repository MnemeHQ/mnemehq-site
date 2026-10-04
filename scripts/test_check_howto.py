"""Tests for scripts/check_howto.py."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_howto import SECTIONS, check_page  # noqa: E402

VERSION = "0.9.2"


def _fixture(tmp_path: Path) -> Path:
    fx = tmp_path / "fx"
    (fx / "expected").mkdir(parents=True)
    (fx / "docs").mkdir()
    (fx / "docs" / "ADR-1.md").write_text("---\nid: ADR-1\n---\nBody line\n", encoding="utf-8")
    (fx / "steps.yaml").write_text(
        "steps:\n"
        "  - name: check\n"
        "    run: >-\n"
        "      mneme check --memory m.json\n"
        "      --input a.py --query q\n"
        "    expect_exit: 2\n",
        encoding="utf-8",
    )
    (fx / "expected" / "check.txt").write_text(
        "FAIL  [ADR-1] rule\n\nResult: FAIL\nexit=2\n", encoding="utf-8"
    )
    return fx


def _section(sid: str, body: str = "<p>Text.</p>") -> str:
    return f'<section class="prose-section" id="{sid}"><h2>{sid}</h2>{body}</section>'


def _page(tmp_path: Path, overrides: dict[str, str] | None = None, *,
          version: str = VERSION, end_up: bool = True, order=None) -> Path:
    bodies = {sid: "<p>Text.</p>" for sid in SECTIONS}
    bodies["configure"] = (
        '<pre class="term-block" data-fixture="file:docs/ADR-1.md">---\nid: ADR-1\n---\nBody line\n</pre>'
    )
    bodies["run"] = (
        '<pre class="term-block" data-fixture="cmd">mneme check --memory m.json \\\n'
        "  --input a.py --query q</pre>"
    )
    bodies["expected-result"] = (
        '<pre class="term-block" data-fixture="out:check">FAIL  [ADR-1] rule\n\nResult: FAIL</pre>'
    )
    bodies.update(overrides or {})
    ids = order or SECTIONS
    hero = f'<p class="howto-meta">~10 min &middot; Tested with mneme-hq {version}</p>'
    if end_up:
        hero += "<p class=\"end-up\">You&rsquo;ll end up with: a failing check.</p>"
    html = "<html><body>" + hero + "".join(_section(s, bodies[s]) for s in ids) + "</body></html>"
    page = tmp_path / "site" / "docs" / "how-to" / "demo" / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(html, encoding="utf-8")
    return page


def _site(tmp_path: Path, *, sitemap: bool = True, hub: bool = True) -> Path:
    site = tmp_path / "site"
    (site / "docs" / "how-to").mkdir(parents=True, exist_ok=True)
    (site / "sitemap.xml").write_text(
        "<loc>https://mnemehq.com/docs/how-to/demo/</loc>" if sitemap else "", encoding="utf-8"
    )
    (site / "docs" / "how-to" / "index.html").write_text(
        '<a href="/docs/how-to/demo/">Demo</a>' if hub else "", encoding="utf-8"
    )
    return site


def _check(tmp_path, page, **site_kw):
    site = _site(tmp_path, **site_kw)
    return check_page(page, _fixture(tmp_path), VERSION, site)


def test_well_formed_page_passes(tmp_path):
    assert _check(tmp_path, _page(tmp_path)) == []


def test_missing_section_is_reported(tmp_path):
    order = [s for s in SECTIONS if s != "evidence"]
    errors = _check(tmp_path, _page(tmp_path, order=order))
    assert any("evidence" in e and "missing" in e for e in errors)


def test_sections_out_of_order_are_reported(tmp_path):
    order = list(SECTIONS)
    order[0], order[1] = order[1], order[0]
    errors = _check(tmp_path, _page(tmp_path, order=order))
    assert any("order" in e for e in errors)


def test_stale_tested_version_is_reported(tmp_path):
    errors = _check(tmp_path, _page(tmp_path, version="0.9.1"))
    assert any("0.9.1" in e for e in errors)


def test_missing_end_up_line_is_reported(tmp_path):
    errors = _check(tmp_path, _page(tmp_path, end_up=False))
    assert any("end up with" in e for e in errors)


def test_command_not_in_fixture_is_reported(tmp_path):
    page = _page(tmp_path, {"run": '<pre data-fixture="cmd">mneme check --mode strict</pre>'})
    errors = _check(tmp_path, page)
    assert any("mneme check --mode strict" in e for e in errors)


def test_comment_lines_in_command_blocks_are_allowed(tmp_path):
    page = _page(tmp_path, {"run": '<pre data-fixture="cmd"># run the check\n'
                                   "mneme check --memory m.json --input a.py --query q</pre>"})
    assert _check(tmp_path, page) == []


def test_output_not_in_expected_file_is_reported(tmp_path):
    page = _page(tmp_path, {"expected-result": '<pre data-fixture="out:check">Result: PASS</pre>'})
    errors = _check(tmp_path, page)
    assert any("out:check" in e for e in errors)


def test_file_block_that_differs_from_fixture_file_is_reported(tmp_path):
    page = _page(tmp_path, {"configure": '<pre data-fixture="file:docs/ADR-1.md">id: ADR-2</pre>'})
    errors = _check(tmp_path, page)
    assert any("docs/ADR-1.md" in e for e in errors)


def test_unchecked_code_block_in_checked_section_is_reported(tmp_path):
    page = _page(tmp_path, {"evidence": "<pre>anything goes</pre>"})
    errors = _check(tmp_path, page)
    assert any("data-fixture" in e for e in errors)


def test_page_missing_from_sitemap_is_reported(tmp_path):
    errors = _check(tmp_path, _page(tmp_path), sitemap=False)
    assert any("sitemap" in e for e in errors)


def test_page_missing_from_hub_is_reported(tmp_path):
    errors = _check(tmp_path, _page(tmp_path), hub=False)
    assert any("hub" in e for e in errors)
