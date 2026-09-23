#!/usr/bin/env python3
"""House-voice lint for the OG card manifest.

Two patterns keep creeping into copy that this lint exists to catch:

  - "bottleneck": a word the house style has ruled out as a crutch.
  - the em dash (U+2014) used as a connective in a sentence: the house
    style writes short clauses instead. This is NOT a ban on all dashes --
    the en dash (U+2013, used in ranges like "2024-2026") and the plain
    hyphen are untouched; only U+2014 is a violation.

`findings(record)` is the pure, testable core -- it reads every field with
`.get()`, never `[]`, because callers (including the tests) legitimately
pass sparse records that do not carry every key.

Escape hatch: a truthy `voice_ok` on a record suppresses all of that
record's findings. This exists because some copy legitimately quotes an
external source (e.g. a report title) that happens to contain a banned
token, and a regex cannot tell a quoted title from house prose. `voice_ok`
is a short list of reasons, reviewed same as the copy it excuses -- it is
not a way to silence the lint, it is a documented, per-record exception.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import og_manifest

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "site" / "og" / "cards.yaml"

BOTTLENECK_RE = re.compile(r"\bbottleneck\b", re.IGNORECASE)
EM_DASH = "—"  # U+2014 only -- not U+2013 (en dash) or "-" (hyphen).

_SCALAR_FIELDS = ("headline", "sup", "alt", "subtitle", "badge", "name")


def _check_text(label: str, text: str) -> list[str]:
    out = []
    if BOTTLENECK_RE.search(text):
        out.append(f"{label}: contains 'bottleneck': {text!r}")
    if EM_DASH in text:
        out.append(f"{label}: contains an em dash (U+2014): {text!r}")
    return out


def _check_field(out: list[str], label: str, value: object) -> None:
    if isinstance(value, str) and value:
        out.extend(_check_text(label, value))


def findings(record: dict) -> list[str]:
    """Return house-voice violations for one resolved (or raw) record.

    Structured fields render copy on the card face exactly like the scalar
    ones do, so they get walked too: every string in a `rows` triple (the
    proof family), every `label`/`value`/`verdict` in a `boxes` entry (the
    comparison family), and every `text` in a `chain` pill (the integration
    family). The `kind` discriminator in each of those is an enum value,
    not prose, so it is deliberately skipped.
    """
    if record.get("voice_ok"):
        return []

    out: list[str] = []
    for field in _SCALAR_FIELDS:
        _check_field(out, field, record.get(field))

    # rows (proof): [label, value, kind] triples, or a legacy flat
    # list/dict of strings -- kind (index 2) is never checked.
    rows = record.get("rows")
    if isinstance(rows, list):
        for i, row in enumerate(rows):
            if isinstance(row, str):
                _check_field(out, f"rows[{i}]", row)
            elif isinstance(row, (list, tuple)):
                for j, value in enumerate(row[:2]):
                    _check_field(out, f"rows[{i}][{j}]", value)
    elif isinstance(rows, dict):
        for key, value in rows.items():
            _check_field(out, f"rows[{key}]", value)

    # boxes (comparison): {label, value, verdict, kind} mappings.
    boxes = record.get("boxes")
    if isinstance(boxes, list):
        for i, box in enumerate(boxes):
            if isinstance(box, dict):
                for key in ("label", "value", "verdict"):
                    _check_field(out, f"boxes[{i}].{key}", box.get(key))

    # chain (integration): {text, kind} pills.
    chain = record.get("chain")
    if isinstance(chain, list):
        for i, item in enumerate(chain):
            if isinstance(item, dict):
                _check_field(out, f"chain[{i}].text", item.get("text"))

    return out


def main() -> int:
    manifest = og_manifest.load(MANIFEST)
    errors: list[str] = []

    for rel, raw in sorted(manifest.items()):
        for finding in findings(raw or {}):
            errors.append(f"{rel or '<home>'}: {finding}")

    for e in errors:
        print(f"ERROR -- {e}")

    if errors:
        print(f"{len(errors)} house-voice issue(s) found")
        return 1
    print(f"OK -- {len(manifest)} record(s), 0 house-voice issue(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
