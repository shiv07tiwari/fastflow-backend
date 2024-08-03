from typing import List, Dict
from pydantic import BaseModel


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    num_nodes: int
    nodes: List = []
    edges: List[Dict[str, str]] = []
    started_at: float | None = None
    executed_at: float | None = None
    status: str | None = None

    def to_dict(self):
        return self.__dict__

