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
# reranker = CohereReranker()
reranker = NoReranker()

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
question = "What is the revenue of Safran 2022"

prompt = """
You are a financial analyst at a large investment firm. You have been asked to analyze the financial performance of a company.

You run in a loop of Thought, Suggestions ,Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the suitable actions available to you - then return 
PAUSE.
Observation will be the result of running those actions.

Your available actions are:

query_com_kb:
e.g. query_com_kb: What is the revenue of SpiritAeroSystems 2022
Gives the context for the query for Companies in the Commerical Aerospace Industry.

query_uss_kb:
e.g. query_uss_kb: What is the revenue of Echostar 2021
Gives the context for the query for Companies in the Universial Satellite Services Industry.

Example session:

Question: What is the revenue of SpiritAeroSystems 2022 and Echostar 2021
Thought: I need to find the revenue of SpiritAeroSystems 2022 which is a Commerical Aerospace company and Echostar 2021 which is from a Universial Satellite Services company

Action: query_com_kb: SpiritAeroSystems 2022
PAUSE

You will be called again with the result of the action:

"""

system = {"role":"system", 
          "content":prompt}

messages =[]
messages.append(system)
messages.append({"role": "user", "content": question})

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
response_message = response.choices[0].message 
messages.append(response_message)

print(response_message)

tool_calls = response_message.tool_calls
if tool_calls:
    tool_call_id = tool_calls[0].id
    tool_function_name = tool_calls[0].function.name
    tool_query = json.loads(tool_calls[0].function.arguments)['query']

    tool_query = "What is the" + tool_query

    if tool_function_name == "query_com_kb":
        context = query_com_kb(tool_query)
    elif tool_function_name == "query_uss_kb":
        context = query_uss_kb(tool_query)
    else:
        print(f"Unknown tool function: {tool_function_name}")
        context = "I'm sorry, I don't have that information."
        #Exit out of the if statement
        tool_calls = None

    print(context)
    messages.append({
            "role":"tool", 
            "tool_call_id":tool_call_id, 
            "name": tool_function_name, 
            "content":context
        })
    
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print(final_response.choices[0].message.content)
else:
    print(response_message.content)



