#!/usr/bin/env python3
"""Render OG cards from site/og/cards.yaml.

Rendering is pinned. An unpinned browser makes "deterministic" cards
produce pixel diffs whenever Chromium changes underneath them, which is
how a regenerate-and-diff gate turns into noise.

Usage:
  python scripts/render_og.py --strict --out site
  python scripts/render_og.py --strict --dry-run
  python scripts/render_og.py --only insights/rag-is-not-memory/
"""
from __future__ import annotations

import argparse
import asyncio
import functools
import html as html_mod
import sys
from pathlib import Path

import og_geometry
import og_manifest

REPO = Path(__file__).resolve().parent.parent
TPL = REPO / "templates" / "og"
MANIFEST = REPO / "site" / "og" / "cards.yaml"
CARD_NAME = "og-v2.png"          # PUBLISHING.md:105 -- never overwrite og.png
WIDTH, HEIGHT = 1200, 630
PLAYWRIGHT_PIN = "1.58.0"
CHROMIUM_PIN = "145.0.7632.6"
TYPE_FLOOR = 30


def label_for(record: dict) -> str:
    """Category label. Editorial resolves from the PATH, not the family:
    one family carries two labels (INSIGHT / CONCEPT), so a family-keyed
    dict cannot express it. Brand cards carry the identity alone.

    Hub cards (editorial listing pages) also carry the identity alone: the
    subtitle is already the descriptor, so a category label in the top bar
    would duplicate it (e.g. "INSIGHT" in the top bar and "INSIGHTS" again
    as the hub subtitle)."""
    fam, path = record["family"], record["path"]
    if fam == "brand":
        return ""
    if record.get("variant") == "hub":
        return ""
    if fam == "editorial":
        return "Concept" if path.startswith("concepts/") else "Insight"
    return {"integration": "Integration", "comparison": "Comparison",
            "proof": "Demo"}[fam]


def fit(lines: list[str]) -> int:
    """Size on the LONGEST LINE so a deliberate break never shrinks the card."""
    n = max((len(x) for x in lines), default=0)
    size = 94 if n <= 38 else 78 if n <= 62 else 70 if n <= 92 else 61
    assert size >= TYPE_FLOOR, f"{size}px is below the {TYPE_FLOOR}px type floor"
    return size


def _lines_html(lines: list[str], accent: str | None) -> str:
    esc = [html_mod.escape(x) for x in lines]
    out = "<br>".join(esc)
    if accent:
        a = html_mod.escape(accent)
        out = out.replace(a, f"<em>{a}</em>", 1)
    return out


# ---------------------------------------------------------------------------
# Structured-family builders. Markup reproduced faithfully from the
# owner-approved reference at
# .superpowers/sdd/2026-09-21-og-card-system/approved-mockup-reference.py
# (_ROW, _BOX, _PILL, _ARROW and the CARDS["2-proof"] / ["3-integration"] /
# ["5-compare"] entries). Do not redesign.
# ---------------------------------------------------------------------------

_ROW = ('<div style="display:flex;align-items:center;gap:30px;background:{bg};border:2px solid {bd};'
        'border-left:8px solid {ac};border-radius:10px;padding:26px 34px">'
        '<span style="font-family:\'DM\';font-size:36px;font-weight:500;color:{ac};'
        'letter-spacing:.06em;min-width:220px">{k}</span>'
        '<span style="font-family:\'IN\';font-size:48px;color:{tc};font-weight:600;'
        'letter-spacing:-.6px">{v}</span></div>')

_ROW_STYLES = {
    "held": dict(bg="var(--surface)", bd="var(--border2)", ac="var(--accent)", tc="var(--text)"),
    "neutral": dict(bg="var(--surface)", bd="var(--border)", ac="var(--quiet)", tc="var(--muted)"),
    "denied": dict(bg="rgba(255,92,122,.08)", bd="rgba(255,92,122,.34)",
                   ac="var(--error)", tc="var(--text)"),
}

_BOX = ('<div style="flex:1;background:{bg};border:2px solid {bd};border-radius:12px;padding:30px 34px">'
        '<div style="font-family:\'DM\';font-size:36px;font-weight:500;color:{lc};'
        'letter-spacing:.06em;margin-bottom:20px">{label}</div>'
        '<div style="font-family:\'IN\';font-size:50px;color:{vc};font-weight:600;'
        'letter-spacing:-.6px;margin-bottom:22px">{value}</div>'
        '<div style="font-family:\'DM\';font-size:36px;font-weight:500;color:{lc};'
        'letter-spacing:.04em">{verdict}</div></div>')

