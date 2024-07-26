from nodes.base_node import BaseNode, BaseNodeInput, InputType
from nodes.constants import NodeModelTypes


class UserInputNode(BaseNode):
    """
    Used to accept an input from user/api
    """
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("input", InputType.COMMON, "text", is_required=True),
            ]
            super().__init__(
                id='user_input',
                name="User Input",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Accepts an input from user",
                node_type="input",
                is_active=True,
                inputs=inputs,
                outputs=["response"],
                **kwargs
            )

    async def execute(self, input: dict) -> dict:
        return {"response": input.get("input")}

    def can_execute(self, inputs: dict) -> bool:
        return True
