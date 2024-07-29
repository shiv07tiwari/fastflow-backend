import io
import zipfile
from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services.file_reader import extract_data_from_csv, extract_text_from_pdf


class ZipReaderNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("file_path", InputType.COMMON, "file", is_required=True),
            ]
            super().__init__(
                id='zip_reader',
                name="ZIP Reader",
                icon_url="https://cdn-icons-png.flaticon.com/512/337/337946.png",
                description="Reads a ZIP file from disk and extracts contents",
                node_type="ai",
                is_active=True,
                inputs=inputs,
                outputs=["file_names", "file_contents"],
                workflow_node_name="zip_reader",
                **kwargs
            )

    def _process_zip_file(self, file, file_name) -> str | None:
        try:
            file_bytes = file.read()
            if file_name.endswith('.csv'):
                return extract_data_from_csv(file_bytes)
            elif file_name.endswith('.txt'):
                return file_bytes.decode()
            elif file_name.endswith('.pdf'):
                return extract_text_from_pdf(file_bytes)
            else:
                print(f"Unsupported file type for {file_name}")
                return None
        except Exception as e:
            print({f"error processing file {file_name}": str(e)})
            return None

    def _extract_files_from_zip(self, zip_bytes):
        file_names = []
        file_contents = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
            for file_name in zip_file.namelist():
                with zip_file.open(file_name) as file:
                    file_content = self._process_zip_file(file, file_name)
                    if file_content:
                        file_contents.append(file_content)
                        file_names.append(file_name)

        return file_names, file_contents

    async def execute(self, input: dict) -> []:
        from databases.repository.file_upload import FileUploadRepository
        file_path = input.get("file_path")
        repo = FileUploadRepository()
        try:
            file_contents_bytes = repo.read_file(file_path)
            file_names, file_contents = self._extract_files_from_zip(file_contents_bytes)
        except Exception as e:
            return {"error": str(e)}

        response = []
        for i in range(len(file_names)):
            response.append({
                "file_names": file_names[i],
                "file_contents": file_contents[i]
            })

        return response
