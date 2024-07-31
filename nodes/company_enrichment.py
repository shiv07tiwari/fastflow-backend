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
            BaseNodeInput("company_name", InputType.COMMON, "text", is_required=True),
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

    async def _generate_company_summary(self, company_name, company_website):
        gemini_service = GeminiService()
        company_urls = get_urls_for_search_query(f"Company ${company_name}", 3)
        company_urls.append(company_website)

        _web_data = []
        for url in company_urls:
            data = scrape_website_content(url)
            _web_data.append(data)

        web_data = await asyncio.gather(*_web_data)
        web_data_text_blob = " \\ Scraped Information \\ ".join([data for data in web_data if data is not None])
        response = await gemini_service.generate_response(PROMPT.format(web_data=web_data_text_blob),
                                                          name="company_enrichment", stream=False)
        return response

    async def execute(self, input: dict) -> []:
        company_name = input.get("company_name")
        company_website = input.get("company_url", None) # TODO: Validate this URL

        if not isinstance(company_website, list):
            company_website = [company_website]
        if not isinstance(company_name, list):
            company_name = [company_name]

        data_pairs = list(zip(company_name, company_website))

        response = []
        for name, website in data_pairs:
            summary = await self._generate_company_summary(name, website)
            response.append({
                "company_name": name,
                "summary": summary,
                "primary_industry": ""
            })

        return response

    async def can_execute(self, *args, **kwargs):
        return True
