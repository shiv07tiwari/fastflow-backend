import io
import pandas as pd
from nodes.base_node import BaseNode
from services.utils import extract_links
import pdfplumber


class FileReader(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            super().__init__(
                id='file_reader',
                name="File Reader",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Reads a file from disk and processes based on file type",
                node_type="ai",
                is_active=True,
                inputs=["file_path"],
                outputs=["response", "links"],
                workflow_node_name="file_reader",
                **kwargs
            )

    def _extract_text_from_pdf(self, pdf_bytes):
        text = ''
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text

    def _extract_data_from_csv(self, file_bytes):
        try:
            # Using StringIO to convert bytes to a string buffer
            csv_data = pd.read_csv(io.StringIO(file_bytes.decode()))
            return csv_data.to_csv(index=False)  # Convert DataFrame back to CSV format
        except pd.errors.ParserError as e:
            return {"error": "Failed to parse CSV file: " + str(e)}

    async def execute(self, input: dict) -> dict:
        from databases.repository.file_upload import FileUploadRepository
        file_path = input.get("file_path")
        repo = FileUploadRepository()

        try:
            file_contents = repo.read_file(file_path)
            if file_path.endswith('.pdf'):
                file_contents = self._extract_text_from_pdf(file_contents)
                links = extract_links(file_contents)
            elif file_path.endswith('.csv'):
                file_contents = self._extract_data_from_csv(file_contents)
                links = []
            else:
                return {"error": f"Unsupported file type for {file_path}"}
        except Exception as e:
            return {"error": str(e)}

        return {
            "response": file_contents,
            "links": links
        }
