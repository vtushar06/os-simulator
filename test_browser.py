#!/usr/bin/env python3
"""Test SmartLabOS in headless browser to capture console errors."""
import asyncio
from playwright.async_api import async_playwright

async def test_smartlabos():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Capture console messages
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        print("Loading http://localhost:8000...")
        await page.goto("http://localhost:8000")
        await page.wait_for_timeout(2000)
        
        print("\nClicking 'Load demo workload'...")
        await page.click("#btn-demo")
        await page.wait_for_timeout(2000)
        
        print("Clicking Play...")
        await page.click("#btn-play")
        await page.wait_for_timeout(3000)
        
        # Check panels
        print("\n=== Checking Panel Content ===")
        metrics_html = await page.inner_html("#tabla-metricas")
        print(f"Metrics panel length: {len(metrics_html)} chars")
        print(f"Metrics empty: {len(metrics_html.strip()) == 0}")
        
        log_html = await page.inner_html("#bitacora")
        print(f"Event log length: {len(log_html)} chars")
        print(f"Event log empty: {len(log_html.strip()) == 0}")
        
        # Check canvas
        canvas = await page.query_selector("#cv-gantt")
        if canvas:
            width = await canvas.get_attribute("width")
            print(f"Gantt canvas width: {width}")
        
        print("\n=== Console Messages ===")
        for log in console_logs[:20]:  # First 20
            print(log)
        
        if page_errors:
            print("\n=== PAGE ERRORS ===")
            for err in page_errors:
                print(err)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_smartlabos())
