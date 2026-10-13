"""Regression tests for structured-data checks around details-based navigation."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seo_check  # noqa: E402


def test_nested_breadcrumb_ignores_page_switcher_links():
    markup = """
    <ol class="breadcrumb">
      <li><a href="/">Home</a></li>
      <li><a href="/docs/">Docs</a></li>
      <li><a href="/docs/how-to/">How-to guides</a></li>
      <!-- mneme:page-switcher:start --><li class="page-switcher-item">
        <details class="page-switcher"><summary>Current</summary><ul>
          <li><a href="/docs/cli/">CLI</a></li>
          <li><a href="/docs/mcp/">MCP</a></li>
        </ul></details>
      </li><!-- mneme:page-switcher:end -->
    </ol>
    """
    ctx = SimpleNamespace(rel_path="docs/how-to/example/index.html")
    assert seo_check.rule_breadcrumb_html(markup, ctx) == (seo_check.PASS, "")


def test_page_switcher_details_are_not_treated_as_faq():
    markup = """
    <details class="page-switcher"><summary>Current page</summary>
      <a href="/docs/cli/">CLI</a>
    </details>
    """
    ctx = SimpleNamespace(main_body=markup, types={"Article"})
    assert seo_check.rule_faq_consistency(markup, ctx) == (seo_check.PASS, "")


def test_real_details_faq_still_requires_faq_schema():
    markup = "<section class='article-faq'><details><summary>Question?</summary><p>Answer.</p></details></section>"
    ctx = SimpleNamespace(main_body=markup, types={"Article"})
    status, message = seo_check.rule_faq_consistency(markup, ctx)
    assert status == seo_check.FAIL
    assert "FAQPage" in message
