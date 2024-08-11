import asyncio
import uuid

from nodes.base_node import BaseNode, BaseNodeInput, InputType
from services import GeminiService
from PIL import Image


class InvoiceProcessorNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("file_path", InputType.COMMON, "file", is_required=True),
                BaseNodeInput("invoice_data", InputType.COMMON, "prompt", is_required=False),
            ]
            super().__init__(
                id='invoice_processor',
                name="Invoice Processor",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Processes an invoice using Gemini AI",
                node_type="AI",
                is_active=True,
                inputs=inputs,
                outputs=["summary", "invoice_id", "total_amount", "tax_amount", "discount", "buyer"]
            )

    async def execute(self, input: dict) -> []:
        from databases.repository.file_upload import FileUploadRepository
        repo = FileUploadRepository()
        service = GeminiService()

        image_url = input.get("file_path")
        invoice_data = input.get("invoice_data")
        if not isinstance(image_url, list):
            image_url = [image_url]
        if not isinstance(invoice_data, list):
            invoice_data = [invoice_data]

        DEFAULT_PROMPT = """
        Analyze this image and extract all the key information about an invoice.
        Additionally, you are given a textual data which might contain the information about the invoice.
        If image is not given, provide the information from the text.
        If the data is not of an invoice, provide an empty JSON object.
        {invoice_data}
        
        Provide the following details:
        - invoice_id
        - total_amount
        - tax_amount
        - discount
        - buyer
        - summary [A short but crisp summary of the invoice]
        In a JSON format.
        """
        responses = []
        for i in range(len(image_url)):
            image_url = image_url[i]
            invoice_data = invoice_data[i] if i < len(invoice_data) else ""
            prompt = DEFAULT_PROMPT.format(invoice_data=invoice_data)
            try:
                unique_id = uuid.uuid4().hex
                image = Image.open(repo.download_file(image_url, f"{unique_id}-temp.jpg"))
                response = service.generate_json_response(prompt, "Gemini Image", stream=False, img=image)
                responses.append(response)
                # Delete the file after processing. Access the file at root level
            except Exception as e:
                return {"error": str(e)}

        extracted_data = await asyncio.gather(*responses)
        return [
            {
                "summary": data.get("summary"),
                "invoice_id": data.get("invoice_id"),
                "total_amount": data.get("total_amount"),
                "tax_amount": data.get("tax_amount"),
                "discount": data.get("discount"),
                "buyer": data.get("buyer"),
            }
            for data in extracted_data
        ]