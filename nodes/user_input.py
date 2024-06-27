from nodes.base_node import Node


class UserInputNode(Node):
    """
    Used to accept an input from user/api
    """
    def __init__(self, **kwargs):
        super().__init__(
            id='user_input',
            name="User Input",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Accepts an input from user",
            node_type="input",
            is_active=True,
            inputs=["input"],
            outputs=["response"],
            **kwargs
        )

    def execute(self, input: dict) -> dict:
        return {"response": input.get("input")}

    def can_execute(self, inputs: dict) -> bool:
        return True