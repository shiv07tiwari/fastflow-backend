import random

from nodes.gemini import GeminiNode
from nodes.workflow_node import WorkFlowNode
from workflows.base_workflow import WorkflowSchema


class DataBase:
    def __init__(self):
        self.gemini_node = GeminiNode()

        self.gemini_workflow = WorkflowSchema(
            id="1",
            name="Gemini Demo Workflow",
            owner="admin",
            edges=[],
            nodes={},
            description="This is a demo workflow for Gemini",
        )

        self.gemini_workflow_node = WorkFlowNode(
            id="1",
            workflow=self.gemini_workflow.id,
            node=self.gemini_node,
            input={"prompt": "Who is the president of the United States?"},
            output={},
        )
        self.gemini_workflow_node_2 = WorkFlowNode(
            id="2",
            workflow=self.gemini_workflow.id,
            node=self.gemini_node,
            input={},
            output={},
        )
        self.workflow_nodes = [self.gemini_workflow_node, self.gemini_workflow_node_2]
        self.edges = [
            {
                "id": "edge1",
                "source": self.gemini_workflow_node.id,
                "target": self.gemini_workflow_node_2.id,
                "inputHandle": "prompt",
            },
            {
                "id": "edge2",
                "source": self.gemini_workflow_node.id,
                "target": self.gemini_workflow_node_2.id,
                "inputHandle": "stream",
            }
        ]

        self.gemini_workflow.add_nodes([self.gemini_workflow_node, self.gemini_workflow_node_2])
        self.gemini_workflow.add_edges(self.edges)

    def fetch_workflow(self, workflow_id: str):
        if workflow_id == self.gemini_workflow.id:
            return self.gemini_workflow
        return None

    def get_base_node_for_workflow_node(self, node_id: str):
        for wf_node in self.workflow_nodes:
            if wf_node.id == node_id:
                return wf_node.node
