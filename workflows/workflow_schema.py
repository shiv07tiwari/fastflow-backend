from typing import List, Optional, Dict
from pydantic import BaseModel


class WorkflowSchema(BaseModel):
    """This is the schema for a workflow. Created by user."""
    id: str | None = None
    name: str | None = None
    description: Optional[str] = None
    owner: str | None = None
    nodes: List[str] = []  # Store individual nodes
    edges: List[Dict[str, str]] = []  # Store edges (source, target, sourceHandle)

    def __str__(self):
        return f"{self.name} - {self.description or 'No description'}"

    def add_nodes(self, nodes: List[str]):
        for node in nodes:
            self.nodes.append(node)  # TODO: Maybe redundant?

    def set_nodes(self, nodes: List[str]):
        self.nodes = nodes or []

    def set_edges(self, edges: List[Dict[str, str]]):
        self.edges = edges or []

    def to_dict(self) -> dict:
        return self.__dict__
