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
    dict cannot express it. Brand cards carry the identity alone."""
    fam, path = record["family"], record["path"]
    if fam == "brand":
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


def build_html(record: dict) -> str:
    tpl = (TPL / f"{record['family']}.html").read_text(encoding="utf-8")
    geometry = ""
    if record["family"] == "editorial":
        geometry = og_geometry.render(
            record["path"].rstrip("/").rsplit("/", 1)[-1],
            record["motif"], record["tone"])
    label = label_for(record)
    return (tpl
            .replace("{{geometry}}", geometry)
            .replace("{{family_label}}", html_mod.escape(label))
            .replace("{{headline_px}}", str(fit(record["lines"])))
            .replace("{{lines_html}}", _lines_html(record["lines"], record["accent"]))
            .replace("{{sup}}", html_mod.escape(record.get("sup") or "")))


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
