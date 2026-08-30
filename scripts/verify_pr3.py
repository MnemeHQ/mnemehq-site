"""PR3 verification: pilot page, team pages, pricing.
Usage: python scripts/verify_pr3.py
"""
import threading
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).parent.parent / "site"
SHOTS = Path(__file__).parent.parent / "scratch" / "pr3-shots"
PORT = 8744

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
        page.route("https://formspree.io/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"ok":true}',
        ))

        # ── Pilot page ──
        page.goto(f"{base}/pilot/", wait_until="networkidle")
        # side-by-side above the fold
        side_by_side = page.evaluate("""() => {
          const fit = document.querySelector('.fit-section').getBoundingClientRect();
          const form = document.querySelector('.pilot-form-wrap').getBoundingClientRect();
          return Math.abs(fit.top - form.top) < 40;
        }""")
        check("[pilot] criteria + form side-by-side", side_by_side)
        page.screenshot(path=str(SHOTS / "pilot-desktop.png"))
        # required fields
        req = page.evaluate("""() => [...document.querySelectorAll('#pilot-form [required]')]
          .map(el => el.name).sort()""")
        check("[pilot] exactly 4 required fields",
              req == ["challenge", "company", "email", "name"])
        check("[pilot] team type optional", page.locator('#pilot-team-type[required]').count() == 0)
        check("[pilot] challenge label asks for one rule",
              "one architectural rule" in page.locator('label[for="pilot-challenge"]').text_content())
        # coral submit, >= 44px
        btn = page.locator("#pilot-submit")
        bg = btn.evaluate("el => getComputedStyle(el).backgroundColor")
        h = btn.evaluate("el => el.getBoundingClientRect().height")
        check("[pilot] submit coral", bg == "rgb(234, 115, 94)")
        check("[pilot] submit >= 44px", h >= 44)

        # form events: start, error, submit
        events = page.evaluate("""() => {
          window.dataLayer = [];
          const form = document.getElementById('pilot-form');
          form.querySelector('#pilot-name').focus();
          form.dispatchEvent(new Event('focusin', {bubbles:true}));
          const btn = document.getElementById('pilot-submit');
          btn.click();  // empty form -> validation error
          return window.dataLayer.map(d => d.event);
        }""")
        check("[pilot] pilot_form_start emitted", "pilot_form_start" in events)
        check("[pilot] pilot_form_error emitted on empty submit", "pilot_form_error" in events)
        ev2 = page.evaluate("""() => {
          window.dataLayer = [];
          document.getElementById('pilot-name').value = 'Test';
          document.getElementById('pilot-email').value = 't@x.io';
          document.getElementById('pilot-company').value = 'X';
          document.getElementById('pilot-challenge').value = 'rule';
          document.getElementById('pilot-submit').click();
          return new Promise(r => setTimeout(() => r(window.dataLayer.map(d => d.event)), 1500));
        }""")
        check("[pilot] pilot_form_attempt emitted on valid submit", "pilot_form_attempt" in ev2)
        check("[pilot] pilot_form_success emitted after HTTP 200", "pilot_form_success" in ev2)
        check("[pilot] no legacy generic form events emitted",
              not any(e in ev2 for e in ("form_start", "form_submit", "form_success")))

        # mobile screenshot
        pm = browser.new_page(viewport={"width": 390, "height": 844})
        pm.goto(f"{base}/pilot/", wait_until="networkidle")
        pm.screenshot(path=str(SHOTS / "pilot-mobile.png"))
        pm.close()

        # ── Team pages ──
        for path in ["for/", "for/cto/", "for/platform/", "for/principal-engineer/"]:
            page.goto(f"{base}/{path}", wait_until="networkidle")
            pilot = page.locator('a.cta-btn-primary[data-cta-intent="pilot"]').count()
            contact = page.locator('a.btn-primary[href="/contact/"]').count()
            check(f"[{path}] pilot primary present", pilot >= 1)
            check(f"[{path}] no lime contact primary", contact == 0)

        # ── Pricing ──
        page.goto(f"{base}/pricing/", wait_until="networkidle")
        h1 = page.locator("h1").text_content()
        check("[pricing] h1 reframed", "Open source now" in h1)
        ent = page.locator(".pricing-card").nth(2).text_content()
        check("[pricing] enterprise marked as roadmap", "later" in ent and "TBD" in ent)
        install = page.locator('a:has-text("Install Mneme")').first
        check("[pricing] OSS install -> quickstart", (install.get_attribute("href") or "") == "/docs/#quickstart")
        check("[pricing] no Talk-to-us /contact/ card CTA", page.locator('.btn-card[href="/contact/"]').count() == 0)
        lime = page.evaluate("""() => [...document.querySelectorAll('.btn-card')]
          .filter(el => getComputedStyle(el).backgroundColor === 'rgb(200, 240, 96)').length""")
        check("[pricing] zero lime card buttons", lime == 0)
        page.screenshot(path=str(SHOTS / "pricing.png"), full_page=True)

        page.close()
        browser.close()
    httpd.shutdown()

    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        raise SystemExit(1)
    print("ALL PR3 CHECKS PASSED")


if __name__ == "__main__":
    main()
