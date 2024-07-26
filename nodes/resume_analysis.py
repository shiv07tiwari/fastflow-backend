import json
import re

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService
from services.google import get_urls_for_search_query
from services.web_scrapping import scrape_website_content

EXTRACTOR_PROMPT = """
The following is the resume of a candidate applying for a job as a software engineer.
Your task is to extract some key information from the resume and answer the following questions:

1. What is the candidate's name?
2. What is the candidate's current employer? Only return the name of the employer.
4. Summarize and return a list of candidates work experience.
5. Summarize and return a list of candidates skills.

Return the answers in a dictionary with the following keys:
- name
- current_employer
- work_experience
- skills

Please format the response to not contain any next lines or special characters.
ENSURE THAT THE RESPONSE IS IN JSON FORMAT WHICH CAN BE PARSED BY PYTHON USING json.loads(). Do not add anything extra to the response.

The resume is as follows:
\\\
{resume}
\\\
"""

CONSOLIDATOR_PROMPT = """
The following is the extracted information from various sources about a candidate applying for a job as a software engineer.
Your task is to consolidate the information to make it as human readable as possible.
Remove all new lines and weird characters from the response.

RESUME INFORMATION:
\\\
{resume}
\\\

GITHUB INFORMATION:
\\\
{github}
\\\

Additional Instructions:
{instructions}
"""


def is_github_profile_url(url):
    regex = r"^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$"
    return bool(re.match(regex, url))

def is_portfolio_url(url):
    # TODO: How?
    return False

def is_linkedin_url(url):
    return False


class ResumeAnalysisNode(BaseNode):

    def __init__(self, **kwargs):
        inputs = [
            BaseNodeInput("input_resume", InputType.EXTERNAL_ONLY, "text"),
            BaseNodeInput("instructions", InputType.INTERNAL_ONLY, "text"),
        ]
        super().__init__(
            id='resume_analysis',
            name="Resume Analysis",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Analyze a resume to extract key information",
            node_type="ai",
            is_active=True,
            inputs=inputs,
            outputs=["response", "links"],
        )

    async def _process_resume(self, file_content, instructions):
        gemini_service = GeminiService()
        formatted_prompt = EXTRACTOR_PROMPT.format(resume=file_content, instructions=instructions)
        extracted_information = await gemini_service.generate_response(formatted_prompt, name="resume_analysis",
                                                                              stream=False)
        extracted_information_json = json.loads(extracted_information)

        name = extracted_information_json.get("name")
        current_employer = extracted_information_json.get("current_employer")

        google_search_text = f"{name} {current_employer} Github"
        urls = get_urls_for_search_query(google_search_text)

        github_url = None
        for url in urls:
            if is_github_profile_url(url):
                github_url = url
                break

        github_data = await scrape_website_content(github_url, 30000)

        resume_data = extracted_information_json["work_experience"] + extracted_information_json["skills"]
        consolidator_prompt = CONSOLIDATOR_PROMPT.format(resume=resume_data, github=github_data, instructions=instructions)
        response = await gemini_service.generate_response(consolidator_prompt, name="resume_analysis", stream=False)

        return response, [github_url]

    async def execute(self, input: dict) -> dict:
        file_output = input.get("input_resume")
        instructions = input.get("instructions")

        response, links = await self._process_resume(file_output, instructions)

        return {
            "response": response,
            "links": links
        }
