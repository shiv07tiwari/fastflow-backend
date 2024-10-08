from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict


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
    EXTRACT = "extract"
    STAR = "star"


class InputType(Enum):
    INTERNAL_ONLY = "internal"
    EXTERNAL_ONLY = "external"
    COMMON = "common"
    CONFIG = "config"


class BaseNodeInput(BaseModel):
    key: str
    handle_type: str
    input_type: str  # What type of UI input is this (text, dropdown, etc)
    is_required: bool

    def __init__(self, key: str, handle_type: InputType | str, input_type: str, is_required: bool = False):
        handle_type = handle_type if isinstance(handle_type, str) else handle_type.value
        super().__init__(key=key, handle_type=handle_type, input_type=input_type, is_required=is_required)

    def to_dict(self) -> dict:
        return self.__dict__


class BaseNode(BaseModel):
    """
    This is a single node in the workflow. Created by system.
    """
    model_config = ConfigDict(extra='allow')
    
    id: str
    name: str
    icon_url: str
    description: str
    created_at: str | None = None
    updated_at: str | None = None
    is_active: bool = True
    node_type: str
    inputs: List[BaseNodeInput] = []
    outputs: List[str] = []

    def execute(self, *args, **kwargs):
        raise NotImplementedError()

    def can_execute(self, *args, **kwargs):
        raise NotImplementedError()

    def to_dict(self) -> dict:
        return self.__dict__
