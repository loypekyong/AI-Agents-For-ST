from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.graphs import Neo4jGraph

import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  
OPENAI_API = os.getenv("OPENAI_API")


def initialize_neo4j():
    return Neo4jGraph(
        url=NEO4J_URI,  # Replace with your Neo4j URI
        username=NEO4J_USERNAME,             # Replace with your Neo4j username
        password=NEO4J_PASSWORD      
    )


def generate_cypher_query(llm, query):
    cypher_prompt = PromptTemplate(
        input_variables=["query"],
        template="Given the user's query: {query}, generate a Cypher query to extract the relevant information from the Neo4j graph."
    )
    cypher_generator = LLMChain(llm=llm, prompt=cypher_prompt)
    return cypher_generator.run(query)


def query_neo4j(graph, llm, prompt):
    generate_cypher_query = generate_cypher_query(llm, prompt)
    results = graph.query(generate_cypher_query)
    return results