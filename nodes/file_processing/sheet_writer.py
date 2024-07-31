import os
import uuid

import pandas as pd
from nodes.base_node import BaseNode, BaseNodeInput, InputType


class SheetWriterNode(BaseNode):

    def __init__(self, **kwargs):
        inputs = [
            BaseNodeInput("column_1", InputType.EXTERNAL_ONLY, "text", is_required=True),
            BaseNodeInput("column_2",  InputType.EXTERNAL_ONLY, "text", is_required=True),
            BaseNodeInput("column_3",  InputType.EXTERNAL_ONLY, "text", is_required=True),
            BaseNodeInput("headers",  InputType.INTERNAL_ONLY, "text", is_required=True),
        ]
        super().__init__(
            id='sheet_writer',
            name="Sheet Writer",
            icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
            description="Write data to an Excel Sheet",
            node_type="ACTION",
            inputs=inputs,
            outputs=["sheet_url"],
        )

    def create_csv(self, headers, rows, filename='output'):
        random_id = uuid.uuid4().hex[:6]
        filename = f'{filename}-{random_id}.csv'
        # Convert your headers and rows into a Pandas DataFrame, then save as CSV
        df = pd.DataFrame(rows, columns=headers)
        df.to_csv(filename, index=False)
        return filename

    async def execute(self, input: dict) -> dict:
        from databases.repository.file_upload import FileUploadRepository
        repo = FileUploadRepository()
        # Write to Google Sheet
        _headers: str = input.get("headers")
        headers = _headers.split(",")
        column_1 = input.get("column_1", [])
        column_2 = input.get("column_2", [])
        column_3 = input.get("column_3", [])
        max_length = max(len(column_1), len(column_2), len(column_3))

        if isinstance(column_1, str):
            rows = [[column_1, column_2, column_3]]
        else:
            rows = []
            for i in range(max_length):
                row = []
                row.append(column_1[i] if i < len(column_1) else "")
                row.append(column_2[i] if i < len(column_2) else "")
                row.append(column_3[i] if i < len(column_3) else "")
                rows.append(row)

        file_path = self.create_csv(headers, rows)
        public_url = repo.upload_file(file_path)
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)

        return {
            "sheet_url": public_url
        }