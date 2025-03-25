import os
import sys
import time
# allow importing dsrag modules
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(utils_dir)

from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI, AnthropicChatAPI
from dsrag.reranker import CohereReranker, NoReranker
from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf


import openai
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI, ChatCohere
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
# load API keys; you will need to obtain these if you haven't yet

from dotenv import load_dotenv
# from openai import OpenAI
import os, json

load_dotenv()

STORAGE_DIR = "/app/storage" if os.environ.get("DOCKER") else "../storage"

# Initialize OpenAI and KnowledgeBase
def response(question, llm_name=0):
    llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0) if llm_name == 0 else ChatCohere()
    reranker = CohereReranker()

    # dictionary to store source document name and text used in response
    doc_dict = {"doc_id":'', "text":''}

    # Assuming KnowledgeBase already exist
    def query_kb(sector_id, query, reranker):
        sector_kb = KnowledgeBase(sector_id, reranker=reranker, vector_db=ChromaDB(sector_id), storage_directory=STORAGE_DIR)
        document = sector_kb.query([query])
        if document:
            # save document source data to return later
            doc_id_list = document[0]["doc_id"].split()
            doc_dict["doc_id"] = '_'.join(doc_id_list) + '.pdf'
            doc_dict["text"] = document[0]["text"]
            return document[0]["text"]
        else:
            sector_kb = KnowledgeBase(sector_id, reranker=NoReranker(), vector_db=ChromaDB(sector_id), storage_directory=STORAGE_DIR)
            document = sector_kb.query([query])
            # save document source data to return later
            if document:
                doc_id_list = document[0]["doc_id"].split()
                doc_dict["doc_id"] = '_'.join(doc_id_list)
                doc_dict["text"] = document[0]["text"]
            return document[0]["text"] if document else "No relevant information found."

    # ReAct Automation

    path = f"{STORAGE_DIR}/metadata"   
    files_list = os.listdir(path)
    print(files_list)

    sector_ids = []

    for i in range(len(files_list)):
        sector_id = os.listdir(path)[i][:-5]
        sector_ids.append(sector_id)

    def create_dynamic_tools(knowledge_bases, reranker):
        tools = []
        for kb in knowledge_bases:
            print('next kb')
            tool = Tool(
                name=f"search_{kb}",
                func=lambda query, kb=kb: query_kb(kb, query, reranker),
                description=f"Returns the relevant information for queries about {kb} companies."
            )
            tools.append(tool)
        return tools

    tools = create_dynamic_tools(sector_ids, reranker)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # question = "What is the revenue of Echostar 2021 and WillisLease 2021?"

    agent = initialize_agent(tools, llm=llm, agent="chat-conversational-react-description",max_iterations=2, memory=memory, verbose=True)
    response = agent.run(question)
    for chunk in response:
        yield chunk
    yield f'||Source Document: {doc_dict["doc_id"]}\n\n {doc_dict["text"]}' if doc_dict["doc_id"]!='' else ''

if __name__ == "__main__":
    question = input("Enter your question: ")
    for chunk in response(question):
        print(chunk)