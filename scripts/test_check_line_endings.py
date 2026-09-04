"""Distinguish Git checkout conversion from newline changes in a candidate."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import check_line_endings as check


class CandidateLineEndingsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git('init', '-q')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'user.name', 'Local Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.page = self.root / 'page.html'

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              capture_output=True)

    def baseline(self, newline):
        self.page.write_bytes(b'<p>before</p>' + newline + (b'<p>text</p>' + newline) * 20)
        self.git('add', 'page.html')
        self.git('commit', '-qm', 'fixture')

    def run_check(self, *args):
        with patch.object(check, 'REPO_ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            return check.main(['check_line_endings.py', *args, 'HEAD'])

    def test_cached_check_ignores_working_checkout_conversion(self):
        self.baseline(b'\n')
        self.page.write_bytes(self.page.read_bytes().replace(b'before', b'after'))
        self.git('add', 'page.html')
        self.page.write_bytes(self.page.read_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(self.run_check('--cached'), 0)
        self.assertEqual(self.run_check(), 1)

    def test_cached_check_rejects_actual_newline_rewrite(self):
        self.baseline(b'\r\n')
        self.page.write_bytes(self.page.read_bytes().replace(b'\r\n', b'\n'))
        self.git('add', 'page.html')
        self.assertEqual(self.run_check('--cached'), 1)


if __name__ == '__main__':
    unittest.main()
