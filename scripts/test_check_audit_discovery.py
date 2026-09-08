"""Cover the Audit discovery contract validator against synthetic trees."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_audit_discovery as check

GOOD_AUDIT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Architecture Protection Audit | Mneme HQ</title>
</head>
<body><h1>Audit</h1></body>
</html>
"""

GOOD_WORKSPACE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta name="description" content="Architecture Protection Audit workspace - Mneme HQ" />
    <meta name="robots" content="noindex, follow" />
    <link rel="canonical" href="https://mnemehq.com/audit/" />
    <title>Architecture Protection Audit Workspace | Mneme HQ</title>
  </head>
  <body><div id="root"></div></body>
</html>
"""

GOOD_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://mnemehq.com/audit/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
"""

GOOD_LLMS = """# Mneme HQ

## Key pages

- [Architecture Protection Audit](https://mnemehq.com/audit/): Repository-level assessment.
"""


class AuditDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.write('site/audit/index.html', GOOD_AUDIT_PAGE)
        self.write('site/audit/workspace/index.html', GOOD_WORKSPACE)
        self.write('audit/frontend/index.html', GOOD_WORKSPACE)
        self.write('site/sitemap.xml', GOOD_SITEMAP)
        self.write('site/llms.txt', GOOD_LLMS)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def run_check(self):
        with patch.object(check, 'REPO_ROOT', self.root), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = check.main()
        return code, out.getvalue()

    def test_clean_tree_passes(self):
        code, output = self.run_check()
        self.assertEqual(code, 0, output)

    def test_retired_name_in_workspace_source_fails(self):
        self.write('audit/frontend/index.html',
                   GOOD_WORKSPACE.replace('Architecture Protection Audit workspace',
                                          'Architecture Governability Audit'))
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('audit/frontend/index.html', output)

    def test_retired_name_in_og_template_fails(self):
        self.write('site/og-audit.html',
                   '<span>Architecture Governability Audit</span>')
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('og-audit.html', output)

    def test_missing_sitemap_entry_fails(self):
        self.write('site/sitemap.xml',
                   GOOD_SITEMAP.replace('https://mnemehq.com/audit/',
                                        'https://mnemehq.com/demo/'))
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('sitemap.xml', output)

    def test_missing_llms_entry_fails(self):
        self.write('site/llms.txt', '# Mneme HQ\n\n## Key pages\n\n- [Home](https://mnemehq.com/): x.\n')
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('llms.txt', output)

    def test_generic_audit_title_fails(self):
        self.write('site/audit/index.html',
                   GOOD_AUDIT_PAGE.replace('Architecture Protection Audit | Mneme HQ',
                                           'Architecture Audit | Mneme HQ'))
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('canonical <title>', output)

    def test_workspace_without_noindex_fails(self):
        self.write('site/audit/workspace/index.html',
                   GOOD_WORKSPACE.replace(
                       '<meta name="robots" content="noindex, follow" />', ''))
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('noindex', output)

    def test_workspace_without_canonical_fails(self):
        self.write('audit/frontend/index.html',
                   GOOD_WORKSPACE.replace(
                       '<link rel="canonical" href="https://mnemehq.com/audit/" />', ''))
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn('canonical link', output)


if __name__ == '__main__':
    unittest.main()
