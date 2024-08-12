import asyncio
import json

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService

# TODO: Add company metadata [once we have users, cache this company context]
SOFTWARE_HIRING_PROMPT = """
The provided data is the resume of the candidate applying for position in a software development company.

You have to evaluate the resume based on the following criteria:
1. Genuine projects: They should have worked on genuine projects which demonstrate deep understanding of the technology.
2. Work Experience: They should have relevant work experience in the field.
3. Skills: They should have the required skills for the job.

Sometimes the resumes are very generic, think critically if they have done quality work in the past.
"""

DOMAIN_PROMPT_MAP = {
    "software_hiring": SOFTWARE_HIRING_PROMPT,
}


SCORE_PROMPT = """
You are given a set of data and a set of criteria. Your task is to generate a score based on the criteria.
Think step by step and calculate the score after thoroughly understanding the criteria and the data.
You have to be very critical and precise in your evaluation. Do not give generic scores.

If the criteria is not very clear, think about what would be the best way to evaluate the data and use that
to generate the score.

The data is as follows:
\\
{data}
\\

The criteria is as follows:
\\
{criteria}
\\

Output a json response with keys as follows:
- score: The score out of 100 based on the criteria. Key should be "score" and value should be an integer. 
- reasoning: The reasoning behind the score. Key should be "reasoning" and value should be a string explaining the score.
Start with the candidate's name in your reasoning.

You must return ONLY the JSON output in this schema. Do not include markdown triple backticks around your output.
"""


class ScoringNode(BaseNode):

    def __init__(self, **kwargs):
        inputs = [
            BaseNodeInput("data", InputType.COMMON, "text", is_required=True),
            BaseNodeInput("criteria", InputType.COMMON, "text", is_required=True),
        ]
        super().__init__(
            id='scoring',
            name="Scorer",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Generate a score based on the criteria",
            node_type="ACTION",
            inputs=inputs,
            outputs=["score", "reasoning"],
        )

    async def execute(self, input: dict) -> []:
        gemini_service = GeminiService()

        data = input.get("data")
        criteria = input.get("criteria")


        if isinstance(data, str):
            data = [data]

        results = []
        for _data in data:
            prompt = SCORE_PROMPT.format(data=_data, criteria=criteria)
            results.append(gemini_service.generate_cached_json_response(prompt, name="scoring", stream=False, img=False))

        results = await asyncio.gather(*results)

        return [{"score": str(response_json.get("score")), "reasoning": response_json.get("reasoning")} for response_json in results]
