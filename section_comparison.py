from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import os

openai_api = "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"
os.environ["OPENAI_API_KEY"] = openai_api

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embeddings(text):
  response = client.embeddings.create(
    model = 'text-embedding-ada-002',
    input = text 
  )

  return response.data[0].embedding

def cosine_similarity(emb1, emb2):
  return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

def get_similarity(text1, text2):
  emb1 = get_embeddings(text1)
  emb2 = get_embeddings(text2)

  similarity = cosine_similarity(emb1, emb2)

  return similarity

# Test Case
if __name__ == "__main__":
  text1 = """Comtech is a global leader in next-gen 911 systems and critical communication technologies, 
          achieving $581.7 million in consolidated net sales in fiscal 2021 despite COVID-19 challenges."""

  text2 = """The document highlights Comtech's strong future revenue visibility exceeding $1.0 billion, excluding additional potential LEO opportunities.
          The acquisition of UHP Networks Inc. enhances their satellite technologies, and they have expanded market leadership in NG-911 services. 
          Frost & Sullivan recognized Comtech for notable market growth."""

  # print(get_embeddings(text1))
  print(get_similarity(text1, text2))