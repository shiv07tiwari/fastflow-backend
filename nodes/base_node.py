from enum import Enum
from typing import List

from pydantic import BaseModel


class NodeType(Enum):
    """
    This is the type of the node.
    """
    AI = "ai"
    GITHUB = "github"
    SALES = "sales"
    DECISION = "decision"
    FORK = "fork"
    JOIN = "join"


class Node(BaseModel):
    """
    This is a single node in the workflow. Created by system.
    """
    id: str
    name: str
    icon_url: str
    description: str
    created_at: str | None = None
    updated_at: str | None = None
    is_active: bool = True
    node_type: NodeType
    inputs: List[str] = []
    outputs: List[str] = []

    def execute(self, *args, **kwargs):
        raise NotImplementedError()