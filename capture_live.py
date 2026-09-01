import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create context with cache disabled
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            extra_http_headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        )
        page = await context.new_page()
        
        failed = []
        page.on("requestfailed", lambda req: failed.append(f"[FAILED REQ] {req.url}: {req.failure}"))
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
        
        print("Navigating to https://mnemehq.com/audit/workspace/ ...")
        response = await page.goto("https://mnemehq.com/audit/workspace/", wait_until="networkidle")
        print(f"Status: {response.status}")
        
        await page.wait_for_timeout(1000)
        
        if failed:
            print("Failures encountered:")
            for f in failed:
                print(" ", f)
        else:
            print("All network requests succeeded with 200 OK!")
            
        await page.screenshot(path="workspace_rendered.png", full_page=True)
        print("Screenshot saved to workspace_rendered.png")
        
        await browser.close()

asyncio.run(run())