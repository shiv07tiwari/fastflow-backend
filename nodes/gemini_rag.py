from nodes.base_node import BaseNode, NodeType, BaseNodeInput, InputType
from nodes.constants import NodeModelTypes
from services.mem_rag import InMemoryRAG

class GeminiRAGNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "text", is_required=True),
                BaseNodeInput("input_1", InputType.COMMON, "text"),
            ]
            super().__init__(
                id='gemini_rag',
                name="Gemini",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Generate a Response from Gemini AI using RAG",
                node_type=NodeType.AI.value,
                is_active=True,
                inputs=inputs,
                outputs=["response"],
                **kwargs
            )
        

    async def execute(self, input: dict) -> list:
        prompt = input.get("prompt")
        input_1 = input.get("input_1", [])

        if not isinstance(input_1, list):
            input_1 = [input_1]

        self.rag = InMemoryRAG()
        self.rag.add_documents_from_list(input_1[0].split("<sep>"))

        response = []
        for item in input_1:
            formatted_prompt = prompt.format(input_1=item)
            try:
                rag_response = self.rag.query(formatted_prompt)
                response.append(rag_response['response'])
            except Exception as e:
                print(f"Error in executing node {self.name}: {e}")
                raise e

        return {
            "response": response
        }

    def can_execute(self, inputs: dict) -> bool:
        for input_key in [id for id in self.inputs]:
            if input_key not in inputs or not inputs[input_key]:
                return False
        return True
