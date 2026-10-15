#!/usr/bin/env python3
"""Test each import individually."""
import asyncio
from playwright.async_api import async_playwright

modules = [
    "api.js",
    "controls.js", 
    "editor.js",
    "render_comparativa.js",
    "render_cpu.js",
    "render_procesos.js",
    "render_gantt.js",
    "render_memoria.js",
    "render_io.js",
    "render_metricas.js",
    "render_log.js",
    "state.js",
]

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        await page.goto("http://localhost:8000/?v=test2")
        await page.wait_for_timeout(1000)
        
        for mod in modules:
            result = await page.evaluate(f"""
                async () => {{
                    try {{
                        const m = await import('/static/js/{mod}');
                        return {{ ok: true, exports: Object.keys(m).length }};
                    }} catch (e) {{
                        return {{ ok: false, error: e.message }};
                    }}
                }}
            """)
            status = "✓" if result.get("ok") else "✗"
            if result.get("ok"):
                print(f"{status} {mod:25s} ({result.get('exports')} exports)")
            else:
                print(f"{status} {mod:25s} ERROR: {result.get('error')}")
        
        await browser.close()

asyncio.run(test())
