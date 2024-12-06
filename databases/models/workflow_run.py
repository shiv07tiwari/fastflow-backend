from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    num_nodes: int
    nodes: List = Field(default=[])
    edges: List[Dict[str, str]] = Field(default=[])
    started_at: Optional[float] = Field(default=None)
    executed_at: Optional[float] = Field(default=None)
    status: str = "RUNNING"
    approve_node: Optional[str] = Field(default=None)

    def to_dict(self):
        return self.__dict__

    def mark_success(self):
        self.status = "SUCCESS"

    def mark_failed(self):
        self.status = "FAILED"

    def mark_running(self):
        self.status = "RUNNING"

    def mark_waiting_for_approval(self):
        self.status = "WAITING_FOR_APPROVAL"

    def is_completed(self):
        return self.status is not "RUNNING"

