from nodes.base_node import BaseNode
from services import GeminiService

PROMPT = """
Your task is to summarize the following text:
{input_content}

Instructions for summarizing:
- Remove all new lines and weird characters from the response.
- It should not lose the context of the text.

"""


class SummarizerNode(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='summarizer',
                name="Summarizer",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Summarize a text using Gemini",
                node_type="ai",
                is_active=True,
                inputs=["input_content"],
                outputs=["response"],
                workflow_node_type="summarizer",
                **kwargs
            )

    async def execute(self, input: dict) -> dict:
        input_content = input.get("input_content")
        gemini_service = GeminiService()
        formatted_prompt = PROMPT.format(input_content=input_content)
        response = await gemini_service.generate_response(prompt=formatted_prompt, name=self.name, stream=False)

        return {
            "response": response,
        }
