import os
from dsrag.document_parsing import extract_text_from_pdf

def create_KB(uss_kb, folder_path, doc_ids):
    for file in os.listdir(folder_path):
        if file.endswith('.pdf'):
            print(os.path.join(folder_path, file))
            text = extract_text_from_pdf(os.path.join(folder_path, file))
            print(type(text))
            doc_ids.append(file)
            uss_kb.add_document(doc_id=file, text=text[0])
    return doc_ids
