import asyncio

from nodes.base_node import BaseNode, BaseNodeInput, InputType, NodeType
from services import GeminiService


class ExtractorNode(BaseNode):

    def __init__(self,  **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("input_text", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "text"),
            ]
            super().__init__(
                id='extractor',
                name="Extractor",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Extract information from a text",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["extracted_text"],
                **kwargs
            )

    async def execute(self, input: dict) -> []:
        prompt = input.get("prompt")
        input_text = input.get("input_text")
        if not isinstance(input_text, list):
            input_text = [input_text]

        BASE_PROMPT = """
        Your task is to extract information from the given text.
        {text}
        
        The following prompt contains information about what is to be extracted
        {prompt}
        
        Output Format:
        - If you find multiple pieces of information, return a list of dictionaries, with key value pairs
        - If you find a single information, return a single dictionary with key value pairs
        """
        service = GeminiService()
        extracted_text = []

        for text in input_text:
            formatted_prompt = BASE_PROMPT.format(prompt=prompt,text=text)
            promise = service.generate_cached_response(formatted_prompt, name=self.name, stream=False)
            extracted_text.append(promise)

        extracted_text = await asyncio.gather(*extracted_text)
        return [
            {"extracted_text": text} for text in extracted_text
        ]
