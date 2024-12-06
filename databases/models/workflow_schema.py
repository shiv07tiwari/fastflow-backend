from __future__ import annotations

from typing import List, Optional, Dict

from pycparser.c_ast import Union
from pydantic import BaseModel


class WorkflowSchema(BaseModel):
    """This is the schema for a workflow. Created by user."""
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    nodes: List[str]  # Store individual nodes
    edges: List[Dict[str, str]]  # Store edges (source, target, sourceHandle)
    latest_run_id: Optional[str] = None
    ai_description: Optional[str] = None

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
