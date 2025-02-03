from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import CohereReranker, NoReranker

from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf

# import environment variables
from dotenv import load_dotenv
from openai import OpenAI
import os, json

load_dotenv()

llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker()

com_id = "CommAero"
uss_id = "USS"

com_kb = KnowledgeBase(com_id, reranker = reranker, vector_db=ChromaDB(com_id), storage_directory="~/AI-Agents-For-ST/storage")
uss_kb = KnowledgeBase(uss_id, reranker = reranker, vector_db=ChromaDB(uss_id), storage_directory="~/AI-Agents-For-ST/storage")

def query_com_kb(query):
    document = com_kb.query(query)
    context = document[0]["text"]
    return context

def query_uss_kb(query):
    document = uss_kb.query(query)
    context = document[0]["text"]
    return context

tools = [{
    "type": "function",
    "function": {
        "name": "query_com_kb",
        "description": "Query a knowledge base to retrieve relevant info for companies related to Commerical Aerospace.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What is the user's question or search query for companies related to Commerical Aerospace."
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
}, {
    "type": "function",
    "function": {
        "name": "query_uss_kb",
        "description": "Query a knowledge base to retrieve relevant info for companies related to Universal Satellite Services.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What is the user's question or search query for companies related to Universal Satellite Services."
                },
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    }
}]

client = OpenAI()
question = "What is the revenue of Echostar 2021"

system = {"role":"system", "content":"You are a financial analyst at a large investment firm. You have been asked to analyze the financial performance of a company."}

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        system,
        {"role": "user", "content": question}
    ],
    tools=tools
)

# Print the entire completion object for debugging
# print(completion)

# Check if tool_calls is None
if completion.choices[0].message.tool_calls is None:
    print("No tool calls were made.")
else:
    print("Tool call was made.")
    tool_call = completion.choices[0].message.tool_calls[0]
    print(tool_call.function.name, tool_call.function.arguments)
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    


    # # Create a response message for the tool call
    # tool_response_message = {
    #     "role": "tool",
    #     "content": result,
    #     "tool_call_id": tool_call.id
    # }

    # # Send the response message back to the LLM to continue the conversation
    # final_completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": "You are a financial analyst at a large investment firm. You have been asked to analyze the financial performance of a company."},
    #         {"role": "user", "content": question},
    #         {"role": "assistant", "content": "", "tool_calls": [tool_call]},
    #         tool_response_message
    #     ],
    #     tools=tools
    # )



def get_context(name , query):
    if name == "query_com_kb":
        document = com_kb.query(query)
    elif name == "query_uss_kb":
        document = uss_kb.query(query)
    else:
        document = None
    context = document[0]["text"]
    return context

user = """

{context}

Based on the information provided, answer the following questions:

{question}
"""

query = [question]
context = get_context(function_name, query)

print(context)

prompt = user.format(context=context, question=question)

prompt = {"role":"user", "content":prompt}

messages = [system, prompt]

llm = OpenAIChatAPI(model='gpt-4o-mini')


message = []
response = llm.make_llm_call(messages)
print(response)