from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType
from nodes.constants import NodeModelTypes
from services import GeminiService


class GeminiNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "text"),
                BaseNodeInput("input_1", InputType.EXTERNAL_ONLY, "text"),
                BaseNodeInput("input_2", InputType.EXTERNAL_ONLY, "text"),
            ]
            super().__init__(
                id='gemini',
                name="Gemini",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Generate a Response from Gemini AI",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["response"],
                **kwargs
            )

    def format_prompt(self, prompt: str, input: dict) -> str:
        # Filter out keys that are in self.inputs and not in the prompt
        formatted_input = {k: v for k, v in input.items()
                           if k in self.inputs and f"{{{k}}}" in prompt}

        # Use ** to unpack the dictionary as keyword arguments
        return prompt.format(**formatted_input)

    async def execute(self, input: dict) -> {}:
        service = GeminiService()
        for keys in self.inputs:
            if keys not in input:
                print("WARNING: ", keys, " not in input")

        prompt = input.get("prompt")
        formatted_prompt = self.format_prompt(prompt, input)

        try:
            response = await service.generate_response(prompt=formatted_prompt, name=self.name, stream=None)
        except Exception as e:
            print(f"Error in executing node {self.name}: {e}")
            raise e
        return {
            "response": response
        }

    def can_execute(self, inputs: dict) -> bool:
        for input_key in self.inputs:
            if input_key not in inputs or not inputs[input_key]:
                return False
        return True

