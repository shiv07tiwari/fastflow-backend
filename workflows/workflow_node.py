from pydantic import BaseModel

from databases.repository.node import NodeRepository
from nodes.base_node import Node


class WorkFlowNode(BaseModel):
    id: str | None = None
    node: str = None
    workflow: str | None = None
    input: dict | None = {}
    output: dict | None = {}

    def to_dict(self) -> dict:
        return self.__dict__

    def get_node(self):
        repo = NodeRepository()
        return repo.fetch_by_id(self.node)
