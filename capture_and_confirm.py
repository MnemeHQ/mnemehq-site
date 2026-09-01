import asyncio
import json
import subprocess
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 1000},
            extra_http_headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        )
        page = await context.new_page()
        
        print("Navigating to https://mnemehq.com/audit/workspace/ ...")
        await page.goto("https://mnemehq.com/audit/workspace/", wait_until="networkidle")
        
        print("Submitting adr/gadr audit form...")
        await page.fill("#repo-url", "https://github.com/adr/gadr")
        
        async with page.expect_response(lambda res: "/api/audit" in res.url and res.status == 200, timeout=120000):
            await page.click("button[type='submit']")
        
        print("API responded 200 OK! Waiting for .stats-grid in UI...")
        await page.wait_for_selector(".stats-grid", timeout=15000)
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path="report_live_confirmed.png", full_page=True)
        print("Full page screenshot saved to report_live_confirmed.png")
        
        await browser.close()

asyncio.run(run())