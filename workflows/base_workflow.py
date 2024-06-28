from typing import List, Optional, Dict
from pydantic import BaseModel

from workflows.workflow_node import WorkFlowNode


class WorkflowSchema(BaseModel):
    """This is the schema for a workflow. Created by user."""
    id: str
    name: str
    description: Optional[str] = None
    owner: str
    nodes: List[str] = []  # Store individual nodes
    edges: List[Dict[str, str]] = []  # Store edges (source, target, sourceHandle)
    adj_list: Dict[str, List[Dict[str, str]]] = {}  # Store adjacency list with handles

    def __str__(self):
        return f"{self.name} - {self.description or 'No description'}"

    def add_nodes(self, nodes: List[WorkFlowNode]):
        for node in nodes:
            self.nodes.append(node.id)  # TODO: Maybe redundant?

    def add_edges(self, edges: List[Dict[str, str]]):
        self.edges = edges or []

    def get_node(self, id: str) -> Optional[WorkFlowNode]:
        return

    def to_dict(self) -> dict:
        return self.__dict__
