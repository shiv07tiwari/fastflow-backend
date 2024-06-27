from pydantic import BaseModel

from nodes.base_node import Node


class WorkFlowNode(BaseModel):
    id: str | None = None
    node: str = None
    workflow: str | None = None
    input: dict | None = {}
    output: dict | None = {}
