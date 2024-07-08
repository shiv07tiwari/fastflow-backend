from databases import base
from databases.constants import Tables
from databases.controller import DatabaseController
from nodes.combine_text import CombineTextNode
from nodes.file_reader import FileReader
from nodes.gemini import GeminiNode
from nodes.user_input import UserInputNode
from nodes.web_scraper import WebScraperNode
from workflows import workflow_node, base_workflow


class Fixtures:
    def __init__(self):
        self.db_controller = DatabaseController(db=base.db)

    def add_test_data(self, n: int = 1):
        self.db_controller.clear_table(Tables.Node)
        self.db_controller.clear_table(Tables.WorkflowSchema)
        self.db_controller.clear_table(Tables.WorkFlowNode)

        for i in range(n):
            gemini_node = GeminiNode()
            combine_text_node = CombineTextNode()
            web_scrapper_node = WebScraperNode()
            user_input_node = UserInputNode()
            file_reader_node = FileReader()

            gemini_workflow = base_workflow.WorkflowSchema(
                id="WF"+str(i),
                name="Gemini Demo Workflow",
                owner="admin",
                edges=[],
                nodes=[],
                description="This is a demo workflow for Gemini",
            )

            web_workflow_node = workflow_node.WorkFlowNode(
                id="WN"+gemini_workflow.id+str(i),
                workflow=gemini_workflow.id,
                node=web_scrapper_node.id,
                required_inputs=["url"],
                available_inputs={"url": "https://www.instawork.com/"},
                output={},
            )
            gemini_workflow_node_2 = workflow_node.WorkFlowNode(
                id="WN"+gemini_workflow.id+str(i+1),
                workflow=gemini_workflow.id,
                node=gemini_node.id,
                required_inputs=["prompt", "input1"],
                available_inputs={
                    "prompt": "This is the data about Instawork. ''' {input1} ''' How many workers does Instawork have?",
                    "input1": None,
                },
                output={},
            )
            workflow_nodes = [
                web_workflow_node.id,
                gemini_workflow_node_2.id,
            ]

            edges = [
                {
                    "id": "edge1",
                    "source": web_workflow_node.id,
                    "target": gemini_workflow_node_2.id,
                    "inputHandle": "input1",
                },
            ]

            gemini_workflow.add_nodes(workflow_nodes)
            gemini_workflow.add_edges(edges)

            self.db_controller.insert(Tables.Node, gemini_node.to_dict(), document_id=gemini_node.id)
            self.db_controller.insert(Tables.Node, combine_text_node.to_dict(), document_id=combine_text_node.id)
            self.db_controller.insert(Tables.Node, web_scrapper_node.to_dict(), document_id=web_scrapper_node.id)
            self.db_controller.insert(Tables.Node, user_input_node.to_dict(), document_id=user_input_node.id)
            self.db_controller.insert(Tables.Node, file_reader_node.to_dict(), document_id=file_reader_node.id)
            self.db_controller.insert(Tables.WorkflowSchema, gemini_workflow.to_dict(), document_id=gemini_workflow.id)
            self.db_controller.insert(Tables.WorkFlowNode, web_workflow_node.to_dict(), document_id=web_workflow_node.id)
            self.db_controller.insert(Tables.WorkFlowNode, gemini_workflow_node_2.to_dict(), document_id=gemini_workflow_node_2.id)
