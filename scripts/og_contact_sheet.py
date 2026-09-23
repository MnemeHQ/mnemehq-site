#!/usr/bin/env python3
"""Build the Task 11 Gate B visual QA contact sheet.

Produces an HTML page (referencing the already-staged PNGs under
site/og-staging/, NOT re-rendering anything) that shows each selected
card at three widths: 1200px (native), 552px (LinkedIn feed width), and
360px (the acceptance surface). A human reviews this page; the script
itself makes no pass/fail judgment.

Usage:
  python scripts/og_contact_sheet.py [--out PATH] [--staging DIR]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import og_manifest  # noqa: E402

MANIFEST = REPO / "site" / "og" / "cards.yaml"
CARD_NAME = "og-v2.png"


def load_records() -> list[dict]:
    raw = og_manifest.load(MANIFEST)
    return [og_manifest.resolve(rel, raw.get(rel), strict=True) for rel in sorted(raw)]


def build_groups(records: list[dict]) -> list[tuple[str, str, list[dict]]]:
    """Return [(group_title, note, [records])]."""
    groups: list[tuple[str, str, list[dict]]] = []

    # 1. One representative per family.
    fam_order = ["brand", "proof", "integration", "editorial", "comparison"]
    fam_pick = []
    seen = set()
    for r in records:
        if r["family"] in fam_order and r["family"] not in seen:
            fam_pick.append(r)
            seen.add(r["family"])
    fam_pick.sort(key=lambda r: fam_order.index(r["family"]))
    groups.append(("Five families (one representative each)", "", fam_pick))

    # 2. One editorial card per motif -- all eight, flag any that can't be found.
    motif_order = ["connected", "broken", "boundary", "branch",
                   "stack", "intersection", "propagation", "isolated"]
    motif_pick = []
    missing_motifs = []
    for m in motif_order:
        cand = next((r for r in records
                     if r["family"] == "editorial" and r.get("variant") != "hub"
                     and r["motif"] == m), None)
        if cand:
            motif_pick.append(cand)
        else:
            missing_motifs.append(m)
    note = (f"MISSING -- no card resolves to motif(s): {', '.join(missing_motifs)}"
             if missing_motifs else "")
    groups.append(("Eight motifs (one card each)", note, motif_pick))

    # 3. All tone:failure cards.
    failures = [r for r in records if r["tone"] == "failure"]
    groups.append((f"tone: failure ({len(failures)} cards, expect 8)", "", failures))

    # 4. All 9-10 word headlines.
    longh = [r for r in records if len(r["headline"].split()) >= 9]
    groups.append((f"Headlines of 9-10 words ({len(longh)} cards, expect 20)", "", longh))

    # 5. All hub cards.
    hubs = [r for r in records if r.get("variant") == "hub"]
    groups.append((f"variant: hub ({len(hubs)} cards, expect 8)", "", hubs))

    # 6. All brand cards.
    brands = [r for r in records if r["family"] == "brand"]
    groups.append((f"All brand cards ({len(brands)} cards, expect 15)", "", brands))

    return groups


PAGE_TOP = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>OG Card Gate B Contact Sheet</title>
<style>
  body { background:#0c0c0d; color:#e8e8ec; font-family: -apple-system, Segoe UI, sans-serif; padding: 24px; }
  h1 { font-size: 22px; }
  h2 { font-size: 17px; margin-top: 48px; border-bottom: 1px solid #2e2e34; padding-bottom: 8px; }
  .note { color: #ff5c7a; font-weight: 600; margin: 6px 0 16px; }
  .card { margin-bottom: 36px; border: 1px solid #222226; border-radius: 8px; padding: 16px; background: #141416; }
  .card .path { font-family: monospace; font-size: 13px; color: #a8a8b8; margin-bottom: 10px; word-break: break-all; }
  .meta { font-size: 12px; color: #88889a; margin-bottom: 10px; }
  .widths { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
  .widths figure { margin: 0; }
  .widths figcaption { font-size: 11px; color: #88889a; margin-top: 4px; text-align: center; }
  .widths img { display: block; border: 1px solid #2e2e34; background:#000; }
  .w1200 img { width: 1200px; max-width: 90vw; }
  .w552 img { width: 552px; }
  .w360 img { width: 360px; }
</style>
</head><body>
<h1>OG Card System -- Task 11 Gate B Visual QA Contact Sheet</h1>
<p>Each card below is shown at 1200px (native), 552px (LinkedIn feed width), and 360px (the acceptance surface).
Images reference the staged renders under <code>site/og-staging/</code> -- nothing here is re-rendered.</p>
<div class="note">KNOWN ISSUE (see task-11-report.md Section 4): the Step 1 render pipeline has a
stale-cache race that made 78% of staged cards byte-identical to a DIFFERENT page's card. The path
label under each image is correct; the card's headline/content may not be. Judge layout and
legibility here, not per-card copy correctness, until Step 1 is re-rendered with a fix.</div>
"""

PAGE_BOTTOM = "</body></html>\n"


def card_block(rec: dict, staging_rel: str) -> str:
    rel = rec["path"]
    img_path = f"{staging_rel}/{rel}{CARD_NAME}" if rel else f"{staging_rel}/{CARD_NAME}"
    label = rel or "(root)"
    fam = rec["family"]
    extra_bits = [f"family={fam}", f"tone={rec['tone']}", f"motif={rec['motif']}"]
    if rec.get("variant"):
        extra_bits.append(f"variant={rec['variant']}")
    extra_bits.append(f"headline_words={len(rec['headline'].split())}")
    meta = " | ".join(extra_bits)
    headline = rec["headline"]
    return f"""<div class="card">
  <div class="path">{label}</div>
  <div class="meta">{meta}</div>
  <div class="meta">headline: &ldquo;{headline}&rdquo;</div>
  <div class="widths">
    <figure class="w1200"><img src="{img_path}" loading="lazy"><figcaption>1200px (native)</figcaption></figure>
    <figure class="w552"><img src="{img_path}" loading="lazy"><figcaption>552px (LinkedIn)</figcaption></figure>
    <figure class="w360"><img src="{img_path}" loading="lazy"><figcaption>360px (acceptance)</figcaption></figure>
  </div>
</div>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / ".superpowers" / "sdd" /
                                          "2026-09-21-og-card-system" / "task-11-contact-sheet.html"))
    ap.add_argument("--staging", default="og-staging",
                     help="path (relative to the output file's directory, via site/) to the staged renders; "
                          "default assumes the contact sheet is opened with site/og-staging/ reachable")
    args = ap.parse_args(argv)

    records = load_records()
    groups = build_groups(records)

    out_path = Path(args.out)
    # Contact sheet lives under .superpowers/sdd/..., staged PNGs live under site/og-staging/.
    # Compute a relative path from the output file to the repo's site/og-staging directory.
    staging_dir = REPO / "site" / args.staging
    rel_staging = Path(
        __import__("os").path.relpath(staging_dir, out_path.parent)
    ).as_posix()

    html_parts = [PAGE_TOP]
    total_cards = 0
    for title, note, recs in groups:
        html_parts.append(f"<h2>{title}</h2>\n")
        if note:
            html_parts.append(f'<div class="note">{note}</div>\n')
        for r in recs:
            html_parts.append(card_block(r, rel_staging))
            total_cards += 1
    html_parts.append(PAGE_BOTTOM)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(html_parts), encoding="utf-8")
    print(f"Wrote {out_path} with {total_cards} card entries across {len(groups)} groups "
          f"(staged PNGs referenced at {rel_staging}/).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
