import time

from nodes.base_node import BaseNode, NodeType
from fastapi.concurrency import run_in_threadpool

from playwright.sync_api import sync_playwright

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

    def _scrape_website_content(self, url: str, timeout=3000000000):
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

                page.goto(url)

                # Wait for the content to load
                page.wait_for_load_state('networkidle')

                # Scroll to ensure all content is loaded
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)  # Allow time for any lazy-loaded content

                content = page.inner_text("body")

                browser.close()
                print(f"Successfully scraped content from {url}")
                return content
        except Exception as e:
            print(f"Error scraping content from {url}: {e}")
            browser.close()
            raise  # Re-raise the exception for the retry decorator

    async def execute(self, input: dict) -> dict:
        url: str = input.get("url")
        url = url.strip()
        data = await run_in_threadpool(self._scrape_website_content, url, 300000000)
        return {"response": data}

    def can_execute(self, inputs: dict) -> bool:
        return True
