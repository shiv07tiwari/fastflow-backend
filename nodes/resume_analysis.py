import json

from nodes.file_reader import FileReader
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
"""


class ResumeAnalysisNode(FileReader):

    def __init__(self, **kwargs):
        super().__init__(
            id='resume_analysis',
            name="Resume Analysis",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Analyze a resume to extract key information",
            node_type="ai",
            is_active=True,
            inputs=["file_path"],
            outputs=["response"],
            workflow_node_type="file_reader",
        )

    async def execute(self, input: dict) -> dict:
        file_output = await super().execute(input)
        gemini_service = GeminiService()
        formatted_prompt = EXTRACTOR_PROMPT.format(resume=file_output['response'])
        extracted_information = await gemini_service.generate_response(formatted_prompt, name="resume_analysis", stream=False)
        extracted_information_json = json.loads(extracted_information)

        github_data = await run_in_threadpool(scrape_website_content, extracted_information_json['github'], 30000)

        portfolio_data = await run_in_threadpool(scrape_website_content, extracted_information_json['portfolio'], 30000)

        project_data = await run_in_threadpool(scrape_website_content, extracted_information_json['project'], 30000)


        resume_data = extracted_information_json["work_experience"] + extracted_information_json["skills"]
        consolidator_prompt = CONSOLIDATOR_PROMPT.format(resume=resume_data, github=github_data, portfolio=portfolio_data, project=project_data)
        response = await gemini_service.generate_response(consolidator_prompt, name="resume_analysis", stream=False)


        return {
            "response": response,
        }
