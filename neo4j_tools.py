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
        validate_cypher=True,
        graph=graph,
        allow_dangerous_requests=True,
        verbose=True,
        return_intermediate_steps=True,
        temperature=0,
    )
    return chain.run({"query": query})


def query_neo4j(graph, llm, query):
    cypher_prompt = PromptTemplate(
        input_variables=["query"],
        template=(f"You are a graph query assistant. Given the user's question: {query}, "
                  "generate an appropriate Cypher query to retrieve the relevant data from the Neo4j graph. "
                  "Note: You are strongly prohibited from generating queries that can result in permanent alteration of the original graph.")
    )
    query = f"""
            You are an expert in generating Cypher queries for Neo4j. Your task is to generate a Cypher query based on the user's question and the graph schema. 
            Carefully follow these instructions:
            - Use the example query as the format and structure reference.
            - Always use `r.kb_id` instead of `r.root_id` when traversing nodes.
            - The kb to be used is 'uss_kb_id' for USS or 'commAero' for Commercial Aerospace. Take note of which kb to use.
            - Focus on retrieving `sec_chunks` related to company information with keywords like 'revenue', 'income', or 'earnings'.
            - [Optional] Given a key from the initial query, you can come up with similar meaning words to help with the search. Like how we can also use 'income' and 'earnings' from the original word 'revenue'. 
            - Limit the first result to 1 node, look through its connections, then limit the second results to 20 nodes.
            - Ensure the query matches the schema and uses only valid properties.
            - Use the provided query as a reference for wording but strictly adhere to the example query structure.

            Example for key word search:
            '''
            MATCH (root:Root)-[:HAS_SECTOR]->(:Sector)-[:HAS_DEPARTMENT]->(dept:Department)-[:IN_YEAR]->(year:Year)-[:COVERS]->(:Document_title)-[:HAS_SUMMARY]->(:Document_summ)-[:HAS_SECTION_TITLE]->(section:Section)
            WHERE (dept.kb_id = 'uss_kb_id' OR section.sec_chunks CONTAINS 'revenue' OR section.sec_chunks CONTAINS 'income' OR section.sec_chunks CONTAINS 'earnings') AND year.doc_year = '2022'
            WITH section
            ORDER BY size([chunk IN split(section.sec_chunks, ' ') WHERE chunk CONTAINS 'revenue' OR chunk CONTAINS 'income' OR chunk CONTAINS 'earnings']) DESC
            LIMIT 1
            MATCH (section)-[:IS_RELATED_TO]->(related:Section)
            RETURN related AS related_sections
            LIMIT 20
            '''

            Given the user's question: '{query}' and the schema: '{graph.schema}', generate a Cypher query following the example's structure exactly. Ensure:
            - The WHERE clause prioritizes `kb_id` and uses `CONTAINS` for `sec_chunks`.
            - Results are limited to 20 nodes.
            - The query matches the schema faithfully.

            
            Do NOT deviate from the example structure or introduce properties not in the schema.
    """
    gen_cypher = generate_cypher_query(llm, graph, query, cypher_prompt)
    lines = gen_cypher.strip().split('\n') # Split into lines and strip whitespace
    cleaned_gen_q = '\n'.join(lines[1:-1]) 

    res = graph.query(cleaned_gen_q)
    return res