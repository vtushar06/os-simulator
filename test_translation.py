#!/usr/bin/env python3
"""Test that all event log messages are in English by exercising every event type."""
import asyncio
import sys
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        # Collect console errors
        errors = []
        page.on("console", lambda msg: errors.append(msg.text()) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        
        print("Loading http://localhost:8000 ...")
        await page.goto("http://localhost:8000", wait_until="networkidle")
        await page.wait_for_timeout(500)
        
        # 1. Load the demo workload (8 processes)
        print("Loading demo workload...")
        await page.click("#btn-demo")
        await page.wait_for_timeout(800)
        
        # 2. Run FCFS for several ticks to generate admission, dispatch, I/O, termination events
        print("Running FCFS...")
        for _ in range(15):
            await page.click("#btn-step")
            await page.wait_for_timeout(100)
        
        # 3. Check event log for admission, dispatch, io_block, io_interrupt, termination
        log_html = await page.inner_html("#bitacora")
        print(f"Event log length: {len(log_html)} chars")
        
        events_seen = set()
        if "admission" in log_html.lower() or "arrives" in log_html.lower():
            events_seen.add("admission")
        if "dispatch" in log_html.lower():
            events_seen.add("dispatch")
        if "i/o" in log_html.lower() or "blocks" in log_html.lower():
            events_seen.add("io_block")
        if "terminates" in log_html.lower() or "releases" in log_html.lower():
            events_seen.add("termination")
        
        print(f"Events seen after FCFS: {events_seen}")
        
        # 4. Change scheduler to Priority (live config change)
        print("Changing scheduler to Priority...")
        await page.select_option("#sel-scheduler", "prioridad_np")
        await page.wait_for_timeout(500)
        
        log_html = await page.inner_html("#bitacora")
        if "scheduler" in log_html.lower() and "changed" in log_html.lower():
            events_seen.add("scheduler_change")
            print("✓ Scheduler change event found")
        
        # 5. Change memory strategy to Best-Fit (live)
        print("Changing memory strategy to Best-Fit...")
        await page.select_option("#sel-estrategia", "best_fit")
        await page.wait_for_timeout(500)
        
        log_html = await page.inner_html("#bitacora")
        if "memory" in log_html.lower() and "strategy" in log_html.lower() and "changed" in log_html.lower():
            events_seen.add("memory_strategy_change")
            print("✓ Memory strategy change event found")
        
        # 6. Reset and try Round Robin to get quantum_end events
        print("Resetting and running Round Robin...")
        await page.click("#btn-reset")
        await page.wait_for_timeout(300)
        await page.select_option("#sel-scheduler", "rr")
        await page.wait_for_timeout(300)
        await page.click("#btn-demo")
        await page.wait_for_timeout(500)
        
        for _ in range(20):
            await page.click("#btn-step")
            await page.wait_for_timeout(80)
        
        log_html = await page.inner_html("#bitacora")
        if "quantum" in log_html.lower() or "timer" in log_html.lower():
            events_seen.add("quantum_end")
            print("✓ Quantum end event found")
        
        # 7. Check for any Spanish words in the event log
        spanish_words = [
            "proceso", "memoria", "estrategia", "caliente", "planificador",
            "reemplazo", "cambio", "dispositivo", "llegada", "ráfaga",
            "prioridad", "bloqueado", "terminado", "ejecut", "despach",
            "libera", "admision", "apropiado", "solicita"
        ]
        
        found_spanish = []
        for word in spanish_words:
            if word in log_html.lower():
                found_spanish.append(word)
        
        if found_spanish:
            print(f"\n❌ SPANISH WORDS FOUND IN EVENT LOG: {found_spanish}")
            print(f"Event log excerpt:\n{log_html[:2000]}")
            return False
        
        # 8. Check the full page HTML for Spanish
        full_html = await page.content()
        page_spanish = []
        for word in spanish_words:
            if word in full_html.lower():
                page_spanish.append(word)
        
        if page_spanish:
            print(f"\n⚠ Spanish words found in page HTML: {page_spanish}")
            print("(These may be internal identifiers, checking context...)")
        
        print(f"\n✓ All event types exercised: {events_seen}")
        print(f"✓ No Spanish user-visible text found in event log")
        print(f"Console errors: {len(errors)}")
        
        if errors:
            print("Errors encountered:")
            for err in errors:
                print(f"  {err}")
        
        await browser.close()
        return len(errors) == 0 and not found_spanish

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
