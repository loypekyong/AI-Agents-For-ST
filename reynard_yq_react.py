from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import CohereReranker, NoReranker
from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf


import openai
import os
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

# com_id = "CommAero"
# uss_id = "USS"

# com_kb = KnowledgeBase(com_id, reranker=reranker, vector_db=ChromaDB(com_id), storage_directory="~/AI-Agents-For-ST/storage")
# uss_kb = KnowledgeBase(uss_id, reranker=reranker, vector_db=ChromaDB(uss_id), storage_directory="~/AI-Agents-For-ST/storage")

# Assuming KnowledgeBase already exist
def query_kb(sector_id, query, reranker):
    sector_kb = KnowledgeBase(sector_id, reranker=reranker, vector_db=ChromaDB(sector_id), storage_directory="~/AI-Agents-For-ST/storage")
    document1 = "yq_node"
    document2 = sector_kb.query(query)
    title_yq = document1[0]["text"] 
    text_py = "This part obtained via Relational Matrix, denoted as Vector_Text: \n" + document2[0]["text"]

    if document1[0]["doc_id"] == document2[[0]["doc_id"]] and document1[0]["chunk_id"] == document2[[0]["chunk_id"]]:
        return text_py
    elif document1[0]["doc_id"] == document2[[0]["doc_id"]]:
        # section_id = title_yq
        # text1_yq = "This part obtained via Relational Matrix, denoted as Graph_Text: sector_kb + find section description based on section id
        # return text1_yq + text_py
        pass
    else:
        return text_py if document1 else "No relevant information found."

# ReAct Automation

path = "./storage/metadata"   
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

tools = create_dynamic_tools(sector_ids, reranker)
 
client = OpenAI(model='gpt-4o-mini')
question = "What is the revenue of Airbus 2022 and Echostar 2021"

agent = initialize_agent(tools, llm=llm, agent="zero-shot-react-description", verbose=True)
agent.run(question)