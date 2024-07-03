from typing import List

from pydantic import BaseModel

from databases.repository.node import NodeRepository
from nodes.base_node import BaseNode


class WorkFlowNode(BaseModel):
    id: str | None = None
    node: str = None
    workflow: str | None = None
    required_inputs: List[str] | None = []
    available_inputs: dict | None = {}
    output: dict | None = {}

    def to_dict(self) -> dict:
        return self.__dict__

    def get_node(self):
        repo = NodeRepository()
        return repo.fetch_by_id(self.node)

    def can_execute(self):
        base_node = self.get_node()
        base_node_inputs = base_node.inputs

        # Ensure that all base node inputs are available and required
        for input in base_node_inputs:
            if input not in self.required_inputs:
                raise ValueError(f"Missing required input {input} for node {base_node.name}")

        for input in base_node_inputs:
            if input not in self.available_inputs:
                return False

        return True


