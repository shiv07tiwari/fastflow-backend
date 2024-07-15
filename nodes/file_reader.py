from nodes.base_node import BaseNode
from services.file_reader import extract_text_from_pdf, extract_data_from_csv
from services.utils import extract_links


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

    async def execute(self, input: dict) -> dict:
        from databases.repository.file_upload import FileUploadRepository
        file_path = input.get("file_path")
        repo = FileUploadRepository()

        try:
            file_contents = repo.read_file(file_path)
            if file_path.endswith('.pdf'):
                file_contents = extract_text_from_pdf(file_contents)
                links = extract_links(file_contents)
            elif file_path.endswith('.csv'):
                file_contents = extract_data_from_csv(file_contents)
                links = []
            else:
                return {"error": f"Unsupported file type for {file_path}"}
        except Exception as e:
            return {"error": str(e)}

        return {
            "response": file_contents,
            "links": links
        }
