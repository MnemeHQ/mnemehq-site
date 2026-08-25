"""PR 1 verification: screenshots, keyboard focus, destination integrity,
one-filled-action-per-cluster, no lime button fills.
Usage: python scripts/verify_pr1.py
"""
import threading
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).parent.parent / "site"
SHOTS = Path(__file__).parent.parent / "scratch" / "pr1-shots"
PORT = 8741

failures = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


def main():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    SHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for label, url in [("home", f"http://127.0.0.1:{PORT}/"),
                           ("docs", f"http://127.0.0.1:{PORT}/docs/")]:
            for width, height, tag in [(1280, 900, "desktop"), (390, 844, "mobile")]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url, wait_until="networkidle")

                if width == 1280:
                    # 1. Nav CTA is outline: transparent fill, has border
                    nav_cta = page.locator(".nav-links a.btn-nav-cta").first
                    bg = nav_cta.evaluate("el => getComputedStyle(el).backgroundColor")
                    border = nav_cta.evaluate("el => getComputedStyle(el).borderStyle")
                    check(f"[{label}] nav CTA transparent fill", bg in ("rgba(0, 0, 0, 0)", "transparent"))
                    check(f"[{label}] nav CTA outlined", border == "solid")
                    # no lime fill anywhere on buttons
                    lime = page.evaluate("""() =>
                      [...document.querySelectorAll('a.btn-nav-cta, button, a[class*="btn"], a[class*="cta"]')]
                        .filter(el => { const s = getComputedStyle(el);
                          return s.backgroundColor === 'rgb(200, 240, 96)'; }).length""")
                    check(f"[{label}] zero lime button fills", lime == 0)

                page.screenshot(path=str(SHOTS / f"{label}-{tag}.png"), full_page=(width == 1280))
                page.close()

        # Destination integrity + cluster rule + keyboard focus (homepage, desktop)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")

        hero_install = page.locator('.hm-actions a[data-cta-intent="install"]').first
        check("[home] hero Install primary -> #install", hero_install.get_attribute("href") == "#install")
        check("[home] #install target exists", page.locator("#install").count() >= 1)

        filled_in_hero = page.evaluate("""() => {
          const hero = document.querySelector('.hm-hero');
          return [...hero.querySelectorAll('a')]
            .filter(el => { const s = getComputedStyle(el);
              const m = s.backgroundColor.match(/\\d+/g);
              return m && (+m[0] === 234 && +m[1] === 115 && +m[2] === 94); }).length;
        }""")
        check("[home] exactly ONE filled coral action in hero", filled_in_hero == 1)

        # keyboard focus ring reaches the hero primary
        page.keyboard.press("Tab")   # skip link
        focused = page.evaluate("document.activeElement.className")
        check("[home] first tab stop is skip link", "skip-link" in focused)

        # analytics handler present
        has_handler = page.evaluate("[...document.scripts].some(s => s.textContent.includes('cta-analytics'))")
        check("[home] analytics handler script present", has_handler)

        # simulate a click and inspect dataLayer
        events = page.evaluate("""() => {
          window.dataLayer = [];
          const el = document.querySelector('.hm-actions a[data-cta-intent]');
          el.click();
          return window.dataLayer.filter(d => d.event === 'cta_click');
        }""")
        ok = len(events) == 1 and events[0].get("cta_intent") == "install" \
             and events[0].get("cta_position") == "hero" \
             and events[0].get("page_type") == "homepage"
        check("[home] cta_click event payload correct", ok)

        # docs page checks
        page.goto(f"http://127.0.0.1:{PORT}/docs/", wait_until="networkidle")
        check("[docs] copy install command control present",
              page.locator('[data-code-copy]').count() >= 1)
        copy_events = page.evaluate("""() => {
          window.dataLayer = [];
          document.querySelector('[data-code-copy]').click();
          return window.dataLayer.filter(d => d.event === 'code_copy');
        }""")
        check("[docs] code_copy emitted (not cta_click)",
              len(copy_events) == 1 and "pip install mneme-hq" in copy_events[0].get("copy_context", ""))

        page.close()
        browser.close()

    httpd.shutdown()

    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        raise SystemExit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
