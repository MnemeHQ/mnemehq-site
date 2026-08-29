#!/usr/bin/env python3
"""Synchronize public Mneme core-install references from one version manifest.

Usage:
    python scripts/sync_core_version.py 0.7.0
    python scripts/sync_core_version.py --check
    python scripts/sync_core_version.py --self-test

The update command changes the manifest and every active `mneme-hq` install
command in site HTML and the repository README. Historical release notes are
deliberately out of scope. `--check` is run in CI to prevent a manual edit from
letting one page drift away from the manifest.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "scripts" / "core_version.json"
VERSION = re.compile(r"^\d+\.\d+\.\d+$")

# Matches `mneme-hq>=0.6.0`, its HTML-escaped equivalent, and optional extras.
VERSIONED_REQUIREMENT = re.compile(
    r"(?P<package>mneme-hq(?:\[[^\]\s\"']+\])?)(?P<operator>>=|&gt;=)(?P<version>\d+\.\d+\.\d+)"
)

# Matches only unpinned published install commands. A source checkout (`-e .`)
# and prose that names the distribution without an install command are ignored.
UNPINNED_INSTALL = re.compile(
    r"(?P<prefix>\b(?:(?:python(?:3)?\s+-m\s+)?pipx?|uv\s+pip)\s+install\s+)"
    r"(?P<quote>[\"']?)(?P<package>mneme-hq(?:\[[^\]]+\])?)(?P=quote)"
    # Do not match a requirement operator or longer package name, but allow an
    # HTML closing tag immediately after the package.
    r"(?P<suffix>(?=$|[\s\"'`,.;:!?)}\]])|(?=</))"
)


@dataclass(frozen=True)
class Manifest:
    package: str
    minimum_version: str


def load_manifest() -> Manifest:
    raw = json.loads(MANIFEST_PATH.read_bytes().decode("utf-8"))
    package = raw.get("package")
    version = raw.get("minimum_version")
    if package != "mneme-hq" or not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError(f"invalid core version manifest: {MANIFEST_PATH}")
    return Manifest(package=package, minimum_version=version)


def target_files() -> list[Path]:
    files = sorted((ROOT / "site").rglob("*.html"))
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    return files


def read_source(path: Path) -> str:
    """Read source without normalizing its line endings."""
    return path.read_bytes().decode("utf-8")


def write_source(path: Path, text: str) -> None:
    """Write source without changing its line-ending convention."""
    path.write_bytes(text.encode("utf-8"))


def replace_requirements(text: str, version: str) -> str:
    def replace_versioned(match: re.Match[str]) -> str:
        return f"{match.group('package')}{match.group('operator')}{version}"

    text = VERSIONED_REQUIREMENT.sub(replace_versioned, text)

    def replace_unpinned(match: re.Match[str]) -> str:
        quote = match.group("quote")
        return (
            f"{match.group('prefix')}{quote}{match.group('package')}"
            f">={version}{quote}{match.group('suffix')}"
        )

    return UNPINNED_INSTALL.sub(replace_unpinned, text)


def findings(version: str) -> list[str]:
    stale: list[str] = []
    for path in target_files():
        relative = path.relative_to(ROOT)
        text = read_source(path)
        for match in VERSIONED_REQUIREMENT.finditer(text):
            if match.group("version") != version:
                stale.append(f"{relative}: {match.group(0)}")
        for match in UNPINNED_INSTALL.finditer(text):
            stale.append(f"{relative}: unpinned {match.group(0)}")
    return stale


def write_manifest(version: str) -> None:
    MANIFEST_PATH.write_text(
        json.dumps({"package": "mneme-hq", "minimum_version": version}, indent=2) + "\n",
        encoding="utf-8",
    )


def synchronize(version: str) -> int:
    changed: list[Path] = []
    for path in target_files():
        before = read_source(path)
        after = replace_requirements(before, version)
        if after != before:
            write_source(path, after)
            changed.append(path.relative_to(ROOT))
    write_manifest(version)
    print(f"Core version set to {version}; updated {len(changed)} file(s).")
    for path in changed:
        print(f"  {path}")
    return 0


def self_test() -> int:
    version = "0.6.0"
    cases = {
        "pip install mneme-hq": "pip install mneme-hq>=0.6.0",
        'pipx install "mneme-hq"': 'pipx install "mneme-hq>=0.6.0"',
        'pip install "mneme-hq[langchain]"': 'pip install "mneme-hq[langchain]>=0.6.0"',
        'pipx install "mneme-hq&gt;=0.5.1"': 'pipx install "mneme-hq&gt;=0.6.0"',
    }
    failures = [
        source
        for source, expected in cases.items()
        if replace_requirements(source, version) != expected
    ]
    if failures:
        print("core version synchronizer self-test failed:")
        for source in failures:
            print(f"  {source}")
        return 1
    print(f"core version synchronizer self-test: OK ({len(cases)} cases)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="new minimum mneme-hq version (X.Y.Z)")
    parser.add_argument("--check", action="store_true", help="verify all active references match the manifest")
    parser.add_argument("--self-test", action="store_true", help="verify synchronizer matching behavior")
    args = parser.parse_args(argv)

    if args.self_test:
        if args.check or args.version:
            parser.error("--self-test cannot be combined with a version or --check")
        return self_test()

    if args.check == bool(args.version):
        parser.error("provide a version to synchronize, or use --check")

    if args.check:
        manifest = load_manifest()
        stale = findings(manifest.minimum_version)
        if stale:
            print(f"Core version reference drift from {manifest.minimum_version}:")
            for item in stale:
                print(f"  {item}")
            return 1
        print(f"Core version references: OK ({manifest.minimum_version})")
        return 0

    assert args.version is not None
    if not VERSION.fullmatch(args.version):
        parser.error("version must use X.Y.Z form, for example 0.7.0")
    return synchronize(args.version)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
