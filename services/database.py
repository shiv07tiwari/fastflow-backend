from nodes.combine_text import CombineTextNode
from nodes.gemini import GeminiNode
from nodes.web_scraper import WebScraperNode
from workflows.workflow_node import WorkFlowNode
from workflows.base_workflow import WorkflowSchema


class DataBase:
    """
    This is a dummy database class that stores the workflows and nodes.
    """

    def __init__(self):
        self.gemini_node = GeminiNode()
        self.combine_text_node = CombineTextNode()
        self.web_scrape_node = WebScraperNode()

        self.gemini_workflow = WorkflowSchema(
            id="1",
            name="Gemini Demo Workflow",
            owner="admin",
            edges=[],
            nodes=[],
            description="This is a demo workflow for Gemini",
        )

        self.gemini_workflow_node = WorkFlowNode(
            id="1",
            workflow=self.gemini_workflow.id,
            node=self.gemini_node.id,
            input={"prompt": "Return only the official website URL of Instawork, including HTTPS. It should be a valid URL."},
            outputs={},
        )
        # self.gemini_workflow_node_2 = WorkFlowNode(
        #     id="2",
        #     workflow=self.gemini_workflow.id,
        #     node=self.gemini_node,
        #     input={"prompt": "Who is the greatest captain in cricket?"},
        #     output={},
        # )
        self.scrape_workflow_node = WorkFlowNode(
            id="3",
            workflow=self.gemini_workflow.id,
            node=self.web_scrape_node.id,
            input={},
            outputs={},
        )
        self.workflow_nodes = [
            self.gemini_workflow_node,
            self.scrape_workflow_node,
        ]

        self.edges = [
            {
                "id": "edge1",
                "source": self.gemini_workflow_node.id,
                "target": self.scrape_workflow_node.id,
                "inputHandle": "url",
            },
        ]

        self.gemini_workflow.add_nodes_mapping(self.workflow_nodes)
        self.gemini_workflow.add_edges(self.edges)

    def fetch_workflow(self, workflow_id: str):
        if workflow_id == self.gemini_workflow.id:
            return self.gemini_workflow
        return None

    def get_base_node_for_workflow_node(self, node_id: str):
        for wf_node in self.workflow_nodes:
            if wf_node.id == node_id:
                return wf_node.node
