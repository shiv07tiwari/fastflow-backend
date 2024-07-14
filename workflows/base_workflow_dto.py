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
    input_handles: Optional[List[str]] = None
    output_handles: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def to_response(workflow: WorkflowSchema, nodes: List[WorkFlowNode]):
        """
        Nodes is passed as a parameter because the whole object is not a part of the WorkflowSchema
        """
        # In Edges, the key inputHandle has to be converted to targetHandle
        # outputHandle has to be converted to sourceHandle !!!
        # This is to maintain consistency with the react webflow builder
        edges = []
        for edge in workflow.edges:
            edge_output = {
                **edge,
                "sourceHandle": edge.get('outputHandle', "response"),
                "targetHandle": edge.get('inputHandle', None)
            }
            edge_output.pop('outputHandle', None)
            edge_output.pop('inputHandle', None)
            edges.append(edge_output)

        return WorkflowResponseDTO(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            owner=workflow.owner,
            nodes=nodes,
            edges=edges,
            adj_list=workflow.adj_list
        )

