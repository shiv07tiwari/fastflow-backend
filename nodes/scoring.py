import json

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService

SCORE_PROMPT = """
You are given a set of data and a set of criteria. Your task is to generate a score based on the criteria.
Think step by step and calculate the score after thoroughly understanding the criteria and the data.

The data is as follows:
\\
{data}
\\

The criteria is as follows:
\\
{criteria}
\\

Output a json response with keys as follows:
- score: The score based on the criteria. Key should be "score" and value should be an integer.
- reasoning: The reasoning behind the score. Key should be "reasoning" and value should be a string explaining the score.

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

    async def execute(self, input: dict) -> dict:
        gemini_service = GeminiService()
        data = input.get("data")
        criteria = input.get("criteria")
        prompt = SCORE_PROMPT.format(data=data, criteria=criteria)
        response = await gemini_service.generate_json_response(prompt, name="scoring", stream=False)

        # If response starts with "```json", remove it
        response = response.replace("```json\n", "")

        response_json = json.loads(response)
        print("Scorer response JSON: ", response_json)
        return {
            "score": response_json.get("score", -1),
            "reasoning": response_json.get("reasoning", "Not available")
        }
