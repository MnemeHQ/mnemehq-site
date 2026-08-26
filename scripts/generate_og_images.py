#!/usr/bin/env python3
"""Generate Mneme HQ Open Graph images from page metadata.

The renderer is data-driven: every public HTML page supplies its own title,
description, and advertised og:image path. Card family and a small set of
high-value editorial overrides are derived from the page path.

Usage:
    python scripts/generate_og_images.py
    python scripts/generate_og_images.py --only / /demo/ /integrations/codex-cli/

Requires:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import argparse
import asyncio
import html
import http.server
import re
import tempfile
import threading
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
WIDTH = 1200
HEIGHT = 630


@dataclass(frozen=True)
class Card:
    path: str
    family: str
    label: str
    headline: str
    support: str
    image_path: Path
    platform: str = ""
    status: str = ""
    statement: str = ""


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "meta":
            key = attrs_d.get("property") or attrs_d.get("name")
            if key and attrs_d.get("content"):
                self.meta[key.lower()] = attrs_d["content"].strip()
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


OVERRIDES: dict[str, dict[str, str]] = {
    "/": {
        "family": "brand",
        "label": "ARCHITECTURAL DRIFT PREVENTION",
        "headline": "Architecture that holds.",
        "support": "Approved architectural intent, enforced before incompatible code lands.",
    },
    "/demo/": {
        "family": "proof",
        "label": "PRODUCT PROOF",
        "headline": "See architectural drift get blocked.",
        "support": "One approved decision. One incompatible change. One deterministic verdict.",
    },
    "/benchmark/": {
        "family": "proof",
        "label": "BENCHMARK",
        "headline": "Measure whether architecture survives the agentic SDLC.",
        "support": "Constraint survival, drift, and enforcement — tested rather than assumed.",
    },
    "/pilot/": {
        "family": "brand",
        "label": "DESIGN PARTNER PILOT",
        "headline": "Find where your AI coding workflow can drift.",
        "support": "Audit architectural intent, enforcement surfaces, and the gaps between them.",
    },
    "/concepts/architectural-drift-prevention/": {
        "family": "editorial",
        "label": "CONCEPT",
        "headline": "Architectural drift prevention",
        "support": "Keep generated code inside decisions already made.",
    },
    "/integrations/codex-cli/": {
        "family": "integration",
        "label": "INTEGRATION",
        "headline": "Codex CLI",
        "platform": "CODEX CLI",
        "status": "NATIVE · SHIPPED",
        "statement": "Block incompatible file changes before execution.",
    },
    "/integrations/antigravity/": {
        "family": "integration",
        "label": "INTEGRATION",
        "headline": "Google Antigravity",
        "platform": "ANTIGRAVITY",
        "status": "NATIVE · SHIPPED",
        "statement": "Apply architectural guardrails at the tool-call boundary.",
    },
    "/integrations/claude-code/": {
        "family": "integration",
        "label": "INTEGRATION",
        "headline": "Claude Code",
        "platform": "CLAUDE CODE",
        "status": "NATIVE · SHIPPED",
        "statement": "Turn ADRs into deterministic pre-tool enforcement.",
    },
}


def normalise_path(page: Path) -> str:
    rel = page.relative_to(SITE_DIR)
    if rel == Path("index.html"):
        return "/"
    if rel.name == "index.html":
        return "/" + rel.parent.as_posix().strip("/") + "/"
    return "/" + rel.as_posix().lstrip("/")


def clean_title(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"\s*[|—-]\s*Mneme HQ\s*$", "", value, flags=re.I)
    return " ".join(value.split()).strip()


def clamp_words(value: str, max_chars: int) -> str:
    value = " ".join(html.unescape(value or "").split())
    if len(value) <= max_chars:
        return value
    cut = value[: max_chars + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut + "…"


def family_for(path: str) -> str:
    if path.startswith("/integrations/"):
        return "integration"
    if path.startswith("/demo/") or path.startswith("/architecture/") or path == "/benchmark/":
        return "proof"
    if path.startswith("/insights/") or path.startswith("/concepts/"):
        return "editorial"
    if path.startswith("/compare/") or path.startswith("/use-cases/") or path.startswith("/for/"):
        return "boundary"
    if path in {"/", "/about/", "/founder/", "/pilot/"}:
        return "brand"
    return "editorial"


def label_for(path: str, family: str) -> str:
    if family == "integration":
        return "INTEGRATION"
    if family == "proof":
        return "PRODUCT PROOF"
    if path.startswith("/insights/"):
        return "INSIGHT"
    if path.startswith("/concepts/"):
        return "CONCEPT"
    if path.startswith("/compare/"):
        return "COMPARISON"
    if path.startswith("/use-cases/"):
        return "USE CASE"
    return "MNEME HQ"


def image_path_from_meta(page: Path, value: str) -> Path:
    if value:
        parsed = urlparse(value)
        candidate = parsed.path or value
        if candidate.startswith("/"):
            target = SITE_DIR / candidate.lstrip("/")
            if target.suffix.lower() == ".png":
                return target
    if page == SITE_DIR / "index.html":
        return SITE_DIR / "og-home-v2.png"
    return page.parent / "og.png"


def parse_card(page: Path) -> Card | None:
    text = page.read_text(encoding="utf-8")
    parser = HeadParser()
    parser.feed(text)
    path = normalise_path(page)

    if page.name.startswith("og-") or path.startswith("/assets/") or page.name == "404.html":
        return None

    override = OVERRIDES.get(path, {})
    family = override.get("family", family_for(path))
    raw_title = parser.meta.get("og:title") or parser.title
    raw_desc = parser.meta.get("og:description") or parser.meta.get("description", "")
    headline = override.get("headline", clean_title(raw_title))
    support = override.get("support", clamp_words(raw_desc, 118))
    label = override.get("label", label_for(path, family))
    image_path = image_path_from_meta(page, parser.meta.get("og:image", ""))

    platform = override.get("platform", "")
    status = override.get("status", "")
    statement = override.get("statement", "")
    if family == "integration" and not platform:
        platform = clean_title(raw_title).upper()
        status = "MNEME INTEGRATION"
        statement = clamp_words(raw_desc, 92)

    if not headline:
        return None

    return Card(
        path=path,
        family=family,
        label=label,
        headline=clamp_words(headline, 96),
        support=clamp_words(support, 132),
        image_path=image_path,
        platform=platform,
        status=status,
        statement=statement,
    )


def discover_cards() -> list[Card]:
    cards: list[Card] = []
    for page in sorted(SITE_DIR.rglob("*.html")):
        card = parse_card(page)
        if card:
            cards.append(card)
    return cards


def font_size_for(headline: str) -> int:
    n = len(headline)
    if n <= 32:
        return 82
    if n <= 52:
        return 74
    if n <= 72:
        return 66
    return 60


def visual_markup(card: Card) -> str:
    esc = html.escape
    if card.family == "integration":
        return f"""
        <div class="integration-object">
          <div class="platform">{esc(card.platform or card.headline)}</div>
          <div class="support-status">{esc(card.status or 'MNEME INTEGRATION')}</div>
          <div class="statement">{esc(card.statement or card.support)}</div>
          <div class="mechanism"><span>ARCHITECTURAL INTENT</span><b>→</b><span class="teal">PRE-TOOL GATE</span><b>→</b><span class="lime">VERDICT</span></div>
        </div>"""
    if card.family == "proof":
        return """
        <div class="proof-object">
          <div class="proof-row approved"><span>ADR-014</span><b>APPROVED</b></div>
          <div class="proof-arrow">↓</div>
          <div class="proof-row proposal"><span>PROPOSED CHANGE</span><b>PostgreSQL</b></div>
          <div class="proof-arrow">↓</div>
          <div class="proof-row blocked"><span>VERDICT</span><b>BLOCKED</b></div>
        </div>"""
    if card.family == "boundary":
        return """
        <div class="boundary-object">
          <div class="boundary-half allowed"><small>INSIDE INTENT</small><strong>ALLOWED</strong></div>
          <div class="boundary-line"></div>
          <div class="boundary-half blocked"><small>OUTSIDE INTENT</small><strong>BLOCKED</strong></div>
        </div>"""
    if card.family == "brand":
        return """
        <div class="artifact-object">
          <div class="artifact-kicker">APPROVED ARCHITECTURE</div>
          <div class="artifact-rule"><span>Decision</span><b>SQLite is the project database</b></div>
          <div class="artifact-rule"><span>Scope</span><b>storage/**</b></div>
          <div class="artifact-seal">ENFORCED BEFORE CODE</div>
        </div>"""
    return """
      <div class="editorial-object">
        <span>INTENT</span><b>→</b><span class="faded">CONTEXT</span><b>→</b><span>CODE</span>
        <div class="drift-line"></div>
        <div class="drift-label">DRIFT STARTS WHEN INTENT STOPS BEING ENFORCEABLE</div>
      </div>"""


def render_html(card: Card) -> str:
    esc = html.escape
    headline_size = font_size_for(card.headline)
    support = f'<div class="support">{esc(card.support)}</div>' if card.support else ""
    visual = visual_markup(card)
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {{ font-family: Instrument Serif; src: url('/assets/fonts/InstrumentSerif-400.woff2') format('woff2'); font-weight: 400; }}
@font-face {{ font-family: DM Mono; src: url('/assets/fonts/DMMono-400.woff2') format('woff2'); font-weight: 400; }}
@font-face {{ font-family: DM Mono; src: url('/assets/fonts/DMMono-500.woff2') format('woff2'); font-weight: 500; }}
* {{ box-sizing: border-box; }}
html, body {{ width: {WIDTH}px; height: {HEIGHT}px; margin: 0; overflow: hidden; background: #0c0c0d; }}
body {{ color: #e8e8ec; font-family: DM Mono, monospace; position: relative; }}
body::before {{ content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px); background-size: 72px 72px; mask-image: linear-gradient(to right, #000, transparent 72%); }}
body::after {{ content: ''; position: absolute; width: 520px; height: 520px; right: -120px; top: -180px; border: 1px solid rgba(139,224,200,.14); border-radius: 50%; box-shadow: 0 0 0 80px rgba(139,224,200,.025), 0 0 0 160px rgba(200,240,96,.018); }}
.frame {{ position: absolute; inset: 34px; border: 1px solid #2c2c31; padding: 38px 44px; display: grid; grid-template-rows: auto 1fr; z-index: 1; }}
.top {{ display: flex; justify-content: space-between; align-items: center; gap: 24px; }}
.brand {{ font-family: Instrument Serif, serif; font-size: 36px; letter-spacing: -.5px; }}
.label {{ font-size: 18px; letter-spacing: .08em; color: #c8f060; border: 1px solid rgba(200,240,96,.35); padding: 9px 14px; background: rgba(200,240,96,.055); }}
.content {{ display: grid; grid-template-columns: minmax(0, 1.12fr) minmax(360px, .88fr); gap: 54px; align-items: center; }}
.copy {{ max-width: 690px; }}
h1 {{ font-family: Instrument Serif, serif; font-weight: 400; font-size: {headline_size}px; line-height: .98; letter-spacing: -2px; margin: 0 0 26px; max-width: 710px; text-wrap: balance; }}
.support {{ font-size: 26px; line-height: 1.36; color: #aaaab8; max-width: 660px; }}
.integration-object, .proof-object, .boundary-object, .artifact-object, .editorial-object {{ min-height: 330px; border: 1px solid #33333a; background: rgba(20,20,22,.88); position: relative; box-shadow: 0 26px 80px rgba(0,0,0,.25); }}
.integration-object {{ padding: 30px; display: flex; flex-direction: column; justify-content: center; }}
.platform {{ font-family: Instrument Serif, serif; font-size: 52px; line-height: 1; margin-bottom: 16px; }}
.support-status {{ align-self: flex-start; font-size: 19px; color: #c8f060; border: 1px solid rgba(200,240,96,.35); padding: 8px 10px; margin-bottom: 28px; }}
.statement {{ font-size: 24px; line-height: 1.35; color: #d0d0d8; }}
.mechanism {{ margin-top: 30px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; font-size: 15px; color: #8e8e9c; }}
.mechanism .teal {{ color: #8be0c8; }} .mechanism .lime {{ color: #c8f060; }}
.proof-object {{ padding: 28px; display: flex; flex-direction: column; justify-content: center; }}
.proof-row {{ display: flex; align-items: center; justify-content: space-between; gap: 24px; border: 1px solid #37373e; padding: 18px 20px; font-size: 17px; }}
.proof-row b {{ font-size: 24px; font-weight: 500; }} .approved b {{ color: #c8f060; }} .proposal b {{ color: #8be0c8; }} .blocked {{ border-color: rgba(255,101,91,.65); background: rgba(255,101,91,.07); }} .blocked b {{ color: #ff655b; font-size: 29px; }}
.proof-arrow {{ text-align: center; color: #686874; font-size: 20px; line-height: 30px; }}
.boundary-object {{ display: grid; grid-template-columns: 1fr 1px 1fr; }} .boundary-half {{ display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 16px; }} .boundary-half small {{ font-size: 17px; color: #8f8f9b; }} .boundary-half strong {{ font-family: Instrument Serif, serif; font-weight: 400; font-size: 48px; }} .allowed strong {{ color: #c8f060; }} .blocked strong {{ color: #ff655b; }} .boundary-line {{ background: #3b3b42; }}
.artifact-object {{ padding: 28px; transform: rotate(1.5deg); }} .artifact-kicker {{ font-size: 17px; color: #ff8c78; margin-bottom: 28px; letter-spacing: .08em; }} .artifact-rule {{ border-top: 1px solid #3b3b42; padding: 18px 0; display: grid; grid-template-columns: 110px 1fr; gap: 16px; }} .artifact-rule span {{ color: #777784; font-size: 16px; }} .artifact-rule b {{ font-size: 22px; font-weight: 400; color: #dedee6; }} .artifact-seal {{ position: absolute; right: 24px; bottom: 24px; border: 1px solid rgba(200,240,96,.5); color: #c8f060; padding: 10px 12px; font-size: 16px; transform: rotate(-2deg); }}
.editorial-object {{ padding: 34px; display: flex; align-items: center; justify-content: center; gap: 14px; font-size: 27px; }} .editorial-object span {{ color: #c8f060; }} .editorial-object .faded {{ color: #777784; }} .editorial-object b {{ color: #62626d; font-weight: 400; }} .drift-line {{ position: absolute; left: 48px; right: 48px; bottom: 82px; height: 2px; background: linear-gradient(90deg,#c8f060,#8be0c8 46%,#ff655b 80%); transform: rotate(-4deg); }} .drift-label {{ position: absolute; left: 42px; right: 42px; bottom: 28px; font-size: 14px; line-height: 1.35; color: #8b8b98; text-align: center; }}
</style>
</head>
<body>
  <div class="frame">
    <div class="top"><div class="brand">Mneme HQ</div><div class="label">{esc(card.label)}</div></div>
    <div class="content">
      <div class="copy"><h1>{esc(card.headline)}</h1>{support}</div>
      {visual}
    </div>
  </div>
</body>
</html>"""


async def generate(cards: list[Card]) -> None:
    from playwright.async_api import async_playwright

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(SITE_DIR), **kwargs
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]

    try:
        with tempfile.TemporaryDirectory(prefix=".og-render-", dir=SITE_DIR) as temp_dir:
            temp_path = Path(temp_dir)
            rel_temp = temp_path.relative_to(SITE_DIR).as_posix()
            render_file = temp_path / "card.html"

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1
                )
                for card in cards:
                    card.image_path.parent.mkdir(parents=True, exist_ok=True)
                    render_file.write_text(render_html(card), encoding="utf-8")
                    await page.goto(
                        f"http://127.0.0.1:{port}/{rel_temp}/card.html",
                        wait_until="networkidle",
                    )
                    await page.evaluate("document.fonts.ready")
                    await page.screenshot(
                        path=str(card.image_path), type="png", full_page=False
                    )
                    print(
                        f"generated {card.path:<60} -> "
                        f"{card.image_path.relative_to(ROOT)}"
                    )
                await browser.close()
    finally:
        server.shutdown()
        server.server_close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=[], help="Page paths to render, e.g. /demo/ /integrations/codex-cli/")
    args = ap.parse_args()

    cards = discover_cards()
    if args.only:
        wanted = {p if p.startswith("/") else f"/{p}" for p in args.only}
        wanted = {p if p == "/" or p.endswith("/") or "." in Path(p).name else p + "/" for p in wanted}
        cards = [c for c in cards if c.path in wanted]
        missing = sorted(wanted - {c.path for c in cards})
        if missing:
            raise SystemExit(f"No public HTML page found for: {', '.join(missing)}")

    if not cards:
        raise SystemExit("No OG cards discovered")

    asyncio.run(generate(cards))
    print(f"\nGenerated {len(cards)} OG image(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
