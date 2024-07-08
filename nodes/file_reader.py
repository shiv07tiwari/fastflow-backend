from nodes.base_node import BaseNode


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
                outputs=["file_contents"],
                workflow_node_type="file_reader",
                **kwargs
            )

    def execute(self, input: dict) -> dict:
        file_path = input.get("file")
        with open(file_path, 'r') as file:
            data = file.read()
        return {"file_contents": data}