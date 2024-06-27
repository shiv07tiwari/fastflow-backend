from nodes.base_node import Node, NodeType
from services import GeminiService


class GeminiNode(Node):
    def __init__(self, **kwargs):
        super().__init__(
            id='gemini',
            name="Gemini",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Generate a Response from Gemini AI",
            node_type=NodeType.AI,
            is_active=True,
            inputs=["prompt", "stream"],
            outputs=["response"],
            **kwargs
        )

    async def execute(self, input: dict) -> {}:
        service = GeminiService()
        for keys in input.keys():
            if keys not in self.inputs:
                raise ValueError(f"Invalid variable {keys} for node {self.name}")

        prompt = input.get("prompt")

        response = await service.generate_response(prompt=prompt, name=self.name, stream=None)
        return {
            "response": response.text
        }

    def can_execute(self, inputs: dict) -> bool:
        for input_key in self.inputs:
            if input_key not in inputs:
                return False
        return True

