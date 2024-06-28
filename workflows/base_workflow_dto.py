from dataclasses import dataclass
from typing import List, Optional, Dict

from workflows.base_workflow import WorkflowSchema
from workflows.workflow_node import WorkFlowNode


@dataclass
class WorkflowResponseDTO:
    id: str
    name: str
    owner: str
    nodes: List[WorkFlowNode]
    edges: List[Dict[str, str]]
    adj_list: Dict[str, List[Dict[str, str]]]
    description: Optional[str] = None

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def to_response(workflow: WorkflowSchema, nodes: List[WorkFlowNode]):
        """
        Nodes is passed as a parameter because the whole object is not a part of the WorkflowSchema
        """
        return WorkflowResponseDTO(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            owner=workflow.owner,
            nodes=nodes,
            edges=workflow.edges,
            adj_list=workflow.adj_list
        )

