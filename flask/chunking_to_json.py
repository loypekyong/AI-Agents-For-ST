import os
import sys
utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(utils_dir)
import argparse
import json
from collections import defaultdict
from dsrag.knowledge_base import KnowledgeBase
from dsrag.document_parsing import extract_text_from_pdf
from dsrag.reranker import NoReranker
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")

def get_folder_paths(base_folder, folder_name):
    current_path = os.getcwd()
    uploads_path = os.path.join(current_path, base_folder)
    
    if not os.path.exists(uploads_path):
        print(f"Error: The directory '{uploads_path}' does not exist.")
        sys.exit(1)

    folder = os.path.join(uploads_path, folder_name)

    return folder

def create_kb(kb, folder_path):
    doc_ids = []
    for file in os.listdir(folder_path):
        if file.endswith('.pdf'):
            print(os.path.join(folder_path, file))
            text = extract_text_from_pdf(os.path.join(folder_path, file))
            print(type(text))
            doc_ids.append(file)
            kb.add_document(doc_id=file, text=text[0])
    return doc_ids

def chunk_documents(kb_id, folder_path, json_path, storage_directory):
    kb = KnowledgeBase(kb_id, reranker=NoReranker(), storage_directory=storage_directory)
    doc_ids = create_kb(kb, folder_path)
    
    # Prepare data for JSON
    # data = []
    for file in doc_ids:
        num_chunks = len(kb.chunk_db.data[file])
        chunks = []
        for i in range(num_chunks):
            chunk = {
                "kb_id": kb_id,
                "doc_id": file,
                "section_title": kb.chunk_db.get_section_title(file, i),
                "chunk_text": kb.chunk_db.get_chunk_text(file, i),
                "document_title": kb.chunk_db.get_document_title(file, i),
                "document_summary": kb.chunk_db.get_document_summary(file, i)
            }
            chunks.append(chunk)
            if i < 10:
                print(chunk)
        
        # Group data by kb_id
        grouped_data = defaultdict(list)
        for entry in chunks:
            grouped_data[entry["kb_id"]].append(entry)
        
        # Write to JSON file
        with open(f'{json_path}{file.split(".")[0]}.json', 'w') as f:
            json.dump(grouped_data, f)

def main():
    pdf_folder = 'flask/uploads/'
    vector_storage_directory = "/app/Dataset/storage"
    json_path = "data_new/"

    # # For benchmarking
    # pdf_folder = 'benchmark\\custom_pdfs'
    # vector_storage_directory = "benchmark\\Dataset\\storage"
    # json_path = "benchmark\\data_new\\"

    print("Starting chunking to json...")
    parser = argparse.ArgumentParser(description='Run Jupyter Notebook for chunking.')
    parser.add_argument('--kb_id', type=str, default='temp', help='Name of kb (kb_id)')
    parser.add_argument('--folder_name', type=str, default='sample', help='Name of folder containing pdf(s)')
    args = parser.parse_args()

    print(args.kb_id, args.folder_name)
    pdf_folder = get_folder_paths(pdf_folder, args.folder_name)
    chunk_documents(args.kb_id, pdf_folder, json_path, vector_storage_directory)

    print("Chunking to json successful!")

if __name__ == "__main__":
    main()