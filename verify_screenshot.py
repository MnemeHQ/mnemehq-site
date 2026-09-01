import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create fresh context with cache bypass
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            extra_http_headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        )
        page = await context.new_page()
        
        # Log all responses
        page.on("response", lambda res: print(f"[{res.status}] {res.url} (type: {res.headers.get('content-type', '')})"))
        
        print("Navigating to https://mnemehq.com/audit/workspace/ ...")
        response = await page.goto("https://mnemehq.com/audit/workspace/", wait_until="networkidle")
        print(f"Main response status: {response.status}")
        
        await page.wait_for_timeout(1000)
        await page.screenshot(path="workspace_verified.png", full_page=True)
        print("Screenshot saved to workspace_verified.png")
        await browser.close()

asyncio.run(run())