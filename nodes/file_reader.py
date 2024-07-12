from nodes.base_node import BaseNode
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
                description="Read a file from disk",
                node_type="ai",
                is_active=True,
                inputs=["file_path"],
                outputs=["response", "links"],
                workflow_node_type="file_reader",
                **kwargs
            )

    async def execute(self, input: dict) -> dict:
        from databases.repository.file_upload import FileUploadRepository
        file_path = input.get("file_path")
        repo = FileUploadRepository()
        try:
            file_contents = repo.read_file(file_path)
            links = extract_links(file_contents)
        except Exception as e:
            return {"error": str(e)}

        return {
            "response": file_contents,
            "links": links
        }
