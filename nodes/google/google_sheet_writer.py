import os

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services.google import GoogleService


class GoogleSheetWriterNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("column_1", InputType.EXTERNAL_ONLY, "text", is_required=True),
                BaseNodeInput("column_2", InputType.EXTERNAL_ONLY, "text", is_required=True),
                BaseNodeInput("column_3", InputType.EXTERNAL_ONLY, "text", is_required=True),
                BaseNodeInput("column_4", InputType.EXTERNAL_ONLY, "text"),
                BaseNodeInput("headers", InputType.INTERNAL_ONLY, "text", is_required=True),
            ]
            super().__init__(
                id='google_sheet_writer',
                name="Google Sheet Writer",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Write data to a Google Sheet",
                node_type="ACTION",
                inputs=inputs,
                outputs=["sheet_url", "column_1", "column_2", "column_3", "column_4"],
            )

    async def execute(self, input: dict) -> []:
        service = GoogleService()
        _headers: str = input.get("headers")
        headers = _headers.split(",")
        column_1 = input.get("column_1", [])
        column_2 = input.get("column_2", [])
        column_3 = input.get("column_3", [])
        column_4 = input.get("column_4", [])
        max_length = max(len(column_1), len(column_2), len(column_3), len(column_4))

        if isinstance(column_1, str):
            rows = [[column_1, column_2, column_3, column_4]]
        else:
            rows = []
            for i in range(max_length):
                row = []
                if i < len(column_1):
                    row.append(column_1[i])
                if i < len(column_2):
                    row.append(column_2[i])
                if i < len(column_3):
                    row.append(column_3[i])
                if i < len(column_4):
                    row.append(column_4[i])
                rows.append(row)

        sheet = await service.create_sheet(rows, headers)

        return [{
            "sheet_url": str(sheet.get("url")),
            "column_1": ",".join(column_1),
            "column_2": ",".join(column_2),
            "column_3": ",".join(column_3),
            "column_4": ",".join(column_4),
        }]