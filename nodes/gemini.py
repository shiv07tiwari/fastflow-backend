from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType
from nodes.constants import NodeModelTypes
from services import GeminiService


class GeminiNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "prompt", is_required=True),
                BaseNodeInput("input_1", InputType.COMMON, "text"),
                BaseNodeInput("input_2", InputType.COMMON, "text"),
                BaseNodeInput("input_3", InputType.EXTERNAL_ONLY, "text"),
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

    async def execute(self, input: dict) -> []:
        service = GeminiService()
        prompt = input.get("prompt")

        response = []
        input_1 = input.get("input_1", [])
        input_2 = input.get("input_2", [])
        input_3 = input.get("input_3", [])

        if not isinstance(input_1, list):
            input_1 = [input_1]
        if not isinstance(input_2, list):
            input_2 = [input_2]
        if not isinstance(input_3, list):
            input_3 = [input_3]

        max_length = max(len(input_1), len(input_2), len(input_3))

        for i in range(max_length):
            _input = {
                "input_1": input_1[i] if i < len(input_1) else "",
                "input_2": input_2[i] if i < len(input_2) else "",
                "input_3": input_3[i] if i < len(input_3) else "",
            }
            formatted_prompt = prompt.format(**_input)
            try:
                llm_response = await service.generate_cached_response(prompt=formatted_prompt, name=self.name, stream=None)
            except Exception as e:
                print(f"Error in executing node {self.name}: {e}")
                raise e
            response.append(str(llm_response))
        return [{
            "response": res
        } for res in response ]

    def can_execute(self, inputs: dict) -> bool:
        for input_key in [id for id in self.inputs]:
            if input_key not in inputs or not inputs[input_key]:
                return False
        return True

