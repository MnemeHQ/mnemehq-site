"""new_article.py must stamp exactly one mid-article CTA band, and never touch
an article that already carries one.

Regression: templates/article.html puts the body file straight after the
article header with no <div class="article-body"> wrapper, and stamp() used
to look only for that wrapper, so every article built from the template
shipped without a band and new_article.py only printed a warning.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insert_mid_cta_band as band  # noqa: E402
import new_article  # noqa: E402

BAND_OPEN = '<aside class="cta-band"'


def _para(n: int) -> str:
    return "<p>" + " ".join(f"word{i}" for i in range(n)) + "</p>"


def _body(first_section_words: int) -> str:
    # The shape of a current body file: sections open with <h2>, no wrapper.
    return "\n\n".join([
        '<h2 id="one">First section</h2>', _para(first_section_words),
        '<h2 id="two">Second section</h2>', _para(120),
        '<h2 id="three">Third section</h2>', _para(120),
    ])


def _build(tmp_path, monkeypatch, body: str) -> str:
    monkeypatch.setattr(new_article, "SITE", tmp_path / "site")
    body_file = tmp_path / "body.html"
    body_file.write_text(body, encoding="utf-8")
    rc = new_article.main([
        "--slug", "test-article", "--title", "Test article",
        "--description", "A test article.", "--lede", "A lede.",
        "--date", "2026-11-27", "--body-file", str(body_file),
        "--type", "Analysis", "--topic", sorted(new_article.TOPIC_NAMES)[0],
    ])
    assert rc == 0
    return (tmp_path / "site" / "insights" / "test-article" / "index.html").read_text(encoding="utf-8")


def test_new_article_gets_exactly_one_band_at_first_section_end(tmp_path, monkeypatch):
    page = _build(tmp_path, monkeypatch, _body(200))
    assert page.count(BAND_OPEN) == 1
    after = page[page.index(BAND_OPEN):]
    assert re.search(r"</aside>\s*<h2[^>]*>(.*?)</h2>", after).group(1) == "Second section"


def test_band_waits_for_150_words(tmp_path, monkeypatch):
    # 100 words in the first section is too short; the band moves one section on.
    page = _build(tmp_path, monkeypatch, _body(100))
    assert page.count(BAND_OPEN) == 1
    after = page[page.index(BAND_OPEN):]
    assert re.search(r"</aside>\s*<h2[^>]*>(.*?)</h2>", after).group(1) == "Third section"


def test_too_short_article_gets_no_band_and_a_warning(tmp_path, monkeypatch, capsys):
    page = _build(tmp_path, monkeypatch, '<h2>One</h2>\n<p>short</p>\n<h2>Two</h2>\n<p>short</p>')
    assert BAND_OPEN not in page
    assert "no section boundary" in capsys.readouterr().err


def test_stamp_is_idempotent_and_keeps_crlf():
    text = ('<article class="article-wrap">\r\n  <header>h</header>\r\n\r\n'
            + _body(200).replace("\n", "\r\n") + "\r\n</article>\r\n")
    once = band.stamp(text)
    assert once.count(BAND_OPEN) == 1
    assert "\n" not in once.replace("\r\n", "")
    assert band.stamp(once) == once


def test_legacy_article_body_wrapper_still_works():
    text = ('<article class="article-wrap"><header>h</header>\n'
            '<div class="article-body">\n' + _body(200) + "\n</div></article>")
    out = band.stamp(text)
    assert out.count(BAND_OPEN) == 1
    assert out.index(BAND_OPEN) < out.index('<h2 id="two"')


@pytest.mark.parametrize("page", sorted(
    p for p in band.INSIGHTS.glob("*/index.html") if p.parent.name not in band.NON_ARTICLE))
def test_published_banded_articles_are_untouched(page):
    text = page.read_bytes().decode("utf-8")
    if 'class="cta-band"' in text:
        assert band.stamp(text) == text
