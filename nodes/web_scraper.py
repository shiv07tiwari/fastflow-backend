from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType

from services.web_scrapping import scrape_website_content

CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"  # noqa: E501


class WebScraperNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("url", InputType.COMMON, "url", is_required=True),
            ]
            super().__init__(
                id='web_scraper',
                name="Web Scraper",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Scrape a website",
                node_type=NodeType.JOIN.value,
                is_active=True,
                inputs=inputs,
                outputs=["data"],
            )

    async def execute(self, input: dict) -> []:
        url = input.get("url", '')
        if not isinstance(url, list):
            url = [url]

        response = []

        for u in url:
            data = await scrape_website_content(u, 30000)
            response.append({"data": data})

        return response

    def can_execute(self, inputs: dict) -> bool:
        return True