_BOX_STYLES = {
    "warn": dict(bg="var(--surface)", bd="var(--border2)", lc="var(--warn)", vc="var(--muted)"),
    "accent": dict(bg="var(--surface)", bd="rgba(181,204,122,.36)", lc="var(--accent)", vc="var(--text)"),
}

_PILL = ('<span style="font-family:\'DM\';font-size:36px;font-weight:500;color:{c};'
         'border:2px solid {b};background:{bg};border-radius:8px;padding:14px 24px;'
         'letter-spacing:.04em;white-space:nowrap">{t}</span>')
_ARROW = ('<span style="font-family:\'DM\';font-size:40px;color:var(--quiet);'
          'padding:0 6px;line-height:1">&rarr;</span>')

_PILL_STYLES = {
    "plain": dict(c="var(--text)", b="var(--border2)", bg="var(--surface)"),
    "accent": dict(c="var(--accent)", b="rgba(181,204,122,.42)", bg="rgba(181,204,122,.08)"),
}


def _rows_html(rows: list) -> str:
    parts = []
    for label, value, kind in rows:
        style = _ROW_STYLES[kind]
        parts.append(_ROW.format(k=html_mod.escape(label), v=html_mod.escape(value), **style))
    return "".join(parts)


def _boxes_html(boxes: list) -> str:
    parts = []
    for box in boxes:
        style = _BOX_STYLES[box["kind"]]
        parts.append(_BOX.format(
            label=html_mod.escape(box["label"]),
            value=html_mod.escape(box["value"]),
            verdict=html_mod.escape(box["verdict"]),
            **style))
    return "".join(parts)


def _chain_html(chain: list) -> str:
    parts = []
    for i, item in enumerate(chain):
        if i:
            parts.append(_ARROW)
        style = _PILL_STYLES[item["kind"]]
        parts.append(_PILL.format(t=html_mod.escape(item["text"]), **style))
    return "".join(parts)


# Dev-only fallback for a structured family missing its required fields.
# Never a production success path: `og_manifest.resolve(strict=True)`
# raises before build_html ever sees such a record, so this branch is only
# reachable in non-strict/local-preview runs. It reuses the generic
# headline+sup tokens so it needs no family-specific data.
_FALLBACK_TPL = (
    '<!DOCTYPE html><html><head><meta charset="utf-8">\n'
    '<link rel="stylesheet" href="_base.css"></head>\n'
    '<body>\n'
    '<div class="frame">\n'
    '  <div class="top"><span class="id">Mneme HQ</span>'
    '<span class="fam">{{family_label}}</span><span class="rule"></span></div>\n'
    '  <div class="body" style="max-width:668px">'
    '<h1 style="font-size:{{headline_px}}px">{{lines_html}}</h1>'
    '<div class="sup" style="margin-top:28px;color:var(--muted)">{{sup}}</div></div>\n'
    '</div>\n'
    '</body></html>'
)


def build_html(record: dict) -> str:
    family = record["family"]
    is_hub = record.get("variant") == "hub"
    geometry = ""
    # Hub cards render no geometry: "no motif pretending it is an article."
    if family == "editorial" and not is_hub:
        geometry = og_geometry.render(
            record["path"].rstrip("/").rsplit("/", 1)[-1],
            record["motif"], record["tone"])
    label = label_for(record)
    # Hub cards never get an italic accent: the dominant text is the topic
    # name, not an argument.
    accent = None if is_hub else record["accent"]
    subtitle_html = ""
    if is_hub and record.get("subtitle"):
        subtitle_html = f'<div class="hub-sub">{html_mod.escape(record["subtitle"])}</div>'

    # Structured-family tokens. In strict mode a missing field never reaches
    # here (og_manifest.resolve already raised); in non-strict/dev mode a
    # gap falls back to the plain headline+sup layout below.
    extra: dict[str, str] = {}
    use_fallback = False
    if family == "proof":
        rows = record.get("rows")
        if rows:
            extra["rows_html"] = _rows_html(rows)
        else:
            use_fallback = True
    elif family == "comparison":
        boxes = record.get("boxes")
        if boxes:
            extra["box_html"] = _boxes_html(boxes)
        else:
            use_fallback = True
    elif family == "integration":
        badge, name, chain = record.get("badge"), record.get("name"), record.get("chain")
        if badge and name and chain:
            extra["badge"] = html_mod.escape(badge)
            extra["name"] = html_mod.escape(name)
            extra["chain_html"] = _chain_html(chain)
        else:
            use_fallback = True

    tpl = _FALLBACK_TPL if use_fallback else (TPL / f"{family}.html").read_text(encoding="utf-8")

    out = (tpl
           .replace("{{geometry}}", geometry)
           .replace("{{family_label}}", html_mod.escape(label))
           .replace("{{headline_px}}", str(fit(record["lines"])))
           .replace("{{lines_html}}", _lines_html(record["lines"], accent))
           .replace("{{sup}}", html_mod.escape(record.get("sup") or ""))
           .replace("{{subtitle_html}}", subtitle_html))
    for token, value in extra.items():
        out = out.replace("{{%s}}" % token, value)
    return out


