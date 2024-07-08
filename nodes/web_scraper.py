import time

from nodes.base_node import BaseNode, NodeType
from fastapi.concurrency import run_in_threadpool

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


from nodes.constants import NodeModelTypes

CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"  # noqa: E501


class WebScraperNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='web_scraper',
                name="Web Scraper",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Scrape a website",
                node_type=NodeType.JOIN.value,
                is_active=True,
                inputs=["url"],
                outputs=["response"],
                workflow_node_type=NodeModelTypes.WebScraper,
            )

    def adaptive_wait(self, page, timeout):
        try:
            # First, wait for DOM content loaded
            page.wait_for_load_state('domcontentloaded', timeout=timeout / 2)
            print("DOM content loaded")

            # Then, wait for network to be idle
            page.wait_for_load_state('networkidle', timeout=timeout / 2)
            print("Network idle")
        except PlaywrightTimeoutError:
            # If networkidle times out, proceed anyway
            pass

    def smart_scroll(self, page, timeout):
        last_height = page.evaluate("document.body.scrollHeight")
        content_stabilized = 0
        start_time = time.time()

        while time.time() - start_time < timeout:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)  # Reduced sleep time
            new_height = page.evaluate("document.body.scrollHeight")
            new_content = page.inner_text("body")

            if new_height == last_height and len(new_content) == len(page.inner_text("body")):
                content_stabilized += 1
                if content_stabilized >= 3:  # Content stable for 3 iterations
                    break
            else:
                content_stabilized = 0

            last_height = new_height

    def _scrape_website_content(self, url: str, timeout=30000):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=CHROME_USER_AGENT,
                    viewport={'width': 1920, 'height': 1080},
                )
                page = context.new_page()
                page.set_default_timeout(timeout)
                page.set_default_navigation_timeout(timeout)

                print(f"Scraping content from {url}", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                page.goto(url)

                self.adaptive_wait(page, timeout)
                self.smart_scroll(page, timeout)

                content = page.inner_text("body")
                print(f"Successfully scraped content from {url}", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                browser.close()
                return content
        except Exception as e:
            print(f"Error scraping content from {url}: {e}")
            raise

    async def execute(self, input: dict) -> dict:
        url: str = input.get("url")
        url = url.strip()
        data = await run_in_threadpool(self._scrape_website_content, url, 30000)
        return {"response": data}

    def can_execute(self, inputs: dict) -> bool:
        return True
