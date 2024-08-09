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
    status: str = "RUNNING"
    approve_node: str | None = None

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

