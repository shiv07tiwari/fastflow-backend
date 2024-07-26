import asyncio

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService
from services.google import get_urls_for_search_query
from services.web_scrapping import scrape_website_content

PROMPT = """
You are given web data from multiple sources about a company.
Your task is to consolidate the information to make it as human readable as possible.

Your response should be formatted like a report and should be easy to read.

The web data is as follows:
\\\
{web_data}
\\\

"""


class CompanyEnrichmentNode(BaseNode):

    def __init__(self, **kwargs):
        inputs = [
            BaseNodeInput("company_name", InputType.COMMON, "text"),
            BaseNodeInput("company_url", InputType.COMMON, "text"),
        ]
        super().__init__(
            id='company_enrichment',
            name="Company Enrichment",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Enrich company information",
            node_type="ai",
            is_active=True,
            inputs=inputs,
            outputs=["company_name", "summary", "primary_industry"],
        )

    async def execute(self, input: dict) -> dict:
        gemini_service = GeminiService()
        company_name = input.get("company_name")
        # TODO: Validate this URL
        company_website = input.get("company_url", None)

        company_urls = get_urls_for_search_query(f"Company ${company_name}", 3)
        company_urls.append(company_website)

        # TODO: Filter garbage URLs

        _web_data = []
        for url in company_urls:
            data = scrape_website_content(url)
            _web_data.append(data)

        web_data = await asyncio.gather(*_web_data)

        # Combine all the web data

        web_data_text_blob = " \\ Scraped Information \\ ".join([data for data in web_data if data is not None])
        response = await gemini_service.generate_response(PROMPT.format(web_data=web_data_text_blob),
                                                          name="company_enrichment", stream=False)

        return {
            "company_name": company_name,
            "summary": response,
            "primary_industry": ""
        }
