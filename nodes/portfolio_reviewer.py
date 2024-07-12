from nodes.base_node import BaseNode
from services.web_scrapping import scrape_website_content

SUPPORTED_DOMAINS = [
    "https://www.linkedin.com/",
    "https://www.github.com/",
]


def scrape_github_profile(url: str) -> dict:
    return scrape_website_content(url)


class PortfolioReviewer(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='portfolio_reviewer',
                name="Portfolio Reviewer",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Review a portfolio",
                node_type="ai",
                is_active=True,
                inputs=["links"],
                outputs=["response"],
                workflow_node_type="portfolio_reviewer",
                **kwargs
            )

    async def execute(self, input: dict) -> dict:
        links: [] = input.get("links") or []

        combined_data = {}
        for link in links:
            # Check if link contains a supported domain
            if any(domain in link for domain in SUPPORTED_DOMAINS):
                if "github" in link:
                    data = scrape_github_profile(link)
                    combined_data["github"] = data
                else:
                    # Scrape LinkedIn profile
                    pass

        return {"response": links}
