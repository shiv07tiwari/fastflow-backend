from pydantic import Field

from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType


class CombineTextNode(BaseNode):
    total_inputs_to_combine: int = Field(default=2)

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("input_text_1", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("input_text_2", InputType.COMMON, "text"),
            ]
            super().__init__(
                id='combine_text',
                name="Combine Text",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Combine multiple text nodes into one",
                node_type=NodeType.JOIN.value,
                is_active=True,
                inputs=inputs,
                outputs=["combined_text"],
                **kwargs
            )
        self.total_inputs_to_combine = kwargs.get("total_inputs_to_combine", 2)

    async def execute(self, input: dict) -> dict:  # Corrected return type annotation
        combined_text = ""
        for i in range(1, self.total_inputs_to_combine + 1):
            text = input.get(f"input_text_{i}")
            if text is not None:  # Ensure 'text' is not None
                combined_text += text.strip() + " "  # Corrected 'trim()' to 'strip()'
        return {"response": combined_text.strip()}  # Remove trailing whitespace

    def can_execute(self, inputs: dict) -> bool:
        return len(inputs) == self.total_inputs_to_combine
