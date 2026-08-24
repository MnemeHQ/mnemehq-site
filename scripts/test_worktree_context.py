#!/usr/bin/env python3
"""Regression tests for the worktree context guard and task provisioner.

Stdlib-only (unittest), matching this repo's check convention. Each test
builds a small real git repository in a temp directory so git subprocess
calls run against actual state, including detached HEAD.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARD = REPO_ROOT / "scripts" / "check_worktree_context.py"
PROVISIONER = REPO_ROOT / "scripts" / "new_task_worktree.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = _load("check_worktree_context", GUARD)
provisioner = _load("new_task_worktree", PROVISIONER)


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"


class GuardTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "file.txt").write_text("one\n", encoding="utf-8")
        git(self.repo, "add", "file.txt")
        git(self.repo, "commit", "-m", "first")
        (self.repo / "file.txt").write_text("two\n", encoding="utf-8")
        git(self.repo, "add", "file.txt")
        git(self.repo, "commit", "-m", "second")

    def write_task_context(self, branch: str, worktree: Path) -> None:
        context_dir = self.repo / ".mneme"
        context_dir.mkdir(exist_ok=True)
        payload = {"branch": branch, "worktree": str(worktree)}
        (context_dir / "task_context.json").write_text(json.dumps(payload), encoding="utf-8")


class TestGuardEvaluation(GuardTestBase):
    def test_correct_branch_and_worktree_passes(self) -> None:
        state = check.gather_state(self.repo)
        self.assertEqual(check.evaluate(state, self.repo, "main"), [])

    def test_wrong_branch_fails(self) -> None:
        git(self.repo, "switch", "-c", "other-task")
        failures = check.evaluate(check.gather_state(self.repo), self.repo, "main")
        self.assertEqual(len(failures), 1)
        self.assertIn("branch mismatch", failures[0])
        self.assertIn("actual branch:   other-task", failures[0])

    def test_wrong_worktree_fails(self) -> None:
        elsewhere = Path(self._tmp.name) / "elsewhere"
        elsewhere.mkdir()
        failures = check.evaluate(check.gather_state(self.repo), elsewhere, "main")
        self.assertEqual(len(failures), 1)
        self.assertIn("worktree mismatch", failures[0])

    def test_detached_head_fails(self) -> None:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        ).stdout.strip()
        git(self.repo, "checkout", "--detach", head)
        failures = check.evaluate(check.gather_state(self.repo), self.repo, "main")
        self.assertEqual(len(failures), 1)
        self.assertIn("detached HEAD", failures[0])

    def test_not_a_git_repository_fails(self) -> None:
        empty = Path(self._tmp.name) / "empty"
        empty.mkdir()
        failures = check.evaluate(check.gather_state(empty), empty, "main")
        self.assertEqual(len(failures), 1)
        self.assertIn("not a git repository", failures[0])


class TestTaskContextResolution(GuardTestBase):
    def test_missing_file_returns_none(self) -> None:
        self.assertIsNone(check.load_task_context(self.repo))

    def test_reads_valid_file(self) -> None:
        self.write_task_context("feat/example", self.repo)
        self.assertEqual(
            check.load_task_context(self.repo),
            {"branch": "feat/example", "worktree": str(self.repo)},
        )

    def test_malformed_json_raises(self) -> None:
        context_dir = self.repo / ".mneme"
        context_dir.mkdir(exist_ok=True)
        (context_dir / "task_context.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            check.load_task_context(self.repo)

    def test_main_no_args_uses_context_file_passes(self) -> None:
        self.write_task_context("main", self.repo)
        self.assertEqual(check.main([], repo=self.repo), 0)

    def test_main_no_args_branch_mismatch_fails_closed(self) -> None:
        self.write_task_context("some/other-branch", self.repo)
        self.assertEqual(check.main([], repo=self.repo), 1)

    def test_main_no_args_without_context_file_fails_closed(self) -> None:
        self.assertEqual(check.main([], repo=self.repo), 1)

    def test_explicit_args_override_context_file(self) -> None:
        stale = Path(self._tmp.name) / "stale-wt"
        stale.mkdir()
        self.write_task_context("stale/branch", stale)
        self.assertEqual(
            check.main(["--expected-root", str(self.repo), "--expected-branch", "main"], repo=self.repo),
            0,
        )


class TestProvisioner(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(provisioner.slugify("feat/example-task"), "feat-example-task")
        self.assertEqual(provisioner.slugify("ci/pytest_merge_gate"), "ci-pytest-merge-gate")

    def test_git_calls_are_scoped_to_script_repo_root(self) -> None:
        """Regression: git calls must target the script's repo, not the caller's cwd."""
        with tempfile.TemporaryDirectory() as tmp:
            recorded = {}

            def fake_run(cmd, **kwargs):
                recorded["cwd"] = kwargs.get("cwd")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            original_run = provisioner.subprocess.run
            provisioner.subprocess.run = fake_run
            try:
                exit_code = provisioner.create_task_worktree(
                    "feat/regression", "origin/main", Path(tmp) / "wt"
                )
            finally:
                provisioner.subprocess.run = original_run
            self.assertEqual(exit_code, 0)
            self.assertIsNotNone(recorded["cwd"])
            self.assertEqual(Path(recorded["cwd"]).resolve(), REPO_ROOT.resolve())


if __name__ == "__main__":
    unittest.main()