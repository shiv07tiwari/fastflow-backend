from nodes.base_node import BaseNode, NodeType
from fastapi.concurrency import run_in_threadpool


from nodes.constants import NodeModelTypes
from services.web_scrapping import scrape_website_content

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

    async def execute(self, input: dict) -> dict:
        url: str = input.get("url")
        url = url.strip()
        data = await run_in_threadpool(scrape_website_content, url, 30000)
        return {"response": data}

    def can_execute(self, inputs: dict) -> bool:
        return True
