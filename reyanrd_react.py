import os
import sys

from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import CohereReranker, NoReranker
from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf


import openai
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
# load API keys; you will need to obtain these if you haven't yet

from dotenv import load_dotenv
# from openai import OpenAI
import os, json

load_dotenv()

# Initialize OpenAI and KnowledgeBase
llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0)
reranker = CohereReranker()

# Assuming KnowledgeBase already exist
def query_kb(sector_id, query, reranker):
    sector_kb = KnowledgeBase(sector_id, reranker=reranker, vector_db=ChromaDB(sector_id), storage_directory="~/AI-Agents-For-ST/storage")
    document = sector_kb.query([query])
    return document[0]["text"] if document else "No relevant information found."

# ReAct Automation

path = "./../storage/metadata"   
files_list = os.listdir(path)

sector_ids = []

for i in range(len(files_list)):
    sector_id = os.listdir(path)[i][:-5]
    sector_ids.append(sector_id)

def create_dynamic_tools(knowledge_bases, reranker):
    tools = []
    for kb in knowledge_bases:
        tool = Tool(
            name=f"search_{kb}",
            func=lambda query, kb=kb: query_kb(kb, query, reranker),
            description=f"Searches the {kb} knowledge base for relevant information."
        )
        tools.append(tool)
    return tools

def kg_query(query):
    graph = neo4j_tools.initialize_neo4j()
    neo4j_results = neo4j_tools.query_neo4j(graph, query)
    document = f"Knowledge Graph Results:\n{neo4j_results}"
    return document

tools = create_dynamic_tools(sector_ids, reranker)
 
client = OpenAI(model='gpt-4o-mini')
question = "What is the revenue of Echostar 2021 and WillisLease 2021?"

agent = initialize_agent(tools, llm=llm, agent="zero-shot-react-description", verbose=True)
agent.run(question)
