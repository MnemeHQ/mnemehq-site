#!/usr/bin/env python3
"""Task 11 Gate B defect scan: automated checks over all 322 OG card records.

Checks (see .superpowers/sdd/2026-09-21-og-card-system/task-11-brief.md, Step 3):
  a) leftover template tokens ("{{" surviving in rendered HTML)
  b) overflow / clipping (element bounding boxes vs the 1200x630 frame,
     and overlap with the identity bar)
  c) truncated or false identifiers (row/chain strings that look like an
     identifier but do not appear verbatim anywhere under site/**/*.html)
  d) capability badges (integration badge vs. that page's own stated status)

This is a read-only QA tool. It never modifies cards.yaml, templates, or
site content -- it only reports.

Usage:
  python scripts/og_defect_scan.py [--json out.json]
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import og_manifest          # noqa: E402
import render_og            # noqa: E402

MANIFEST = REPO / "site" / "og" / "cards.yaml"
SITE = REPO / "site"
TPL_DIR = REPO / "templates" / "og"


def load_records() -> list[dict]:
    raw = og_manifest.load(MANIFEST)
    return [og_manifest.resolve(rel, raw.get(rel), strict=True) for rel in sorted(raw)]


# ---------------------------------------------------------------------------
# (a) leftover template tokens
# ---------------------------------------------------------------------------

def check_template_tokens(records: list[dict]) -> list[dict]:
    findings = []
    for rec in records:
        html = render_og.build_html(rec)
        if "{{" in html or "}}" in html:
            # Report every surviving token occurrence, not just the fact of one.
            tokens = re.findall(r"\{\{[^}]*\}\}", html)
            findings.append({
                "path": rec["path"] or "(root)",
                "tokens": tokens or ["<unbalanced brace, no clean token match>"],
            })
    return findings


# ---------------------------------------------------------------------------
# (b) overflow / clipping -- measured via Playwright bounding boxes
# ---------------------------------------------------------------------------

def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


async def _measure_all(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Returns (overflow_findings, staleness_findings).

    IMPORTANT: render_og.py's own render loop reuses a single fixed temp
    HTML filename across all 322 iterations and lets Playwright fetch it
    over a local HTTP server with default caching. That is vulnerable to
    the browser treating a rapid rewrite-and-refetch as cache-valid (a 304
    or a stale cache hit before the new mtime is observed), so the
    screenshot for record N can silently capture record N-1's page. This
    was independently confirmed by hashing every staged PNG under
    site/og-staging/ -- 126 hash-collision groups (252 of 322 files) were
    found there. This scan therefore uses a UNIQUE filename and a
    cache-busting query string per record, and additionally verifies the
    loaded page's own text contains that record's expected headline/name,
    to guarantee ITS OWN measurements are not victims of the same bug.
    """
    import http.server
    import socketserver
    import threading

    from playwright.async_api import async_playwright

    handler_cls = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(REPO))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler_cls)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    findings: list[dict] = []
    staleness: list[dict] = []
    written_tmp_files: list[Path] = []

    JS = """
    () => {
      const W = 1200, H = 630, EPS = 0.5;
      const top = document.querySelector('.top');
      const topRect = top ? top.getBoundingClientRect() : null;
      const nodes = document.querySelectorAll('.frame, .frame *');
      const out = [];
      for (const el of nodes) {
        const r = el.getBoundingClientRect();
        // Skip zero-area elements (e.g. the <br> tags, empty wrapper divs).
        if (r.width <= 0 && r.height <= 0) continue;
        const overRight = r.right > W + EPS;
        const overBottom = r.bottom > H + EPS;
        const underLeft = r.left < -EPS;
        const underTop = r.top < -EPS;
        // Only elements INSIDE .body count as identity-bar overlap candidates.
        // .frame (which contains .top) and .top itself always geometrically
        // "contain"/equal the identity bar's rect, which is not a defect --
        // it would just be measuring the container against itself.
        let overlapsIdentity = false;
        if (topRect && el.closest('.body')) {
          const vOverlap = r.top < topRect.bottom - EPS && r.bottom > topRect.top + EPS;
          const hOverlap = r.left < topRect.right - EPS && r.right > topRect.left + EPS;
          overlapsIdentity = vOverlap && hOverlap && r.width > 0 && r.height > 0;
        }
        if (overRight || overBottom || underLeft || underTop || overlapsIdentity) {
          out.push({
            tag: el.tagName.toLowerCase(),
            cls: el.className && typeof el.className === 'string' ? el.className : '',
            text: (el.textContent || '').trim().slice(0, 60),
            rect: {left: r.left, top: r.top, right: r.right, bottom: r.bottom},
            overRight, overBottom, underLeft, underTop, overlapsIdentity,
          });
        }
      }
      return out;
    }
    """

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(
                viewport={"width": render_og.WIDTH, "height": render_og.HEIGHT},
                device_scale_factor=1)
            try:
                for i, rec in enumerate(records):
                    tmp_html = TPL_DIR / f"_defect_scan_tmp_{i}.html"
                    written_tmp_files.append(tmp_html)
                    tmp_html.write_text(render_og.build_html(rec), encoding="utf-8")
                    await page.goto(
                        f"http://127.0.0.1:{port}/templates/og/{tmp_html.name}?v={i}",
                        wait_until="networkidle")
                    await page.evaluate("document.fonts.ready")

                    # Staleness self-check: does the loaded page actually show
                    # THIS record's own text? The 'proof' family template never
                    # renders the headline on the card face (only the rows), so
                    # for that family check a row value instead.
                    body_text = _norm_text(await page.evaluate("document.body.innerText"))
                    if rec["family"] == "proof" and rec.get("rows"):
                        expect = rec["rows"][0][1]
                    else:
                        expect = rec.get("name") or rec["headline"]
                    if _norm_text(expect) not in body_text:
                        staleness.append({
                            "path": rec["path"] or "(root)",
                            "expected": expect,
                            "page_text_sample": body_text[:200],
                        })
                        continue  # don't trust geometry measured off wrong content

                    offenders = await page.evaluate(JS)
                    if offenders:
                        findings.append({"path": rec["path"] or "(root)", "offenders": offenders})
            finally:
                await page.close()
                await browser.close()
    finally:
        for f in written_tmp_files:
            if f.exists():
                f.unlink()
        httpd.shutdown()
        httpd.server_close()
        thread.join()

    return findings, staleness


