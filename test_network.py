#!/usr/bin/env python3
"""Test SmartLabOS with network monitoring."""
import asyncio
from playwright.async_api import async_playwright

async def test_smartlabos():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Track network
        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.url}: {req.failure}"))
        
        # Console
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # Errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        print("Loading with cache bust...")
        await page.goto(f"http://localhost:8000/?v={id(page)}")
        await page.wait_for_timeout(3000)
        
        print(f"\nConsole messages: {len(console_logs)}")
        for log in console_logs:
            print(f"  {log}")
        
        print(f"\nPage errors: {len(page_errors)}")
        for err in page_errors:
            print(f"  {err}")
        
        print(f"\nFailed requests: {len(failed_requests)}")
        for req in failed_requests:
            print(f"  {req}")
        
        # Check if main.js was loaded
        main_js = await page.evaluate("document.querySelector('script[src*=main]')")
        print(f"\nmain.js script tag: {main_js}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_smartlabos())
