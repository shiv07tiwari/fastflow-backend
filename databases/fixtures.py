from databases import base
from databases.constants import Tables, NodeTypeClassMappings
from databases.controller import DatabaseController
from nodes.combine_text import CombineTextNode
from nodes.company_enrichment import CompanyEnrichmentNode
from nodes.file_reader import FileReader
from nodes.gemini import GeminiNode
from nodes.reddit_bot import RedditBotNode
from nodes.resume_analysis import ResumeAnalysisNode
from nodes.summarizer import SummarizerNode
from nodes.user_input import UserInputNode
from nodes.web_scraper import WebScraperNode
from nodes.zip_reader import ZipReaderNode
from workflows import workflow_node, base_workflow


class Fixtures:
    def __init__(self):
        self.db_controller = DatabaseController()

    def add_test_data(self, n: int = 1):
        self.db_controller.clear_table(Tables.Node)
        for _node in NodeTypeClassMappings.values():
            node = _node()
            node.inputs = [input.to_dict() for input in node.inputs]
            self.db_controller.insert(Tables.Node, node.to_dict(), document_id=node.id)

        self.db_controller.clear_table(Tables.WorkflowRun)
