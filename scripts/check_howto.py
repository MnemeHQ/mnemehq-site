#!/usr/bin/env python3
"""Validate every how-to guide against its fixture and the guide template.

For each site/docs/how-to/<slug>/index.html this checks:

1. The template sections exist, in order (SECTIONS below), as
   <section id="..."> elements.
2. The meta strip says "Tested with mneme-hq <version>" and the version is the
   one in scripts/core_version.json.
3. The hero carries a "You'll end up with:" line.
4. Every <pre> inside a checked section declares data-fixture, and its text
   matches the fixture at tests/howto/<slug>/:
     data-fixture="cmd"          each non-comment line is a step `run` command
     data-fixture="file:<path>"  the block equals that fixture file
     data-fixture="out:<step>"   the block is a contiguous part of
                                 expected/<step>.txt
5. The guide is in site/sitemap.xml and linked from the /docs/how-to/ hub.

Prose accuracy is out of scope: the adversarial review before merge covers it.

Usage:
    python scripts/check_howto.py   # exit 0 when every guide passes, 1 otherwise
"""
from __future__ import annotations

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
FIXTURES = ROOT / "tests" / "howto"

SECTIONS = (
    "goal",
    "prerequisites",
    "configure",
    "run",
    "expected-result",
    "evidence",
    "troubleshooting",
    "limits",
    "next",
)
CHECKED_SECTIONS = {"configure", "run", "expected-result", "evidence"}

_TESTED = re.compile(r"Tested with mneme-hq (\d+\.\d+\.\d+)")
_END_UP = re.compile(r"You(?:'|’)ll end up with:")


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.section_ids: list[str] = []
        self.blocks: list[tuple[str | None, str | None, str]] = []  # section, fixture, text
        self.text: list[str] = []
        self._section: str | None = None
        self._depth = 0
        self._pre: str | None = None
        self._pre_attr: str | None = None
        self._pre_buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            if self._section is None and a.get("id") in SECTIONS:
                self._section = a["id"]
                self._depth = 0
                self.section_ids.append(a["id"])
            elif self._section is not None:
                self._depth += 1
        elif tag == "pre":
            self._pre = self._section or ""
            self._pre_attr = a.get("data-fixture")
            self._pre_buf = []

    def handle_endtag(self, tag):
        if tag == "section" and self._section is not None:
            if self._depth == 0:
                self._section = None
            else:
                self._depth -= 1
        elif tag == "pre" and self._pre is not None:
            self.blocks.append((self._pre or None, self._pre_attr, "".join(self._pre_buf)))
            self._pre = None

    def handle_data(self, data):
        self.text.append(data)
        if self._pre is not None:
            self._pre_buf.append(data)


def _join_continuations(text: str) -> list[str]:
    joined = re.sub(r"\\\n\s*", " ", text.replace("\r\n", "\n"))
    return [" ".join(line.split()) for line in joined.split("\n")]


def _clean(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    return "\n".join(lines).strip("\n")


def _step_lines(fixture: Path) -> set[str]:
    data = yaml.safe_load((fixture / "steps.yaml").read_text(encoding="utf-8"))
    lines: set[str] = set()
    for step in data["steps"]:
        run = step["run"]
        lines.add(" ".join(run.split()))
        lines.update(line for line in _join_continuations(run) if line)
    return lines


def _check_block(fixture: Path, attr: str, text: str, step_lines: set[str]) -> str | None:
    if attr == "cmd":
        for line in _join_continuations(text):
            if line and not line.startswith("#") and line not in step_lines:
                return f'command not in fixture steps.yaml: "{line}"'
        return None
    kind, _, ref = attr.partition(":")
    if kind == "file":
        path = fixture / ref
        if not path.is_file():
            return f"data-fixture file:{ref} does not exist in the fixture"
        if _clean(text) != _clean(path.read_text(encoding="utf-8")):
            return f"block differs from fixture file {ref}"
        return None
    if kind == "out":
        path = fixture / "expected" / f"{ref}.txt"
        if not path.is_file():
            return f"data-fixture out:{ref} has no expected/{ref}.txt"
        if _clean(text) not in _clean(path.read_text(encoding="utf-8")):
            return f"block is not part of the recorded output out:{ref}"
        return None
    return f'unknown data-fixture value "{attr}"'


def check_page(page: Path, fixture: Path, version: str, site: Path = SITE) -> list[str]:
    errors: list[str] = []
    slug = page.parent.name
    parser = _Page()
    parser.feed(page.read_text(encoding="utf-8"))
    full_text = html.unescape("".join(parser.text))

    missing = [s for s in SECTIONS if s not in parser.section_ids]
    for s in missing:
        errors.append(f'section id="{s}" is missing')
    present = [s for s in parser.section_ids if s in SECTIONS]
    if not missing and present != list(SECTIONS):
        errors.append(f"sections out of order: {present}")

    tested = _TESTED.search(full_text)
    if not tested:
        errors.append('meta strip has no "Tested with mneme-hq X.Y.Z"')
    elif tested.group(1) != version:
        errors.append(f"tested version {tested.group(1)} does not match core_version.json {version}")

    if not _END_UP.search(full_text):
        errors.append("hero has no \"You'll end up with:\" line")

    if not (fixture / "steps.yaml").is_file():
        errors.append(f"no fixture at {fixture}")
        return errors
    step_lines = _step_lines(fixture)
    for section, attr, text in parser.blocks:
        if attr is None:
            if section in CHECKED_SECTIONS:
                errors.append(f'<pre> in #{section} has no data-fixture attribute')
            continue
        problem = _check_block(fixture, attr, text, step_lines)
        if problem:
            errors.append(f"#{section} [{attr}]: {problem}")

    url = f"https://mnemehq.com/docs/how-to/{slug}/"
    if url not in (site / "sitemap.xml").read_text(encoding="utf-8"):
        errors.append(f"{url} is not in sitemap.xml")
    hub = site / "docs" / "how-to" / "index.html"
    if f'href="/docs/how-to/{slug}/"' not in hub.read_text(encoding="utf-8"):
        errors.append("guide is not linked from the /docs/how-to/ hub")
    return errors


def main() -> int:
    version = json.loads((ROOT / "scripts" / "core_version.json").read_text())["minimum_version"]
    pages = sorted((SITE / "docs" / "how-to").glob("*/index.html"))
    failed = 0
    for page in pages:
        errors = check_page(page, FIXTURES / page.parent.name, version)
        rel = page.relative_to(ROOT).as_posix()
        if errors:
            failed += 1
            print(f"FAIL {rel}")
            for e in errors:
                print(f"     {e}")
        else:
            print(f"ok   {rel}")
    print(f"check_howto: {failed} failing guide(s) of {len(pages)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
