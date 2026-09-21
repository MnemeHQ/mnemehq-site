#!/usr/bin/env python3
"""One-shot seeder: build site/og/cards.yaml from the legacy og-*.html templates.

This is scaffolding for the editorial pass, not the editorial pass itself.
It extracts only what is mechanically extractable -- `.heading` and, for
non-Editorial families, `.subtitle` -- and writes one manifest record per
page it can confidently place. It never invents a family, a headline, an
`alt:`, a `tone:`, or a `lines:` break: those are human calls (see
task-7-decisions.md).

Deleted in a later task once the manifest is hand-completed. Safe to
re-run: output is fully deterministic (sorted keys, no derived/random
content), and each run replaces the file from the same legacy sources
rather than merging, so it never accumulates drift across runs.

Usage:
    python scripts/seed_og_manifest.py
"""
from __future__ import annotations

import html as html_mod
import importlib.util
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"
OUT = SITE / "og" / "cards.yaml"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import og_manifest  # noqa: E402


def _load_template_map() -> dict[str, str]:
    """Import TEMPLATE_MAP from generate_og_images.py without requiring
    playwright to be installed (its import is deferred inside that module's
    async function, so a plain module load is safe)."""
    path = Path(__file__).resolve().parent / "generate_og_images.py"
    spec = importlib.util.spec_from_file_location("_legacy_generate_og_images", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.TEMPLATE_MAP


# TEMPLATE_MAP still points at pre-restructure output paths for these three
# templates (a flat `for-cto/` etc. that today holds only a leftover og.png,
# no page). The live pages moved under `for/`. Everything else in
# TEMPLATE_MAP already points at a directory with an index.html.
PATH_CORRECTIONS = {
    "for-cto/": "for/cto/",
    "for-platform/": "for/platform/",
    "for-principal/": "for/principal-engineer/",
}

_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Primary shape, used by the large majority of templates.
_HEADING_RE = re.compile(r'<div class="heading"[^>]*>(.*?)</div>', re.DOTALL)
_SUBTITLE_RE = re.compile(r'<div class="subtitle"[^>]*>(.*?)</div>', re.DOTALL)

# Fallback shape used by a handful of older templates that predate the
# heading/subtitle/tag standardization (plain <h1>/<p>).
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL)
_P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL)


def _clean(fragment: str) -> str:
    """Strip markup from an extracted fragment down to plain text.

    `<br>` variants become a space (they abut words with no whitespace in
    the source, e.g. "matters<br>once"); other tags are dropped in place
    since they wrap inline text that already has surrounding whitespace.
    """
    text = _BR_RE.sub(" ", fragment)
    text = _TAG_RE.sub("", text)
    text = html_mod.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def extract_heading_subtitle(html: str) -> tuple[str | None, str | None]:
    """Return (headline, subtitle) plain text, or (None, None)/(_, None)
    when a template doesn't carry one. Tries the standard `.heading`/
    `.subtitle` shape first, then falls back to `<h1>`/`<p>` for the
    handful of pre-standardization templates."""
    m = _HEADING_RE.search(html)
    if m:
        headline = _clean(m.group(1))
        sub_m = _SUBTITLE_RE.search(html)
        subtitle = _clean(sub_m.group(1)) if sub_m else None
        return headline, subtitle

    m = _H1_RE.search(html)
    if not m:
        return None, None
    headline = _clean(m.group(1))
    sub_m = _P_RE.search(html)
    subtitle = _clean(sub_m.group(1)) if sub_m else None
    return headline, subtitle


def build_records() -> tuple[dict[str, dict], list[str]]:
    """Return (records keyed by page path, warnings)."""
    template_map = _load_template_map()
    records: dict[str, dict] = {}
    warnings: list[str] = []

    for template, output_rel in sorted(template_map.items()):
        template_path = SITE / template
        if not template_path.is_file():
            warnings.append(f"{template}: no such file, skipped")
            continue

        page_dir = output_rel.rsplit("/", 1)[0] if "/" in output_rel else ""
        page_rel = f"{page_dir}/" if page_dir else ""
        page_rel = PATH_CORRECTIONS.get(page_rel, page_rel)

        if not (SITE / page_rel / "index.html").is_file():
            warnings.append(f"{template}: maps to {page_rel!r}, which has no index.html, skipped")
            continue

        html = template_path.read_text(encoding="utf-8")
        headline, subtitle = extract_heading_subtitle(html)
        if headline is None:
            warnings.append(f"{template}: no .heading or <h1> found, skipped")
            continue

        record: dict = {"headline": headline}

        family = og_manifest.family_for_path(page_rel)
        # Only Editorial cards are confirmed headline + identity + motif,
        # nothing else. When family can't be derived yet (the seven paths
        # awaiting an explicit override), keep the subtitle rather than
        # guess it away.
        if subtitle and family != "editorial":
            record["sup"] = subtitle

        if page_rel in records:
            warnings.append(f"{template}: page {page_rel!r} already seeded by another template")
        records[page_rel] = record

    return records, warnings


def main() -> int:
    records, warnings = build_records()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "# CANDIDATE STATE -- seeded mechanically by scripts/seed_og_manifest.py\n"
            "# from the legacy site/og-*.html templates. The editorial pass (family\n"
            "# overrides, headline rewrites, tone: failure, alt: text) is PENDING\n"
            "# human review -- see .superpowers/sdd/2026-09-21-og-card-system/\n"
            "# task-7-decisions.md. Do not treat this file as final.\n"
        )
        yaml.dump(
            records,
            fh,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True,
            width=100,
        )

    print(f"seeded {len(records)} record(s) -> {OUT.relative_to(REPO)}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
