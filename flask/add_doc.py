import sys
import os
# allow importing dsrag modules
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(utils_dir)
from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import NoReranker, CohereReranker


from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the CO_API_KEY variable
cohere_api_key = os.getenv('CO_API_KEY')

llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker()

def get_kb(kb_id):
    Kb = KnowledgeBase(kb_id, reranker = CohereReranker(), vector_db=ChromaDB(kb_id), storage_directory="~/AI-Agents-For-ST/storage")
    return Kb


def get_file_as_id(folder_path):
    if not os.path.exists(folder_path):
        return ValueError
    folder_name = folder_path.split('/')[-1]
    id = folder_name.split('.')[0]
    
    return id

COMM_ID = "Commercial_Aerospace"
USS_ID = "USS"

def Kb_add_doc(Kb, file_path):
    id = get_file_as_id(file_path)
    text = extract_text_from_pdf(file_path)
    Kb.add_document(doc_id=id, text=text[0])
    return Kb

com_kb = KnowledgeBase(COMM_ID, reranker = CohereReranker(), vector_db=ChromaDB(COMM_ID), storage_directory="~/AI-Agents-For-ST/storage")
uss_kb = KnowledgeBase(USS_ID, reranker = CohereReranker(), vector_db=ChromaDB(USS_ID), storage_directory="~/AI-Agents-For-ST/storage")


