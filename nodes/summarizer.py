import asyncio

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService

PROMPT = """
Your task is to summarize the following text:
{input_content}

Instructions for summarizing:
- Think about the content of the text and only summarize the important parts.
- It should not lose the context of the text.
- It should be human readable and easy to understand.

"""


class SummarizerNode(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("input_content", InputType.COMMON, "text", is_required=True),
            ]
            super().__init__(
                id='summarizer',
                name="Summarizer",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Summarize a text using Gemini",
                node_type="ai",
                is_active=True,
                inputs=inputs,
                outputs=["response"],
                **kwargs
            )

    async def execute(self, input: dict) -> list:
        input_content = input.get("input_content")
        if isinstance(input_content, str):
            input_content = [input_content]

        gemini_service = GeminiService()

        responses = []
        for content in input_content:
            formatted_prompt = PROMPT.format(input_content=content)
            response = gemini_service.generate_cached_response(prompt=formatted_prompt, name=self.name, stream=False)
            responses.append(response)
        responses = await asyncio.gather(*responses)

        return [{"response": response} for response in responses]