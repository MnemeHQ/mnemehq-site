import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 1400})
        page = await context.new_page()
        
        # Navigate to workspace
        print("Navigating to https://mnemehq.com/audit/workspace/ ...")
        await page.goto("https://mnemehq.com/audit/workspace/", wait_until="networkidle")
        
        # Fill repo url and click Run Architecture Audit
        print("Filling repo URL...")
        await page.fill("#repo-url", "https://github.com/adr/gadr")
        
        print("Clicking submit...")
        await page.click("button[type='submit']")
        
        print("Waiting for .stats-grid to appear on report page...")
        await page.wait_for_selector(".stats-grid", timeout=60000)
        await page.wait_for_timeout(2000)
        
        print("Taking screenshot...")
        await page.screenshot(path="final_verified_live.png", full_page=True)
        print("Saved to final_verified_live.png")
        await browser.close()

asyncio.run(run())