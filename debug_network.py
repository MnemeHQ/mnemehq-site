import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept and log all responses
        page.on("response", lambda res: print(f"[{res.status}] {res.url} (content-type: {res.headers.get('content-type')})"))
        
        await page.goto("https://mnemehq.com/audit/workspace/", wait_until="networkidle")
        await browser.close()

asyncio.run(run())