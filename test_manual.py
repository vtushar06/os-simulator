#!/usr/bin/env python3
"""Execute main.js code manually."""
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
        
        await page.goto("http://localhost:8000/?v=test3")
        await page.wait_for_timeout(1000)
        
        # Manually run the initialization code from main.js
        result = await page.evaluate("""
            async () => {
                try {
                    const { iniciarStream } = await import('/static/js/api.js');
                    const { initControls } = await import('/static/js/controls.js');
                    const { initEditor } = await import('/static/js/editor.js');
                    const { initComparativa } = await import('/static/js/render_comparativa.js');
                    
                    initControls();
                    initEditor();
                    initComparativa();
                    
                    return { success: true };
                } catch (e) {
                    return { success: false, error: e.message, stack: e.stack };
                }
            }
        """)
        
        print("Result:", result)
        print(f"\nConsole: {len(console_logs)}")
        for log in console_logs[:10]:
            print(f"  {log}")
        print(f"\nErrors: {len(page_errors)}")
        for err in page_errors:
            print(f"  {err}")
        
        await page.wait_for_timeout(1000)
        
        # Now check if panels work
        await page.click("#btn-demo")
        await page.wait_for_timeout(2000)
        await page.click("#btn-play")
        await page.wait_for_timeout(3000)
        
        metrics = await page.inner_html("#tabla-metricas")
        log = await page.inner_html("#bitacora")
        print(f"\nMetrics panel: {len(metrics)} chars")
        print(f"Event log: {len(log)} chars")
        
        await browser.close()

asyncio.run(test())
