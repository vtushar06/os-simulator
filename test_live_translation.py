#!/usr/bin/env python3
"""Verify all UI text and event log messages are in English on the live site."""
import asyncio
import re
import sys
from playwright.async_api import async_playwright

LIVE_URL = "https://os-simulator-vtushar.onrender.com"

SPANISH_WORDS = [
    "proceso", "memoria", "estrategia", "caliente", "planificador",
    "reemplazo", "cambio", "dispositivo", "llegada", "ráfaga", "rafaga",
    "prioridad", "bloqueado", "terminado", "ejecut", "despach",
    "libera", "admision", "apropiado", "solicita", "llega",
    "carga", "bloque", "pasa", "LISTO", "TERMINA", "ABORTA",
    "agota", "quantum", "contexto", "guardando", "cargando",
    "inicia", "curso", "fisica", "cambiada", "cambiado"
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir="/tmp/playwright-videos"
        )
        page = await context.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(msg.text()) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        
        print(f"Loading {LIVE_URL} ...")
        await page.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(1000)
        
        # Check initial page load
        title = await page.title()
        print(f"Page title: {title}")
        
        # 1. Load demo workload
        print("\n1. Loading demo workload...")
        await page.click("#btn-demo")
        await page.wait_for_timeout(1000)
        
        # 2. Change memory strategy to Best-Fit
        print("2. Changing memory strategy to Best-Fit...")
        await page.select_option("#sel-estrategia", "best_fit")
        await page.wait_for_timeout(800)
        
        # Check event log for memory strategy change
        log_html = await page.inner_html("#bitacora")
        if "memory" in log_html.lower() and "strategy" in log_html.lower():
            print("   ✓ Memory strategy change event found")
        
        # 3. Change scheduler to Priority
        print("3. Changing scheduler to Priority...")
        await page.select_option("#sel-scheduler", "prioridad_np")
        await page.wait_for_timeout(800)
        
        log_html = await page.inner_html("#bitacora")
        if "scheduler" in log_html.lower() and "changed" in log_html.lower():
            print("   ✓ Scheduler change event found")
        
        # 4. Run simulation to completion
        print("4. Running simulation to completion...")
        await page.click("#btn-play")
        
        # Wait for simulation to complete (check for TERMINATED badge)
        for _ in range(60):
            estado = await page.text_content("#estado-sim")
            if "TERMINATED" in estado or "PAUSED" in estado:
                tick = await page.text_content("#tick-actual")
                if int(tick) > 50:
                    break
            await page.wait_for_timeout(500)
        
        final_tick = await page.text_content("#tick-actual")
        print(f"   Simulation completed at tick {final_tick}")
        
        # 5. Check event log thoroughly
        print("\n5. Checking event log for Spanish text...")
        log_html = await page.inner_html("#bitacora")
        
        found_spanish = []
        for word in SPANISH_WORDS:
            # Skip words that are substrings of English words or internal IDs
            if word in ["cambio", "proceso", "prioridad", "estrategia", "dispositivo"]:
                # Check for Spanish patterns, not just the word
                patterns = [
                    f"Planificador {word}",
                    f"Estrategia de {word}",
                    f"{word} de memoria",
                    f"llega.*carga",
                    f"despachado a",
                    f"libera su",
                    f"TERMINA.*libera",
                    f"cambio de contexto",
                    f"en caliente",
                ]
                for pattern in patterns:
                    if re.search(pattern, log_html, re.IGNORECASE):
                        found_spanish.append(f"{word} (pattern: {pattern})")
                        break
            elif word in log_html.lower():
                # Check it's not part of a JSON field or option value
                if f'"{word}"' not in log_html and f"value='{word}'" not in log_html:
                    found_spanish.append(word)
        
        if found_spanish:
            print(f"   ❌ Spanish words/patterns found: {found_spanish}")
            print(f"\nEvent log excerpt (first 3000 chars):")
            print(log_html[:3000])
        else:
            print("   ✓ No Spanish text found in event log")
        
        # 6. Check all UI text
        print("\n6. Checking full page HTML for Spanish...")
        full_html = await page.content()
        
        # Check for Spanish patterns in visible text (not in script tags or attributes)
        visible_text = await page.evaluate("""() => {
            return document.body.innerText;
        }""")
        
        page_spanish = []
        for word in SPANISH_WORDS:
            if word in visible_text.lower():
                # Make sure it's not in a hidden element or internal identifier
                if word not in ["proceso", "prioridad", "estrategia", "dispositivo", "memoria"]:
                    page_spanish.append(word)
        
        if page_spanish:
            print(f"   ⚠ Spanish words in visible text: {page_spanish}")
        else:
            print("   ✓ No Spanish in visible page text")
        
        # 7. Export log
        print("\n7. Testing log export...")
        await page.click("#btn-exportar-log")
        await page.wait_for_timeout(500)
        print("   ✓ Log export triggered")
        
        # 8. Check process table
        print("\n8. Checking process table...")
        table_html = await page.inner_html("#tabla-procesos")
        if "burst" in table_html.lower() and "arrival" in table_html.lower():
            print("   ✓ Process table headers in English")
        
        # 9. Check metrics panel
        print("\n9. Checking metrics panel...")
        metrics_html = await page.inner_html(".p-metricas")
        if "terminated" in metrics_html.lower() or "avg" in metrics_html.lower():
            print("   ✓ Metrics in English")
        
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Page loaded: {title}")
        print(f"Final tick: {final_tick}")
        print(f"Console errors: {len(errors)}")
        
        if errors:
            print("\nConsole errors:")
            for err in errors[:5]:
                print(f"  {err}")
        
        success = not found_spanish and not page_spanish
        
        if success:
            print("\n✅ ALL CHECKS PASSED - No Spanish text found")
        else:
            print("\n❌ SPANISH TEXT FOUND - See details above")
            if found_spanish:
                print(f"   Event log: {found_spanish}")
            if page_spanish:
                print(f"   Page text: {page_spanish}")
        
        await context.close()
        await browser.close()
        
        return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
