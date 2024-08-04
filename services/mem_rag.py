from typing import List, Dict, Any
import os 
import json 
import pandas as pd

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core import Document
from llama_index.core.node_parser import JSONNodeParser, SimpleNodeParser
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core import PromptTemplate

class RAGStringQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""
    qa_prompt : PromptTemplate = PromptTemplate(
            "Here are some documents containing information, they could be a JSON-like paragraphs or normal paragraphs, \n"
            "interpret them as needed.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Answer the following query based on the information, do not use any prior knowledge.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
    
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: Gemini

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)

        context_str = "__\n\n__".join([n.node.get_content() for n in nodes])
        response = self.llm.complete(
            self.qa_prompt.format(context_str=context_str, query_str=query_str)
        )

        return dict(response = str(response), nodes = nodes)
    
class InMemoryRAG():
    
    def __init__(self) -> None:
        
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

        llm = Gemini(model="models/gemini-1.5-flash", api_key=GEMINI_API_KEY)
        embed_model = GeminiEmbedding(model_name="models/embedding-001", 
                                    api_key=GEMINI_API_KEY,
                                    title="this is a document")
        self.jsonnodeparser = JSONNodeParser()
        self.textnodeparser = SimpleNodeParser()
        self.index = VectorStoreIndex(nodes = [], embed_model=embed_model)

        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=20,
        )

        
        # configure response synthesizer
        response_synthesizer = get_response_synthesizer()

        self.query_engine = RAGStringQueryEngine(
            retriever=self.retriever,
            response_synthesizer=response_synthesizer,
            llm=llm,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        )

    def add_documents_from_df(self, df: pd.DataFrame):
        json_documents = df.to_dict('records')
        documents = [Document(text=json.dumps(doc)) for doc in json_documents]
        nodes = self.jsonnodeparser.get_nodes_from_documents(documents)
        self.index.insert_nodes(nodes)

    def add_documents_from_json(self, json_documents):
       
        documents = [Document(text=json.dumps(doc)) for doc in json_documents]
        nodes = self.jsonnodeparser.get_nodes_from_documents(documents)
        self.index.insert_nodes(nodes)

    def add_documents_from_list(self, documents):
        documents = [Document(text=doc) for doc in documents]
        nodes = self.textnodeparser.get_nodes_from_documents(documents)
        self.index.insert_nodes(nodes)
        
    def query(self, query: str):
        return self.query_engine.query(query)

    
