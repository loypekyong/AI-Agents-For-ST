from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain.graphs import Neo4jGraph
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  
OPENAI_API = os.getenv("OPENAI_API")


def initialize_neo4j():
    return Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD      
    )


def generate_cypher_query(llm, graph, query, cypher_prompt):
    chain = GraphCypherQAChain.from_llm(
        llm=llm, 
        prompt=cypher_prompt,
        graph=graph,
        allow_dangerous_requests=True,
        verbose=False,
    )
    return chain.run({"query": query})


def query_neo4j(graph, llm, query):
    cypher_prompt = PromptTemplate(
        input_variables=["query"],
        template=("You are a graph query assistant. Given the user's question: {query}, "
                  "generate an appropriate Cypher query to retrieve the relevant data from the Neo4j graph. "
                  "Note: You are strongly prohibited from generating queries that can result in permanent alteration of the original graph.")
    )
    res = generate_cypher_query(llm, graph, query, cypher_prompt)
    return res