"""PR4 verification: insights bands, concept links, benchmark cluster.
Usage: python scripts/verify_pr4.py
"""
import threading
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).parent.parent / "site"
SHOTS = Path(__file__).parent.parent / "scratch" / "pr4-shots"
PORT = 8745

failures = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


def main():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    SHOTS.mkdir(parents=True, exist_ok=True)
    base = f"http://127.0.0.1:{PORT}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # ── Insight article ──
        page.goto(f"{base}/insights/how-ai-coding-agents-use-adrs/", wait_until="networkidle")
        band = page.locator(".cta-band")
        check("[insight] cta-band present", band.count() == 1)
        # band sits after the first h2 section, before the second h2
        order = page.evaluate("""() => {
          const body = document.querySelector('.article-body') || document.body;
          const h2s = body.querySelectorAll('h2');
          const bandEl = document.querySelector('.cta-band');
          if (!h2s.length || !bandEl) return 'missing';
          const second = h2s[1] || h2s[0];
          return bandEl.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING ? 'band-before-h2-2' : 'wrong';
        }""")
        check("[insight] band after first section (before 2nd h2)", order == "band-before-h2-2")
        lime = page.evaluate("""() => [...document.querySelectorAll('.cta-band a')]
          .filter(el => getComputedStyle(el).backgroundColor === 'rgb(200, 240, 96)').length""")
        check("[insight] zero lime in band", lime == 0)
        page.screenshot(path=str(SHOTS / "insight-band.png"), full_page=True)

        # ── Concept page ──
        page.goto(f"{base}/concepts/intent-debt/", wait_until="networkidle")
        check("[concept] soft demo link present", page.locator('a.cta-link[data-cta-component="concept_link"]').count() == 1)

        # ── Benchmark ──
        page.goto(f"{base}/benchmark/", wait_until="networkidle")
        run_btn = page.locator('a:has-text("Run the benchmark")').first
        check("[benchmark] Run the benchmark at top", run_btn.count() >= 1)
        box = run_btn.bounding_box()
        check("[benchmark] above the fold", box and box["y"] < 900)
        check("[benchmark] Contribute a scenario present", page.locator('a:has-text("Contribute a scenario")').count() >= 1)
        page.screenshot(path=str(SHOTS / "benchmark-top.png"))

        # ── Spot-check band rendering on 3 more articles ──
        for slug in ["ai-native-engineering-intent-debt", "why-code-review-cannot-scale-with-ai-output", "harness-engineering-still-needs-governance"]:
            page.goto(f"{base}/insights/{slug}/", wait_until="networkidle")
            b = page.locator(".cta-band")
            ok = b.count() == 1
            prim = page.locator('.cta-band a.cta-btn-primary[data-cta-intent="install"]').count() == 1
            check(f"[insight:{slug}] band + install primary", ok and prim)

        page.close()
        browser.close()
    httpd.shutdown()

    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        raise SystemExit(1)
    print("ALL PR4 CHECKS PASSED")


if __name__ == "__main__":
    main()