def assert_versions() -> None:
    """Fail before rendering rather than emitting subtly different cards.

    playwright is checked here via package metadata, which needs no import
    of the playwright package itself. The Chromium build can only be known
    once a browser is launched, so that check happens in `_render`,
    immediately after `launch()` and before any page is opened.
    """
    import importlib.metadata as md
    got = md.version("playwright")
    if got != PLAYWRIGHT_PIN:
        raise SystemExit(f"ERROR -- playwright {got}, pinned {PLAYWRIGHT_PIN}")


def _records(strict: bool, only: str | None) -> list[dict]:
    """Load and resolve manifest records. `only` restricts to one path."""
    raw = og_manifest.load(MANIFEST)
    paths = [only] if only is not None else sorted(raw)
    return [og_manifest.resolve(rel, raw.get(rel), strict=strict) for rel in paths]


def _out_path(out_dir: Path, record: dict) -> Path:
    rel = record["path"]
    return (out_dir / rel / CARD_NAME) if rel else (out_dir / CARD_NAME)


async def _render(records: list[dict], out_dir: Path) -> None:
    """Serve the repo over local HTTP (so _base.css and the fonts resolve),
    screenshot each record with a pinned Chromium, and verify every PNG
    written is exactly WIDTH x HEIGHT.
    """
    import http.server
    import socketserver
    import threading

    from PIL import Image
    from playwright.async_api import async_playwright

    handler_cls = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(REPO))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler_cls)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    tmp_html = TPL / "_render_tmp.html"
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            if browser.version != CHROMIUM_PIN:
                raise SystemExit(
                    f"ERROR -- chromium {browser.version}, pinned {CHROMIUM_PIN}")
            page = await browser.new_page(
                viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
            try:
                for record in records:
                    tmp_html.write_text(build_html(record), encoding="utf-8")
                    await page.goto(
                        f"http://127.0.0.1:{port}/templates/og/_render_tmp.html",
                        wait_until="networkidle")
                    await page.evaluate("document.fonts.ready")

                    out_path = _out_path(out_dir, record)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(
                        path=str(out_path),
                        clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})

                    with Image.open(out_path) as im:
                        size = im.size
                    if size != (WIDTH, HEIGHT):
                        raise SystemExit(
                            f"ERROR -- {out_path} is {size}, expected "
                            f"{(WIDTH, HEIGHT)}")
            finally:
                await page.close()
                await browser.close()
    finally:
        if tmp_html.exists():
            tmp_html.unlink()
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                     help="require every record to be explicit in the manifest")
    ap.add_argument("--out", default=str(REPO / "site"),
                     help="output root; cards land at <out>/<path>/%s" % CARD_NAME)
    ap.add_argument("--only", default=None,
                     help="render/validate a single page path, e.g. insights/foo/")
    ap.add_argument("--dry-run", action="store_true",
                     help="resolve and validate every record; write nothing "
                          "and touch no browser (works with no Chromium installed)")
    args = ap.parse_args(argv)

    try:
        records = _records(args.strict, args.only)
    except og_manifest.ManifestError as exc:
        print(f"ERROR -- {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"OK -- {len(records)} record(s) resolved cleanly")
        return 0

    assert_versions()
    asyncio.run(_render(records, Path(args.out)))
    print(f"OK -- wrote {len(records)} card(s) under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
