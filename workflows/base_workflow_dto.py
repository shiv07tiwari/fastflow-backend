from typing import List, Optional, Dict

from workflows.workflow_node import WorkFlowNode


class WorkflowResponseDTO:
    id: str
    name: str
    description: Optional[str] = None
    owner: str
    nodes: List[WorkFlowNode] = {}
    edges: List[Dict[str, str]] = []
    adj_list: Dict[str, List[Dict[str, str]]] = {}

    def to_dict(self) -> dict:
        return self.__dict__

