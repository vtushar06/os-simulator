#!/usr/bin/env python3
"""Check if ES modules are loading."""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        await page.goto(f"http://localhost:8000/?v=test")
        await page.wait_for_timeout(2000)
        
        # Try to import main.js manually
        result = await page.evaluate("""
            async () => {
                try {
                    const mod = await import('/static/js/main.js');
                    return { success: true, exports: Object.keys(mod) };
                } catch (e) {
                    return { success: false, error: e.message, stack: e.stack };
                }
            }
        """)
        
        print("Manual import result:", result)
        print(f"\nConsole: {len(console_logs)} messages")
        for log in console_logs:
            print(f"  {log}")
        print(f"\nErrors: {len(page_errors)}")
        for err in page_errors:
            print(f"  {err}")
        
        await browser.close()

asyncio.run(test())
