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

Output Format:
Return a JSON object with the following keys:
- company_name: The name of the company
- contact_email: The contact email of the company
- summary: A summary of the company information in markdown format
- primary_industry: The primary industry of the company

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
            outputs=["company_name", "contact_email", "summary", "primary_industry"],
        )

    async def _generate_company_summary(self, company_name, company_website):
        gemini_service = GeminiService()
        company_urls: list[str] = get_urls_for_search_query(f"Company ${company_name}", 10)

        valid_urls = []

        for url in company_urls:
            base_url = url.lstrip("https://").lstrip("http://").split("/")[0]
            company_name_components = [name.lower() for name in company_name.split(" ")]
            if url == company_website:
                valid_urls.append(url)
            if "crunchbase" in url:
                valid_urls.append(url)
            if "livemint" in url:
                valid_urls.append(url)
            if "tracxn" in url:
                valid_urls.append(url)
            if "economictimes" in url:
                valid_urls.append(url)
            if "yourstory" in url:
                valid_urls.append(url)
            for component in company_name_components:
                if component in base_url:
                    valid_urls.append(url)
                    break

        valid_urls.append(company_website)

        _web_data = []
        for url in valid_urls:
            data = scrape_website_content(url)
            _web_data.append(data)

        web_data = await asyncio.gather(*_web_data)
        web_data_text_blob = " \\ Scraped Information \\ ".join([data for data in web_data if data is not None])
        response = await gemini_service.generate_cached_json_response(PROMPT.format(web_data=web_data_text_blob),
                                                          name="company_enrichment", stream=False, img=False)
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
                "summary": summary.get("summary"),
                "primary_industry": summary.get("primary_industry"),
                "contact_email": summary.get("contact_email"),
            })

        return response

    async def can_execute(self, *args, **kwargs):
        return True
