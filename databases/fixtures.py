from databases import base
from databases.constants import Tables
from databases.controller import DatabaseController
from nodes.combine_text import CombineTextNode
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
        gemini_node = GeminiNode()
        combine_text_node = CombineTextNode()
        web_scrapper_node = WebScraperNode()
        user_input_node = UserInputNode()
        file_reader_node = FileReader()
        resume_analysis_node = ResumeAnalysisNode()
        summarize_node = SummarizerNode()
        zip_reader_node = ZipReaderNode()
        reddit_node = RedditBotNode()

        nodes = [gemini_node, combine_text_node, web_scrapper_node, user_input_node, file_reader_node,
                 resume_analysis_node, summarize_node, zip_reader_node, reddit_node]

        for node in nodes:
            self.db_controller.insert(Tables.Node, node.to_dict(), document_id=node.id)
