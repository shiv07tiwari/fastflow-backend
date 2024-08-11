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
    
    rewrite_prompt : PromptTemplate = PromptTemplate(
            "Here are some documents containing information, they could be a JSON-like paragraphs or normal paragraphs, \n"
            "interpret them as needed.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Here is what I want what to retreive from the documents:\n"
            "{query_str}\n"

            "Rewrite the above query such that it will be more effective in retreiving the documents which can answer"
            " the query. To be clear, do not return the answer to the query, but rather rewrite the query such that" 
            " the retreived documents will be more likely to answer the query. Only return the rewritten query, "
            " do not return anything else. Absolutely nothing else.\n"
            " For example if the documents are like 'It was really nice, would love to visit again';"
            " 'The winter here is awesome'; 'The hotel I stayed in was very dirty' "
            " query is 'What did people like in paris?'"
            " the rewritten query can be like 'Reviews about paris, including places, weather, environment, cleaniless etc' \n"
            "Notice how the rewritten query is more effective in retreiving the documents which can answer the query, "
            "even though the documents don't contain the word paris"
        )
    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: Gemini

    def rewrite_query(self, query_str: str, samples : str = "" ) -> str:
        """Rewrite query based on RAG document content and intent"""
        if len(samples):
            rewritten_query = self.llm.complete(
                self.rewrite_prompt.format(
                    context_str=samples,
                    query_str=query_str,
                )
            )
            return rewritten_query
        return query_str
    
    def custom_query(self, query_str: str, rewrite_query: bool = True) -> str:
        nodes = self.retriever.retrieve(query_str)
        nodes_text = [n.node.get_content() for n in nodes]
        if rewrite_query:
            query_str = self.rewrite_query(query_str,  "__\n\n__".join(nodes_text[:10]))
            print(query_str)

        context_str =  "__\n\n__".join(nodes_text)
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
        
    def query(self, query: str, rewrite_query: bool = True):
        return self.query_engine.custom_query(query)

    
