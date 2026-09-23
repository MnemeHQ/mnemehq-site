#!/usr/bin/env python3
"""One-shot: restore the `accent:` key the seeder dropped.

Defect: the seeder (seed_og_manifest.py) extracted `.heading` as plain
text, discarding which phrase was wrapped in `<em>...</em>` in the legacy
`site/og-*.html` template. That phrase is the italic sage accent -- the
brand device of this card system -- and 76+ records shipped without one.

This script re-extracts the `<em>` phrase from each legacy template's
`.heading` div, maps template -> page path via
generate_og_images.TEMPLATE_MAP, and adds `accent:` to exactly the
records that are missing one.

Hard rules (see task brief):
  - Never touches `headline`.
  - Never overwrites an existing `accent`.
  - Never adds `accent` to a `variant: hub` record.
  - Only adds an accent that is an exact substring of the record's
    current headline after HTML-unescaping + whitespace normalisation
    (the same normalisation the seeder used). Anything else is skipped
    and reported, never forced.

Edits site/og/cards.yaml with a surgical text insertion rather than a
full yaml.dump round-trip, so every untouched record stays byte-for-byte
identical (a full re-dump reformats unrelated flow-style lists, e.g.
`voice_ok: [...]` -> block style, which would bloat the diff).

Usage:
    python scripts/backfill_og_accents.py --dry-run
    python scripts/backfill_og_accents.py
"""
from __future__ import annotations

import argparse
import html as html_mod
import importlib.util
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
MANIFEST = SITE / "og" / "cards.yaml"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import og_manifest  # noqa: E402


