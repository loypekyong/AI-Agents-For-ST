from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import NoReranker, CohereReranker

from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf

# import environment variables
from dotenv import load_dotenv

load_dotenv()

llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker()

com_id = "CommAero"
uss_id = "USS"

com_kb = KnowledgeBase(com_id, reranker = CohereReranker(), vector_db=ChromaDB(com_id), storage_directory="~/AI-Agents-For-ST/storage")
uss_kb = KnowledgeBase(uss_id, reranker = CohereReranker(), vector_db=ChromaDB(uss_id), storage_directory="~/AI-Agents-For-ST/storage")



system = {"role":"system", "content":"You are a financial analyst at a large investment firm. You have been asked to analyze the financial performance of a company."}

question = "What is the revenue of General SpiritAeroSystems 2022"

def get_context(kb, query):
    document = kb.query(query)
    context = document[0]["text"]
    return context

user = """

{context}

Based on the information provided, answer the following questions:

{question}
"""

query = [question]
context = get_context(com_kb, query)

print(context)

prompt = user.format(context=context, question=question)

prompt = {"role":"user", "content":prompt}

messages = [system, prompt]

llm = OpenAIChatAPI(model='gpt-4o-mini')


message = []
response = llm.make_llm_call(messages)
print(response)