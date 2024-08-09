from nodes.base_node import BaseNode, BaseNodeInput, InputType


class HumanApproval(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("data", InputType.EXTERNAL_ONLY, "text", is_required=True),
                BaseNodeInput("is_approved", InputType.INTERNAL_ONLY, "boolean"),
            ]
            super().__init__(
                id='human_approval',
                name="Human Approval",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Human decides if the process should continue",
                node_type="human_approval",
                is_active=True,
                inputs=inputs,
                outputs=["data"],
            )

    async def execute(self, input: dict):
        data = input.get("data")
        is_approved = input.get("is_approved")
        if not isinstance(data, list):
            data = [data]

        return [
            {"data": d} for d in data
        ]