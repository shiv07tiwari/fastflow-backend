from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService

FILTER_PROMPT = """
You are given a set of data and a condition. Your task is to filter the data based on the condition.
Think step by step and filter the data after thoroughly understanding the condition and the data.

Data:
\\
{data}
\\

Condition:
\\
{condition}
\\

Output Format:
{output_instructions}
Return a json response with key as follows:
- filtered_data: The filtered data based on the condition. Key should be "filtered_data" and value should be a list of filtered data.
- A brief explanation of the condition and how it was applied to the data.
- If no data is filtered, return an empty list.

You must return ONLY the JSON output in this schema. Do not include markdown triple backticks around your output.
"""


class FilterNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='filter',
                name="Filter",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Filter data based on conditions",
                node_type="filter",
                is_active=True,
                inputs=[
                    BaseNodeInput("input_data", InputType.COMMON, "data", is_required=True),
                    BaseNodeInput("condition", InputType.COMMON, "text", is_required=True),
                    BaseNodeInput("output_instructions", InputType.INTERNAL_ONLY, "text"),
                ],
                outputs=["filtered_data"],
                **kwargs
            )

    async def execute(self, input: dict) -> []:
        gemini_service = GeminiService()
        data = input.get("input_data")
        if not isinstance(data, list):
            data = [data]

        condition = input.get("condition")
        output_instructions = input.get("output_instructions")

        prompt = FILTER_PROMPT.format(data=data, condition=condition, output_instructions=output_instructions)
        res = await gemini_service.generate_cached_json_response(prompt, "filter", stream=False, img=False)
        return [
            {
                "filtered_data": i
            } for i in res.get("filtered_data")
        ]
