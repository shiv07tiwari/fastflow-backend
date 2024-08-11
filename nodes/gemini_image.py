import asyncio
import os
import uuid

from nodes.base_node import BaseNode, BaseNodeInput, InputType, NodeType
from PIL import Image

from services import GeminiService


class GeminiImageNode(BaseNode):

    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("file_path", InputType.COMMON, "file", is_required=True),
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "prompt", is_required=False),
            ]
            super().__init__(
                id='gemini_image',
                name="Gemini Image",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Analyzes an image using Gemini AI",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["summary"],
            )

    async def execute(self, input: dict) -> []:
        from databases.repository.file_upload import FileUploadRepository
        repo = FileUploadRepository()
        service = GeminiService()

        image_url = input.get("file_path")
        if not isinstance(image_url, list):
            image_url = [image_url]

        DEFAULT_PROMPT = """
        Analyze this image and extract all the key information.
        
        If the document seems like an invoice [handwritten or printed], please provide all the key information with keys:
        - Invoice Number
        - Invoice Date
        - Total Amount
        - Vendor Name
        - Discount
        - Tax Amount
        - Seller Name
        """
        prompt = input.get("prompt") or DEFAULT_PROMPT
        output_format = """
        Output a json object with the following keys:
        - description: A brief description of the image
        - info: A json with keys as the information extracted and values as the extracted information
        """

        FINAL_PROMPT = f"{prompt}\n{output_format}"

        responses = []
        for img in image_url:
            try:
                unique_id = uuid.uuid4().hex
                image = Image.open(repo.download_file(img, f"{unique_id}-temp.jpg"))
                response = service.generate_json_response(FINAL_PROMPT, "Gemini Image", stream=False, img=image)
                responses.append(response)
                # Delete the file after processing. Access the file at root level
            except Exception as e:
                return {"error": str(e)}
        response = await asyncio.gather(*responses)

        return [
            {"summary": str(r.get("description")), "info": str(r.get("info"))} for r in response
        ]