from dataclasses import dataclass
from typing import List, Optional, Dict

from services.utils import format_output_edges, underscore_to_readable
from databases.models.workflow_schema import WorkflowSchema
from databases.models.workflow_node import WorkFlowNode
from pydantic import BaseModel


class WorkflowRunRequest(BaseModel):
    id: str
    nodes: list | None = None
    edges: list | None = None
    run_id: str


@dataclass
class WorkflowResponseDTO:
    id: str | None = None
    name: str | None = None
    nodes: List[WorkFlowNode] | None = None
    edges: List[Dict[str, str]] | None = None
    owner: str | None = None
    description: Optional[str] = None
    output_handles: Optional[List[str]] = None
    variables: Optional[List[Dict[str, str]]] = None

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
        edges = format_output_edges(workflow.edges)

        workflow_output_variables = []

        for node in nodes:
            node_outputs = node.outputs
            node_name = node.node
            if not len(node_outputs) > 0:
                continue
            for output_key in node_outputs[0].keys():
                workflow_output_variables.append({'key': f"{node_name}.{output_key}", "value": f"{underscore_to_readable(node_name)} - {output_key}"})

        print("Workflow Node Output: ", workflow_output_variables)

        return WorkflowResponseDTO(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            owner=workflow.owner,
            nodes=nodes,
            edges=edges,
            variables=workflow_output_variables
        )
