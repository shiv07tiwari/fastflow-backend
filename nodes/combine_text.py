from pydantic import Field

from nodes.base_node import Node, NodeType
from nodes.constants import NodeModelTypes


class CombineTextNode(Node):
    total_inputs_to_combine: int = Field(default=2)

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='combine_text',
                name="Combine Text",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Combine multiple text nodes into one",
                node_type=NodeType.JOIN.value,
                is_active=True,
                inputs=["text"],
                outputs=["combined_text"],
                workflow_node_type=NodeModelTypes.CombineText,
                **kwargs
            )
        self.total_inputs_to_combine = kwargs.get("total_inputs_to_combine", 2)

    async def execute(self, input: dict) -> dict:  # Corrected return type annotation
        combined_text = ""
        for i in range(1, self.total_inputs_to_combine + 1):
            text = input.get(f"text-{i}")
            if text is not None:  # Ensure 'text' is not None
                combined_text += text.strip() + " "  # Corrected 'trim()' to 'strip()'
        return {"combined_text": combined_text.strip()}  # Remove trailing whitespace

    def can_execute(self, inputs: dict) -> bool:
        return len(inputs) == self.total_inputs_to_combine
