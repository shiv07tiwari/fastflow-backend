import asyncio
import time

from playwright.async_api import async_playwright, TimeoutError as PlaywrightAsyncTimeoutError
from databases.cache import cache_response

CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"  # noqa: E501


async def _adaptive_wait(page, timeout):
    try:
        # First, wait for DOM content loaded
        await page.wait_for_load_state('domcontentloaded', timeout=timeout / 2)
        print("DOM content loaded")

        # Then, wait for network to be idle
        await page.wait_for_load_state('networkidle', timeout=timeout / 2)
        print("Network idle")
    except PlaywrightAsyncTimeoutError:
        # If networkidle times out, proceed anyway
        pass


async def _smart_scroll(page, timeout):
    last_height = await page.evaluate("document.body.scrollHeight")
    content_stabilized = 0
    start_time = time.time()

    while time.time() - start_time < timeout:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        new_height = await page.evaluate("document.body.scrollHeight")

        if new_height == last_height:
            content_stabilized += 1
            if content_stabilized >= 3:  # Content stable for 3 iterations
                break
        else:
            content_stabilized = 0

        last_height = new_height


@cache_response()
async def scrape_website_content(url: str, timeout=30000) -> str | None:
    if not url or not url.startswith("http"):
        print(f"Invalid URL for scrapping: {url}")
        return None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=CHROME_USER_AGENT,
                viewport={'width': 1920, 'height': 1080},
            )
            page = await context.new_page()
            page.set_default_timeout(timeout)
            page.set_default_navigation_timeout(timeout)

            print(f"Scraping content from {url}", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            await page.goto(url)

            await _adaptive_wait(page, timeout)
            await _smart_scroll(page, timeout)

            content = await page.inner_text("body")
            print(f"Successfully scraped content from {url}", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

            await browser.close()
            return content
    except Exception as e:
        print(f"Error scraping content from {url}: {e}")
