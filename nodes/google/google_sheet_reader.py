import asyncio
import os

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services.google import GoogleService


class GoogleSheetReaderNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("sheet_url", InputType.COMMON, "text", is_required=True),
            ]
            super().__init__(
                id='google_sheet_reader',
                name="Google Sheet Reader",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Read data from a Google Sheet",
                node_type="ACTION",
                inputs=inputs,
                outputs=["rows", "headers"],
            )

    async def execute(self, input: dict) -> []:
        service = GoogleService()
        sheet_url = input.get("sheet_url")
        if not isinstance(sheet_url, list):
            sheet_url = [sheet_url]

        responses = []
        for url in sheet_url:
            response = service.read_data_from_sheet(url)
            responses.append(response)

        responses = await asyncio.gather(*responses)

        return [{
            "headers": str(data[0]) if len(data) > 0 else [],
            "rows": str(data[1:]) if len(data) > 1 else []
        } for data in responses]