def _load_template_map() -> dict[str, str]:
    """Import TEMPLATE_MAP from generate_og_images.py without requiring
    playwright to be installed (its import is deferred inside that
    module's async function, so a plain module load is safe)."""
    path = Path(__file__).resolve().parent / "generate_og_images.py"
    spec = importlib.util.spec_from_file_location("_legacy_generate_og_images", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.TEMPLATE_MAP


# Same corrections seed_og_manifest.py applies: TEMPLATE_MAP still points at
# pre-restructure output paths for these three templates.
PATH_CORRECTIONS = {
    "for-cto/": "for/cto/",
    "for-platform/": "for/platform/",
    "for-principal/": "for/principal-engineer/",
}

_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_HEADING_RE = re.compile(r'<div class="heading"[^>]*>(.*?)</div>', re.DOTALL)
_EM_RE = re.compile(r"<em>(.*?)</em>", re.DOTALL)


def _clean(fragment: str) -> str:
    """Same cleaning seed_og_manifest.py's `_clean` does: `<br>` -> space,
    strip remaining tags, unescape entities, collapse whitespace."""
    text = _BR_RE.sub(" ", fragment)
    text = _TAG_RE.sub("", text)
    text = html_mod.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def _norm(text: str) -> str:
    """Whitespace-insensitive comparison key (matches og_manifest._norm)."""
    return re.sub(r"\s+", " ", text).strip()


def extract_accent(html: str) -> str | None:
    """Return the cleaned `<em>` phrase from the template's `.heading` div,
    or None if there is no `.heading` or no `<em>` inside it.

    Deliberately scoped to `.heading` only (not the `<h1>` fallback shape a
    handful of pre-standardization templates use) -- that's the shape the
    reported defect names, and the one the Gate A audit's 83-template count
    was verified against.
    """
    m = _HEADING_RE.search(html)
    if not m:
        return None
    em = _EM_RE.search(m.group(1))
    if not em:
        return None
    return _clean(em.group(1))


def page_rel_for(output_rel: str) -> str:
    page_dir = output_rel.rsplit("/", 1)[0] if "/" in output_rel else ""
    page_rel = f"{page_dir}/" if page_dir else ""
    return PATH_CORRECTIONS.get(page_rel, page_rel)


def plan() -> tuple[dict[str, str], list[str]]:
    """Return ({page_rel: accent to add}, [skip reasons])."""
    template_map = _load_template_map()
    raw = og_manifest.load(MANIFEST)

    to_add: dict[str, str] = {}
    skipped: list[str] = []

    for template, output_rel in sorted(template_map.items()):
        template_path = SITE / template
        if not template_path.is_file():
            continue
        page_rel = page_rel_for(output_rel)
        if not (SITE / page_rel / "index.html").is_file():
            continue

        html = template_path.read_text(encoding="utf-8")
        accent = extract_accent(html)
        if accent is None:
            continue  # nothing to backfill for this template

        record = raw.get(page_rel)
        if record is None:
            skipped.append(f"{page_rel!r}: no manifest record for this page (extracted {accent!r})")
            continue
        if not isinstance(record, dict):
            skipped.append(f"{page_rel!r}: manifest record is not a mapping, skipped")
            continue

        if record.get("variant") == "hub":
            skipped.append(f"{page_rel!r}: variant: hub -- no accent added by rule (extracted {accent!r})")
            continue

        if record.get("accent"):
            skipped.append(f"{page_rel!r}: already has accent {record['accent']!r}, left untouched")
            continue

        headline = record.get("headline")
        if not headline:
            skipped.append(f"{page_rel!r}: record has no headline, skipped")
            continue

        if accent not in _norm(headline):
            skipped.append(
                f"{page_rel!r}: extracted accent {accent!r} is not an exact substring of "
                f"headline {headline!r}, skipped")
            continue

        to_add[page_rel] = accent

    return to_add, skipped


def _accent_line(value: str) -> str:
    """Render `accent: <value>` the way pyyaml's block dumper would
    (plain scalar unless quoting is required), with no trailing newline."""
    dumped = yaml.safe_dump({"accent": value}, default_flow_style=False,
                             allow_unicode=True, width=100)
    return dumped.rstrip("\n")


def _apply(to_add: dict[str, str]) -> None:
    """Insert `accent:` as the first key of each named record.

    `accent` sorts before every other key this manifest uses (alt, family,
    headline, lines, motif, rows, subtitle, sup, tone, variant, voice_ok),
    so inserting it first keeps every record's key order exactly what a
    fresh sort_keys=True dump would produce.
    """
    with open(MANIFEST, encoding="utf-8", newline="") as fh:
        text = fh.read()
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    remaining = dict(to_add)

    while i < n:
        line = lines[i]

        if "" in remaining and line == "? ''":
            # Homepage: explicit-key form. `: headline: ...` becomes
            # `:\n  accent: ...\n  headline: ...` -- still one block
            # mapping, just with its first entry moved to its own line.
            out.append(line)
            i += 1
            value_line = lines[i]
            assert value_line.startswith(": "), value_line
            accent_line = _accent_line(remaining.pop(""))
            out.append(":")
            out.append(f"  {accent_line}")
            out.append(f"  {value_line[2:]}")
            i += 1
            continue

        for page_rel in list(remaining):
            if page_rel and line == f"{page_rel}:":
                out.append(line)
                accent_line = _accent_line(remaining.pop(page_rel))
                out.append(f"  {accent_line}")
                break
        else:
            out.append(line)

        i += 1

    if remaining:
        raise RuntimeError(f"could not locate these records in {MANIFEST}: {sorted(remaining)}")

    with open(MANIFEST, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(out))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                     help="report what would change without writing cards.yaml")
    args = ap.parse_args()

    to_add, skipped = plan()

    if args.dry_run:
        print(f"would add {len(to_add)} accent(s)")
    else:
        _apply(to_add)
        print(f"added {len(to_add)} accent(s)")

    for page_rel, accent in sorted(to_add.items()):
        print(f"  {page_rel or '<home>'}: accent={accent!r}")

    if skipped:
        print(f"\n{len(skipped)} skipped:")
        for s in sorted(skipped):
            print(f"  {s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
