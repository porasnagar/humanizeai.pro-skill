"""
Stealth Browser Engine for HumanizeAI.pro using Playwright
Acts as an unbreakable fallback if Cloudflare WAF or Turnstile challenge triggers.
Applies anti-automation evasion patches to bypass bot detection.
"""

import asyncio
import logging
import random
import time
from typing import Optional

logger = logging.getLogger("humanizeai_pro.browser_engine")


class BrowserHumanizeClient:
    """Headless browser client with anti-detection evasion patches.
    Emulates a genuine user interacting with https://www.humanizeai.pro/.
    """

    TARGET_URL = "https://www.humanizeai.pro/"

    def __init__(self, headless: bool = True, timeout_ms: int = 40000):
        self.headless = headless
        self.timeout_ms = timeout_ms

    async def _run_in_browser(self, text: str, style: str = "standard") -> str:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError(
                "Playwright is not installed. Run 'pip install playwright && playwright install chromium'."
            )

        async with async_playwright() as p:
            # Evasion launch arguments
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-browser-side-navigation",
                    "--disable-gpu",
                ],
            )

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="en-US",
                timezone_id="America/New_York",
            )

            # Deep stealth evasion injection
            await context.add_init_script("""
                // Overwrite the `navigator.webdriver` property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                // Mock chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                // Mock plugins & languages
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)

            page = await context.new_page()

            # Intercept API response directly if possible for instant speed
            captured_output = {"text": None}

            async def handle_response(res):
                if "/api/process" in res.url and res.status == 200:
                    try:
                        data = await res.json()
                        results = data.get("result", [])
                        if results and results[0].get("text"):
                            captured_output["text"] = results[0]["text"]
                    except Exception:
                        pass

            page.on("response", handle_response)

            logger.info("Navigating to HumanizeAI Pro via stealth browser...")
            await page.goto(self.TARGET_URL, wait_until="domcontentloaded", timeout=self.timeout_ms)
            await asyncio.sleep(1.5)

            # Dismiss cookie banner if present
            try:
                cookie_btn = page.locator("button:has-text('Accept'), button:has-text('Got it')").first
                if await cookie_btn.is_visible(timeout=1000):
                    await cookie_btn.click()
            except Exception:
                pass

            # Dismiss tooltip if present
            try:
                skip_btn = page.locator("button:has-text('Skip')").first
                if await skip_btn.is_visible(timeout=1000):
                    await skip_btn.click()
            except Exception:
                pass

            # Find input textarea
            textarea = page.locator("textarea").first
            await textarea.wait_for(state="visible", timeout=10000)
            await textarea.fill(text)
            await asyncio.sleep(0.5)

            # Click Humanize AI button
            humanize_btn = page.locator("button:has-text('Humanize')").first
            await humanize_btn.wait_for(state="visible", timeout=10000)
            await humanize_btn.click()

            # Wait for either API response capture or DOM output textarea
            t0 = time.time()
            while time.time() - t0 < (self.timeout_ms / 1000.0):
                if captured_output["text"]:
                    await browser.close()
                    return captured_output["text"]

                # Check textareas in DOM
                textareas = await page.locator("textarea").all()
                if len(textareas) > 1:
                    out_val = await textareas[1].input_value()
                    if out_val and out_val.strip() and out_val.strip() != text.strip():
                        await browser.close()
                        return out_val.strip()

                await asyncio.sleep(0.6)

            await browser.close()
            raise TimeoutError("Browser timed out waiting for humanized output.")

    def humanize_chunk(self, text: str, style: str = "standard") -> str:
        """Synchronous wrapper for browser humanization."""
        return asyncio.run(self._run_in_browser(text, style=style))
