from dsrag.knowledge_base import KnowledgeBase
from dsrag.llm import OpenAIChatAPI
from dsrag.reranker import CohereReranker, NoReranker
from dsrag.database.vector.chroma_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf

from dotenv import load_dotenv
from openai import OpenAI
import os, json

load_dotenv()

# Initialize OpenAI and KnowledgeBase
llm = OpenAIChatAPI(model='gpt-4o-mini')
reranker = CohereReranker()

# com_id = "CommAero"
# uss_id = "USS"

# com_kb = KnowledgeBase(com_id, reranker=reranker, vector_db=ChromaDB(com_id), storage_directory="~/AI-Agents-For-ST/storage")
# uss_kb = KnowledgeBase(uss_id, reranker=reranker, vector_db=ChromaDB(uss_id), storage_directory="~/AI-Agents-For-ST/storage")

# Assuming KnowledgeBase already exist
def query_kb(sector_id, query, reranker):
    sector_kb = KnowledgeBase(sector_id, reranker=reranker, vector_db=ChromaDB(sector_id), storage_directory="~/AI-Agents-For-ST/storage")
    document = sector_kb.query(query)
    return document[0]["text"] if document else "No relevant information found."

# def query_uss_kb(query):
#     document = uss_kb.query(query)
#     return document[0]["text"] if document else "No relevant information found."

# ReAct Automation

path = "./storage/metadata"   
files_list = os.listdir(path)

sector_ids = []

for i in range(len(files_list)):
    sector_id = os.listdir(path)[i][:-5]
    sector_ids.append(sector_id)

tools = []

for i in sector_ids:
    tool = {"type": "function",
            "function": {
                "name": f"query_{i}_kb",
                "description": f"Query a knowledge base to retrieve relevant info for companies related to {i}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"User's question about {i} companies."
                        },
                    },
                    "required": ["query"]
                    }
                }
            }
    tools.append(tool)

client = OpenAI()
question = "What is the revenue of Airbus 2022 and Echostar 2021"

prompt = """
You are a financial analyst at a large investment firm. You have been asked to analyze the financial performance of a company.

You run in a loop of Thought, Suggestions, Action, PAUSE, Observation.
At the end of the loop, you output an Answer.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the suitable actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

query_kb:
- Example: query_com_kb: What is the revenue of SpiritAeroSystems 2022
- Retrieves information about companies in the Commercial Aerospace Industry.

query_kb:
- Example: query_uss_kb: What is the revenue of Echostar 2021
- Retrieves information about companies in the Universal Satellite Services Industry.

Example session:

Question: What is the revenue of SpiritAeroSystems in 2022 and General Echostar in 2021
Thought: I need to find the revenue of SpiritAeroSystems 2022 (Commercial Aerospace) and Echostar 2021 (Universal Satellite Services).

Action: query_kb: SpiritAeroSystems 2022
PAUSE
"""

# Start conversation
messages = [{"role": "system", "content": prompt}]
messages.append({"role": "user", "content": question})

# First API call
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Print the first response
print(completion.choices[0].message.content)
#append the response to the messages list
messages.append(completion.choices[0].message)

# Process tool calls
if completion.choices[0].message.tool_calls:
    tool_calls = completion.choices[0].message.tool_calls
    tool_responses = []

    for tc in tool_calls:
        tool_call_id = tc.id
        tool_function_name = tc.function.name
        tool_query = json.loads(tc.function.arguments)["query"]

        found = False

        for i in sector_ids:
            # Execute the correct function
            if tool_function_name == f"query_{i}_kb":
                print(f"Querying {i} KB: {tool_query}")
                context = query_kb(i,tool_query, reranker)
                Found = True
            # elif tool_function_name == "query_uss_kb":
            #     print(f"Querying Universal Satellite Services KB: {tool_query}")
            #     context = query_kb(tool_query)
        if not Found:
            print(f"Unknown tool function: {tool_function_name}")
            context = "No relevant information found."

        # Store the response properly
        tool_responses.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_function_name,
            "content": context
        })
        

    # Append all tool responses after processing tool calls
    messages.extend(tool_responses)
    print(messages)

    # Make another API call to get the final response
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    print(final_response.choices[0].message.content)
else:
    # If no tool calls were made, just return the initial response
    print(completion.choices[0].message.content)