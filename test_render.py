#!/usr/bin/env python3
"""Test the full render chain."""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        await page.goto("http://localhost:8000/?v=test4")
        await page.wait_for_timeout(1000)
        
        # Load demo and start
        await page.click("#btn-demo")
        await page.wait_for_timeout(2000)
        
        # Manually fetch state and render
        result = await page.evaluate("""
            async () => {
                try {
                    const { renderMetricas } = await import('/static/js/render_metricas.js');
                    const { renderLog } = await import('/static/js/render_log.js');
                    const { renderGantt } = await import('/static/js/render_gantt.js');
                    
                    const resp = await fetch('/api/state');
                    const snap = await resp.json();
                    
                    console.log('Got snapshot, tick:', snap.tick);
                    console.log('Eventos:', snap.eventos?.length);
                    console.log('Gantt:', snap.gantt?.length);
                    console.log('Metricas:', snap.metricas);
                    
                    renderMetricas(snap);
                    renderLog(snap);
                    renderGantt(snap);
                    
                    return { success: true, tick: snap.tick };
                } catch (e) {
                    return { success: false, error: e.message, stack: e.stack };
                }
            }
        """)
        
        print("Result:", result)
        
        await page.wait_for_timeout(500)
        
        metrics = await page.inner_html("#tabla-metricas")
        log = await page.inner_html("#bitacora")
        
        print(f"\nMetrics panel: {len(metrics)} chars")
        if len(metrics) > 0:
            print("✓ Metrics rendered!")
        print(f"Event log: {len(log)} chars")
        if len(log) > 0:
            print("✓ Event log rendered!")
        
        print(f"\nConsole: {len(console_logs)}")
        for msg in console_logs:
            print(f"  {msg}")
        
        await browser.close()

asyncio.run(test())
