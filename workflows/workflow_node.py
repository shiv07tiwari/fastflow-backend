from typing import List

from pydantic import BaseModel

from databases.repository.node import NodeRepository
from nodes.base_node import BaseNodeInput


class WorkFlowNode(BaseModel):
    id: str | None = None
    name: str = "Node"
    node: str = None
    workflow: str | None = None
    available_inputs: dict | None = {}
    outputs: dict | None = {}
    output_handles: List[str] | None = []
    is_deleted: bool = False
    external_inputs: List[BaseNodeInput]
    internal_inputs: List[BaseNodeInput]
    common_inputs: List[BaseNodeInput]
    position: dict | None = {}

    def to_dict(self) -> dict:
        return self.__dict__

    def get_node(self):
        repo = NodeRepository()
        return repo.fetch_by_id(self.node)

    def can_execute(self):
        base_node = self.get_node()
        base_node_inputs = base_node.inputs

        for input in base_node_inputs:
            if input.is_required and input.key not in self.available_inputs:
                return False

        return True
