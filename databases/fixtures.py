from databases import base
from databases.constants import Tables
from databases.controller import DatabaseController
from nodes.combine_text import CombineTextNode
from nodes.gemini import GeminiNode
from workflows import workflow_node, base_workflow


class Fixtures:
    def __init__(self):
        self.db_controller = DatabaseController(db=base.db)

    def add_test_data(self, n: int = 1):

        for i in range(n):
            gemini_node = GeminiNode()
            combine_text_node = CombineTextNode()
            gemini_workflow = base_workflow.WorkflowSchema(
                id="WF"+str(i),
                name="Gemini Demo Workflow",
                owner="admin",
                edges=[],
                nodes=[],
                description="This is a demo workflow for Gemini",
            )

            gemini_workflow_node = workflow_node.WorkFlowNode(
                id="WN"+gemini_workflow.id+str(i),
                workflow=gemini_workflow.id,
                node=gemini_node.id,
                input={"prompt": "Who is the highest run scorer in cricket?"},
                output={},
            )
            gemini_workflow_node_2 = workflow_node.WorkFlowNode(
                id="WN"+gemini_workflow.id+str(i+1),
                workflow=gemini_workflow.id,
                node=gemini_node.id,
                input={"prompt": "Who is the greatest captain in cricket?"},
                output={},
            )
            combine_text_workflow_node = workflow_node.WorkFlowNode(
                id="WN"+gemini_workflow.id+str(i+2),
                workflow=gemini_workflow.id,
                node=combine_text_node.id,
                input={},
                output={},
            )
            workflow_nodes = [
                gemini_workflow_node,
                gemini_workflow_node_2,
                combine_text_workflow_node
            ]

            edges = [
                {
                    "id": "edge1",
                    "source": gemini_workflow_node.id,
                    "target": combine_text_workflow_node.id,
                    "inputHandle": "text-1",
                },
                {
                    "id": "edge2",
                    "source": gemini_workflow_node_2.id,
                    "target": combine_text_workflow_node.id,
                    "inputHandle": "text-2",
                }
            ]

            gemini_workflow.add_nodes(workflow_nodes)
            gemini_workflow.add_edges(edges)

            self.db_controller.insert(Tables.Node, gemini_node.to_dict(), document_id=gemini_node.id)
            self.db_controller.insert(Tables.Node, combine_text_node.to_dict(), document_id=combine_text_node.id)
            self.db_controller.insert(Tables.WorkflowSchema, gemini_workflow.to_dict(), document_id=gemini_workflow.id)
            self.db_controller.insert(Tables.WorkFlowNode, gemini_workflow_node.to_dict(), document_id=gemini_workflow_node.id)
            self.db_controller.insert(Tables.WorkFlowNode, gemini_workflow_node_2.to_dict(), document_id=gemini_workflow_node_2.id)
            self.db_controller.insert(Tables.WorkFlowNode, combine_text_workflow_node.to_dict(), document_id=combine_text_workflow_node.id)
