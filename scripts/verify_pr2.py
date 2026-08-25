"""PR2 verification: demo hub + demo details + integration pages.
Reuses the PR1 checks where relevant. Usage: python scripts/verify_pr2.py
"""
import threading
import functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).parent.parent / "site"
SHOTS = Path(__file__).parent.parent / "scratch" / "pr2-shots"
PORT = 8743

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

        # ── Demo hub ──
        page.goto(f"{base}/demo/", wait_until="networkidle")
        check("[demo-hub] install module present", page.locator("#try .install-module").count() == 1)
        check("[demo-hub] coral install primary", page.locator('#try a.cta-btn-primary[data-cta-intent="install"]').count() == 1)
        lime = page.evaluate("""() => [...document.querySelectorAll('#try a, #try button')]
          .filter(el => getComputedStyle(el).backgroundColor === 'rgb(200, 240, 96)').length""")
        check("[demo-hub] zero lime fills in #try", lime == 0)
        filled = page.evaluate("""() => [...document.querySelectorAll('#try a')]
          .filter(el => { const m = getComputedStyle(el).backgroundColor.match(/\\d+/g);
            return m && +m[0] === 234 && +m[1] === 115 && +m[2] === 94; }).length""")
        check("[demo-hub] one filled coral in cluster", filled == 1)
        page.screenshot(path=str(SHOTS / "demo-hub.png"), full_page=True)

        # ── Demo details ──
        for slug in ["adr-compiler", "architectural-drift", "storage-decision"]:
            page.goto(f"{base}/demo/{slug}/", wait_until="networkidle")
            check(f"[demo:{slug}] #try section present", page.locator("#try").count() == 1)
            check(f"[demo:{slug}] install primary -> quickstart",
                  (page.locator('#try a.cta-btn-primary').first.get_attribute("href") or "").startswith("/docs/#quickstart"))
            check(f"[demo:{slug}] copy button present", page.locator('#try [data-code-copy]').count() == 1)

        # copy event fires on a demo page
        page.goto(f"{base}/demo/adr-compiler/", wait_until="networkidle")
        ev = page.evaluate("""() => { window.dataLayer = [];
          document.querySelector('#try [data-code-copy]').click();
          return window.dataLayer.filter(d => d.event === 'code_copy'); }""")
        check("[demo:adr-compiler] code_copy emitted", len(ev) == 1 and "pip install" in ev[0].get("copy_context", ""))

        # ── Integration pages ──
        for slug, tool in [("claude-code", "Claude Code"), ("codex-cli", "Codex CLI"),
                           ("cursor", "Cursor"), ("warp", "Warp")]:
            page.goto(f"{base}/integrations/{slug}/", wait_until="networkidle")
            setup = page.locator('a[data-cta-intent="setup"]').first
            check(f"[int:{slug}] setup CTA present", setup.count() >= 1)
            check(f"[int:{slug}] setup names the tool", tool in (setup.text_content() or ""))
            check(f"[int:{slug}] setup -> quickstart", (setup.get_attribute("href") or "").startswith("/docs/#quickstart"))
            check(f"[int:{slug}] pilot tertiary present", page.locator('a[data-cta-intent="pilot"][data-cta-position="hero"]').count() == 1)
            if slug == "claude-code":
                page.screenshot(path=str(SHOTS / "integration-claude-code.png"), full_page=False)

        # no lime end-block primaries anywhere sampled
        for slug in ["claude-code", "cursor", "gitlab"]:
            page.goto(f"{base}/integrations/{slug}/", wait_until="networkidle")
            lime = page.evaluate("""() => [...document.querySelectorAll('.cta-block a, .article-footer a')]
              .filter(el => getComputedStyle(el).backgroundColor === 'rgb(200, 240, 96)').length""")
            check(f"[int:{slug}] zero lime end-block buttons", lime == 0)

        # ── Use-case destination fix ──
        page.goto(f"{base}/use-cases/coding-assistant-governance/", wait_until="networkidle")
        install = page.locator('a:has-text("Install Mneme")').first
        check("[use-case] Install Mneme -> quickstart (not GitHub)",
              (install.get_attribute("href") or "").startswith("/docs/#quickstart"))

        page.close()
        browser.close()
    httpd.shutdown()

    print()
    if failures:
        print(f"{len(failures)} FAILURES: {failures}")
        raise SystemExit(1)
    print("ALL PR2 CHECKS PASSED")


if __name__ == "__main__":
    main()
