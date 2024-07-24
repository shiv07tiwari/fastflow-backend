from typing import List, Dict
from pydantic import BaseModel


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    nodes: List = []
    edges: List[Dict[str, str]] = []
    executed_at: float = None

