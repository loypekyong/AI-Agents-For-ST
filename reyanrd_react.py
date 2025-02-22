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
from langchain.memory import ConversationBufferMemory
# load API keys; you will need to obtain these if you haven't yet

from dotenv import load_dotenv
# from openai import OpenAI
import os, json

load_dotenv()

# Initialize OpenAI and KnowledgeBase
def response(question):
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

    tools = create_dynamic_tools(sector_ids, reranker)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    question = "What is the revenue of Echostar 2021 and WillisLease 2021?"

    agent = initialize_agent(tools, llm=llm, agent="chat-conversational-react-description",max_iterations=2, memory=memory, verbose=True)
    response = agent.run(question)
    return response

if __name__ == "__main__":
    question = input("Enter your question: ")
    response(question)
