import json

from nodes.base_node import BaseNode
from services import GeminiService
from services.web_scrapping import scrape_website_content
from fastapi.concurrency import run_in_threadpool

EXTRACTOR_PROMPT = """
The following is the resume of a candidate applying for a job as a software engineer.
Your task is to extract some key information from the resume and answer the following questions:

1. What is the candidate's name?
2. What is the candidate's github profile URL? Make sure it is a valid Github URL, if not present return None
3. What is the candidate's linkedin profile?
4. Summarize and return a list of candidates work experience.
5. Summarize and return a list of candidates skills.
6. What is the candidate's portfolio website? If not present return None
7. Has he linked any projects in his resume. If yes, give a valid URL to one of the projects.

Return the answers in a dictionary with the following keys:
- name
- github
- linkedin
- work_experience
- skills
- portfolio
- project

Please format the response to not contain any next lines or special characters.
ENSURE THAT THE RESPONSE IS IN JSON FORMAT WHICH CAN BE PARSED BY PYTHON USING json.loads()

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

PORTFOLIO INFORMATION:
\\\
{portfolio}
\\\

PROJECT INFORMATION:
\\\
{project}
\\\

Additional Instructions:
{instructions}
"""


class ResumeAnalysisNode(BaseNode):

    def __init__(self, **kwargs):
        super().__init__(
            id='resume_analysis',
            name="Resume Analysis",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Analyze a resume to extract key information",
            node_type="ai",
            is_active=True,
            inputs=["input_resume", "instructions"],
            outputs=["response", "links"],
        )

    async def _process_resume(self, file_content, instructions):
        gemini_service = GeminiService()
        formatted_prompt = EXTRACTOR_PROMPT.format(resume=file_content, instructions=instructions)
        extracted_information = await gemini_service.generate_cached_response(formatted_prompt, name="resume_analysis",
                                                                              stream=False)
        extracted_information_json = json.loads(extracted_information)

        github_url = extracted_information_json.get("github")
        linkedin_url = extracted_information_json.get("linkedin")
        portfolio_url = extracted_information_json.get("portfolio")
        project_url = extracted_information_json.get("project")

        github_data = await run_in_threadpool(scrape_website_content, github_url, 30000)

        portfolio_data = await run_in_threadpool(scrape_website_content, portfolio_url, 30000)

        project_data = await run_in_threadpool(scrape_website_content, project_url, 30000)

        resume_data = extracted_information_json["work_experience"] + extracted_information_json["skills"]
        consolidator_prompt = CONSOLIDATOR_PROMPT.format(resume=resume_data, github=github_data,
                                                         portfolio=portfolio_data, project=project_data)
        response = await gemini_service.generate_response(consolidator_prompt, name="resume_analysis", stream=False)

        return response, [github_url, linkedin_url, portfolio_url, project_url]

    async def execute(self, input: dict) -> dict:
        file_output = input.get("input_resume")
        instructions = input.get("instructions")

        response, links = await self._process_resume(file_output, instructions)

        return {
            "response": response,
            "links": links
        }
