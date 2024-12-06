from typing import List, Optional

from pydantic import BaseModel, Field

from databases.repository.node import NodeRepository
from nodes.base_node import BaseNodeInput


class WorkFlowNode(BaseModel):
    id: Optional[str] = None
    name: str = "Node"
    node: str = None
    workflow: Optional[str] = None
    available_inputs: Optional[dict] = Field(default={})
    outputs: Optional[dict] = Field(default={})
    output_handles: Optional[List[str]] = Field(default=[])
    is_deleted: bool = False
    external_inputs: List[BaseNodeInput]
    internal_inputs: List[BaseNodeInput]
    common_inputs: List[BaseNodeInput]
    position: Optional[dict] = Field(default={})

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