def check_overflow(records: list[dict]) -> tuple[list[dict], list[dict]]:
    import asyncio
    return asyncio.run(_measure_all(records))


# ---------------------------------------------------------------------------
# (c) truncated / false identifiers
# ---------------------------------------------------------------------------

IDENT_RE = re.compile(r"\b([a-z]+_[a-z_]+|ADR-\d+)\b")


def _all_site_html_text() -> str:
    parts = []
    for f in SITE.rglob("*.html"):
        try:
            parts.append(f.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return "\n".join(parts)


def check_identifiers(records: list[dict]) -> list[dict]:
    corpus = _all_site_html_text()
    findings = []
    for rec in records:
        strings = []
        for row in (rec.get("rows") or []):
            label, value, _kind = row
            strings.append(("row.label", label))
            strings.append(("row.value", value))
        for item in (rec.get("chain") or []):
            strings.append(("chain.text", item.get("text", "")))
        # Also scan integration name/badge and comparison boxes for completeness.
        if rec.get("name"):
            strings.append(("name", rec["name"]))
        if rec.get("badge"):
            strings.append(("badge", rec["badge"]))
        for box in (rec.get("boxes") or []):
            strings.append(("box.label", box.get("label", "")))
            strings.append(("box.value", box.get("value", "")))
            strings.append(("box.verdict", box.get("verdict", "")))

        for field, text in strings:
            for m in IDENT_RE.finditer(text):
                ident = m.group(1)
                if ident not in corpus:
                    findings.append({
                        "path": rec["path"] or "(root)",
                        "field": field,
                        "identifier": ident,
                        "source_text": text,
                    })
    return findings


# ---------------------------------------------------------------------------
# (d) capability badges vs. page's own stated status
# ---------------------------------------------------------------------------

STRONG_BADGE_WORDS = ("native", "shipped", "production", "tier 1")
WEAK_STATUS_WORDS = (
    "experimental", "planned", "prototype", "proof of concept", "poc",
    "coming soon", "not yet shipped", "unshipped", "pre-release", "alpha",
    "roadmap-only", "roadmap only",
)

EYEBROW_RE = re.compile(
    r'class="(?:hero-eyebrow|eyebrow-tag|status)"[^>]*>([^<]*)<', re.IGNORECASE)
STATUS_HEADING_RE = re.compile(
    r'<h2>\s*Status[^<]*</h2>\s*<p>(.*?)</p>', re.IGNORECASE | re.DOTALL)


def _page_path_for(rec_path: str) -> Path:
    rel = rec_path if rec_path.endswith("/") else rec_path + "/"
    return SITE / rel / "index.html"


def _self_status_text(html: str) -> str:
    """Text the page uses to describe ITS OWN status -- eyebrow tag(s) plus
    any explicit 'Status:' section. Deliberately narrow: whole-page grep
    picks up the 'Experimental & planned' page-switcher nav group label
    that appears on every integration page regardless of that page's own
    status, which would make every badge look contradicted.
    """
    bits = [m.group(1) for m in EYEBROW_RE.finditer(html)]
    bits += [m.group(1) for m in STATUS_HEADING_RE.finditer(html)]
    return " || ".join(bits)


def check_badges(records: list[dict]) -> list[dict]:
    findings = []
    for rec in records:
        if rec["family"] != "integration":
            continue
        badge = (rec.get("badge") or "")
        badge_l = badge.lower()
        if not any(w in badge_l for w in STRONG_BADGE_WORDS):
            continue
        page_file = _page_path_for(rec["path"])
        if not page_file.is_file():
            findings.append({
                "path": rec["path"], "badge": badge,
                "issue": f"no page found at {page_file}",
            })
            continue
        html = page_file.read_text(encoding="utf-8", errors="ignore")
        self_status = _self_status_text(html)
        self_status_l = self_status.lower()
        hits = [w for w in WEAK_STATUS_WORDS if w in self_status_l]
        if hits:
            findings.append({
                "path": rec["path"], "badge": badge,
                "self_status_text": self_status,
                "contradicting_words": hits,
            })
        elif not self_status.strip():
            findings.append({
                "path": rec["path"], "badge": badge,
                "issue": "no self-status eyebrow/heading found to corroborate badge",
                "confidence": "low",
            })
    return findings


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, help="write full results as JSON to this path")
    ap.add_argument("--skip-overflow", action="store_true",
                     help="skip the Playwright overflow pass (slow); useful when iterating on a/c/d")
    args = ap.parse_args(argv)

    records = load_records()
    print(f"Loaded {len(records)} records.\n")

    results = {}

    print("=== (a) leftover template tokens ===")
    results["template_tokens"] = check_template_tokens(records)
    print(f"{len(results['template_tokens'])} offending page(s)")
    for f in results["template_tokens"]:
        print(f"  FAIL {f['path']}: {f['tokens']}")

    print("\n=== (b) overflow / clipping (+ render-staleness self-check) ===")
    if args.skip_overflow:
        print("SKIPPED")
        results["overflow"] = []
        results["staleness"] = []
    else:
        overflow, staleness = check_overflow(records)
        results["overflow"] = overflow
        results["staleness"] = staleness
        print(f"{len(staleness)} page(s) where the loaded content did not match the "
              f"expected record (stale-cache render bug -- see report)")
        for s in staleness:
            print(f"  STALE {s['path']}: expected {s['expected']!r}, "
                  f"got page text starting {s['page_text_sample']!r}")
        print(f"{len(overflow)} offending page(s) (measured only on verified-fresh loads)")
        for f in overflow:
            print(f"  FAIL {f['path']}: {len(f['offenders'])} offending element(s)")
            for o in f["offenders"]:
                flags = [k for k in ("overRight", "overBottom", "underLeft", "underTop",
                                      "overlapsIdentity") if o.get(k)]
                print(f"      <{o['tag']} class={o['cls']!r}> rect={o['rect']} flags={flags} "
                      f"text={o['text']!r}")

    print("\n=== (c) truncated / false identifiers ===")
    results["identifiers"] = check_identifiers(records)
    print(f"{len(results['identifiers'])} offending identifier occurrence(s)")
    for f in results["identifiers"]:
        print(f"  FAIL {f['path']} [{f['field']}]: {f['identifier']!r} not found under site/**/*.html "
              f"(source: {f['source_text']!r})")

    print("\n=== (d) capability badges ===")
    results["badges"] = check_badges(records)
    print(f"{len(results['badges'])} flagged integration record(s)")
    for f in results["badges"]:
        print(f"  FLAG {f['path']} badge={f['badge']!r}")
        if "contradicting_words" in f:
            print(f"      self-status says: {f['self_status_text']!r}")
            print(f"      contradicting words: {f['contradicting_words']}")
        elif "issue" in f:
            print(f"      {f['issue']}")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nWrote full results to {args.json}")

    total = sum(len(v) for v in results.values())
    print(f"\nTOTAL findings across a/b/c/d: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
