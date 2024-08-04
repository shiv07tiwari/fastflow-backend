import asyncio
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

Return the answers in a JSON with the following keys:
- name
- current_employer
- work_experience
- skills
- github_url [If you can not find one, return empty string]
- linkedin_url [If you can not find one, return empty string]


The resume is as follows:
\\\
{resume}
\\\

You must return ONLY the JSON output in requested schema. Do not include markdown triple backticks around your output.
"""

CONSOLIDATOR_PROMPT = """
The following is the extracted information from various sources about a candidate applying for a job as a software engineer.
Your task is to format the information into a human-readable report.
The report should be elaborate and should include all the important details.
Divide the report into following sections:
- Personal Information
- Work Experience
- Skills
- Strengths
- Weaknesses
- Github Information

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
            BaseNodeInput("input_resume", InputType.EXTERNAL_ONLY, "text", is_required=True),
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
            outputs=["name", "response"],
        )

    async def google_search_for_github_url(self, name, current_employer):
        google_search_text = f"{name} {current_employer} Github"
        urls = get_urls_for_search_query(google_search_text)
        for url in urls:
            if is_github_profile_url(url):
                return url
        return None

    async def _process_resume(self, file_content, instructions):
        """
        TODO: Test this
        """
        gemini_service = GeminiService()
        formatted_prompt = EXTRACTOR_PROMPT.format(resume=file_content, instructions=instructions)
        extracted_information = await gemini_service.generate_cached_json_response(formatted_prompt, name="resume_analysis",
                                                                              stream=False)

        name = extracted_information.get("name")
        current_employer = extracted_information.get("current_employer")
        github_url = extracted_information.get("github_url")
        linkedin_url = extracted_information.get("linkedin_url")
        print("LLM Found github url", github_url)

        if not github_url and False:  # TODO: Remove this False
            github_url = await self.google_search_for_github_url(name, current_employer)

        print(f"awaiting website content {github_url}")
        github_data = await scrape_website_content(github_url, 30000)

        resume_data = extracted_information["work_experience"] + extracted_information["skills"]
        consolidator_prompt = CONSOLIDATOR_PROMPT.format(resume=resume_data, github=github_data,
                                                         instructions=instructions)
        response = await gemini_service.generate_cached_response(consolidator_prompt, name="resume_analysis",
                                                                 stream=False)

        return response, name

    async def execute(self, input: dict) -> []:
        file_output = input.get("input_resume")
        instructions = input.get("instructions")

        if isinstance(file_output, str):
            file_output = [file_output]

        responses = []
        for file in file_output:
            response = self._process_resume(file, instructions)
            responses.append(response)

        responses = await asyncio.gather(*responses)
        return [{"response": response, "name": name} for response, name in responses]
