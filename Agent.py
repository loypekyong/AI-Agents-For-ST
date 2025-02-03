import openai
import re
import httpx
import os
from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv()

client = OpenAI()

prompt = """
You run in a loop of Thought, Suggestions ,Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the suitable actions available to you - then return 
PAUSE.
Observation will be the result of running those actions.

Your available actions are:

find_industry:
e.g. find_industry: SpiritAeroSystems
Finds the industry of the company

query_com_kb:
e.g. query_com_kb: What is the revenue of SpiritAeroSystems 2022
Gives the context for the query for Companies in the Commerical Aerospace Industry

query_uss_kb:
e.g. query_uss_kb: What is the revenue of Echostar 2021
Gives the context for the query for Companies in the Unmanned Systems Industry

Example session:

Question: What is the revenue of SpiritAeroSystems 2022 and Echostar 2021
Thought: I need to find the industry of the companies

Action: find_industry: SpiritAeroSystems
PAUSE

You will be called again with the result of the action:


""".strip()


class Agent
    def