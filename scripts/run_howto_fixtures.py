#!/usr/bin/env python3
"""Replay every how-to guide fixture against the installed `mneme` release.

Each guide under site/docs/how-to/<slug>/ has a fixture at tests/howto/<slug>/:

    steps.yaml         ordered shell steps (name, run, optional expect_exit)
    expected/<name>.txt  normalized stdout+stderr of that step, then `exit=<n>`
    docs/, inputs/, ... any files the steps need

The fixture directory is copied to a temporary directory and the steps run
there in order, in one shared working directory, under bash. Output is
normalized (CRLF, Windows path separators, the temp path) and compared to the
expected file. A guide's code blocks are checked against these files by
scripts/check_howto.py, so a guide cannot show a command or an output the
released package does not produce.

Usage:
    python scripts/run_howto_fixtures.py              # replay all, exit 1 on drift
    python scripts/run_howto_fixtures.py --only SLUG  # one guide
    python scripts/run_howto_fixtures.py --update     # rewrite expected/ (operator only)
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "howto"

# A backslash between two path characters is a Windows separator. A backslash
# before a newline is a shell line continuation and must survive.
_WIN_SEP = re.compile(r"(?<=[\w.])\\(?=[\w.])")

# Deterministic git identity and line endings, so steps that commit behave the
# same on a developer laptop and on the CI runner.
_GIT_ENV = {
    "GIT_AUTHOR_NAME": "Mneme Docs",
    "GIT_AUTHOR_EMAIL": "docs@mnemehq.com",
    "GIT_COMMITTER_NAME": "Mneme Docs",
    "GIT_COMMITTER_EMAIL": "docs@mnemehq.com",
    "GIT_CONFIG_COUNT": "2",
    "GIT_CONFIG_KEY_0": "core.autocrlf",
    "GIT_CONFIG_VALUE_0": "false",
    "GIT_CONFIG_KEY_1": "init.defaultBranch",
    "GIT_CONFIG_VALUE_1": "main",
}


class StepResult(NamedTuple):
    name: str
    ok: bool
    diff: str


def normalize(text: str, tmp: str) -> str:
    text = text.replace("\r\n", "\n")
    for variant in {tmp, tmp.replace("\\", "/")}:
        text = text.replace(variant, "<tmp>")
    return _WIN_SEP.sub("/", text)


def _bash() -> str:
    found = shutil.which("bash")
    if not found:
        raise SystemExit("run_howto_fixtures: bash is required")
    return found


def load_steps(fixture_dir: Path) -> list[dict]:
    data = yaml.safe_load((fixture_dir / "steps.yaml").read_text(encoding="utf-8"))
    return data["steps"]


def run_fixture(fixture_dir: Path, update: bool = False) -> list[StepResult]:
    results: list[StepResult] = []
    env = {**os.environ, **_GIT_ENV, "PYTHONIOENCODING": "utf-8"}
    with tempfile.TemporaryDirectory(prefix="howto-") as tmp:
        work = Path(tmp) / "repo"
        shutil.copytree(
            fixture_dir, work, ignore=shutil.ignore_patterns("expected", "manual", "steps.yaml")
        )
        for step in load_steps(fixture_dir):
            name, cmd = step["name"], step["run"]
            want_exit = int(step.get("expect_exit", 0))
            proc = subprocess.run(
                [_bash(), "-c", cmd],
                cwd=work,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            got = normalize(proc.stdout, str(work.parent)) + f"exit={proc.returncode}\n"
            expected_path = fixture_dir / "expected" / f"{name}.txt"
            if update:
                expected_path.parent.mkdir(parents=True, exist_ok=True)
                expected_path.write_text(got, encoding="utf-8", newline="\n")
            want = (
                expected_path.read_text(encoding="utf-8").replace("\r\n", "\n")
                if expected_path.exists()
                else ""
            )
            problems = []
            if proc.returncode != want_exit:
                problems.append(f"expected exit {want_exit}, got {proc.returncode}")
            if got != want:
                problems.extend(
                    difflib.unified_diff(
                        want.splitlines(), got.splitlines(), "expected", "actual", lineterm=""
                    )
                )
            results.append(StepResult(name, not problems, "\n".join(problems)))
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="replay one guide's fixture")
    ap.add_argument("--update", action="store_true", help="rewrite expected/ outputs")
    args = ap.parse_args()

    dirs = sorted(p for p in FIXTURES.iterdir() if (p / "steps.yaml").exists())
    if args.only:
        dirs = [d for d in dirs if d.name == args.only]
        if not dirs:
            print(f"run_howto_fixtures: no fixture named {args.only}")
            return 1

    failed = 0
    for d in dirs:
        for r in run_fixture(d, update=args.update):
            status = "ok  " if r.ok else "FAIL"
            print(f"{status} {d.name} :: {r.name}")
            if not r.ok:
                failed += 1
                print("\n".join("     " + line for line in r.diff.splitlines()))
    print(f"run_howto_fixtures: {failed} failing step(s) across {len(dirs)} fixture(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
