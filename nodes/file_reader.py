from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services.file_reader import extract_text_from_pdf, extract_data_from_csv
from services.utils import extract_links


class FileReader(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("file_path", InputType.COMMON, "file", is_required=True),
            ]
            super().__init__(
                id='file_reader',
                name="File Reader",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Reads a file from disk and processes based on file type",
                node_type="ai",
                is_active=True,
                inputs=inputs,
                outputs=["response", "links"],
                workflow_node_name="file_reader",
                **kwargs
            )

    async def execute(self, input: dict) -> []:
        from databases.repository.file_upload import FileUploadRepository
        file_path = input.get("file_path", '')
        repo = FileUploadRepository()

        if not isinstance(file_path, list):
            file_path = [file_path]

        response = []
        for path in file_path:
            if not path:
                continue
            path = path.replace('https://storage.googleapis.com/fastflow-81dd7.appspot.com/', '')
            try:
                file_contents = repo.read_file(path)
                if path.endswith('.pdf'):
                    file_contents = extract_text_from_pdf(file_contents)
                    links = extract_links(file_contents)
                elif path.endswith('.csv'):
                    file_contents = extract_data_from_csv(file_contents)
                    links = []
                else:
                    return {"error": f"Unsupported file type for {path}"}
                response.append({
                    "response": file_contents,
                    "links": str(links)
                })
            except Exception as e:
                return {"error": str(e)}

        return response
