"""Tests for scripts/run_howto_fixtures.py."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_howto_fixtures import normalize, run_fixture  # noqa: E402


def _fixture(tmp_path: Path, cmd: str, expected: str, exit_code: int) -> Path:
    d = tmp_path / "fx"
    (d / "expected").mkdir(parents=True)
    (d / "steps.yaml").write_text(
        textwrap.dedent(
            f"""
            steps:
              - name: s1
                run: {cmd}
                expect_exit: {exit_code}
            """
        ),
        encoding="utf-8",
    )
    (d / "expected" / "s1.txt").write_text(expected, encoding="utf-8")
    return d


def test_matching_output_passes(tmp_path):
    d = _fixture(tmp_path, "echo 1", "1\nexit=0\n", 0)
    assert all(r.ok for r in run_fixture(d))


def test_output_drift_fails_with_diff(tmp_path):
    d = _fixture(tmp_path, "echo 2", "1\nexit=0\n", 0)
    [r] = run_fixture(d)
    assert not r.ok
    assert "-1" in r.diff and "+2" in r.diff


def test_wrong_exit_code_fails(tmp_path):
    d = _fixture(tmp_path, "exit 2", "exit=2\n", 0)
    [r] = run_fixture(d)
    assert not r.ok
    assert "expected exit 0" in r.diff


def test_steps_share_one_working_directory(tmp_path):
    d = tmp_path / "fx"
    (d / "expected").mkdir(parents=True)
    (d / "steps.yaml").write_text(
        "steps:\n"
        "  - name: write\n"
        "    run: echo hi > note.txt\n"
        "  - name: read\n"
        "    run: cat note.txt\n",
        encoding="utf-8",
    )
    (d / "expected" / "write.txt").write_text("exit=0\n", encoding="utf-8")
    (d / "expected" / "read.txt").write_text("hi\nexit=0\n", encoding="utf-8")
    assert all(r.ok for r in run_fixture(d))


def test_fixture_files_are_copied_not_mutated(tmp_path):
    d = _fixture(tmp_path, "echo changed > steps.yaml", "exit=0\n", 0)
    before = (d / "steps.yaml").read_text(encoding="utf-8")
    run_fixture(d)
    assert (d / "steps.yaml").read_text(encoding="utf-8") == before


def test_normalize_rewrites_known_windows_paths_and_keeps_continuations():
    raw = "Created .mneme\\project_memory.json\n  mneme add_decision \\\n      --id x\r\n"
    paths = (".mneme", ".mneme/project_memory.json")
    assert normalize(raw, "/tmp/x", paths) == (
        "Created .mneme/project_memory.json\n  mneme add_decision \\\n      --id x\n"
    )


def test_normalize_leaves_json_escapes_alone():
    raw = '{"reason": "violated\\n  path: app\\handlers"}\n'
    assert normalize(raw, "/tmp/x", ("app", "app/handlers")) == (
        '{"reason": "violated\\n  path: app/handlers"}\n'
    )


def test_step_output_paths_are_normalized_end_to_end(tmp_path):
    d = tmp_path / "fx"
    (d / "expected").mkdir(parents=True)
    (d / "sub").mkdir()
    (d / "sub" / "f.txt").write_text("x", encoding="utf-8")
    (d / "steps.yaml").write_text("steps:\n  - name: s\n    run: echo 'sub\\f.txt'\n", encoding="utf-8")
    (d / "expected" / "s.txt").write_text("sub/f.txt\nexit=0\n", encoding="utf-8")
    assert all(r.ok for r in run_fixture(d))


def test_normalize_hides_the_temporary_directory():
    assert normalize("cwd is /tmp/abc123/repo\n", "/tmp/abc123") == "cwd is <tmp>/repo\n"
