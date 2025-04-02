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
        validate_cypher=True,
        graph=graph,
        allow_dangerous_requests=True,
        verbose=False,
        return_intermediate_steps=False,
        temperature=0,
        return_intermediate_steps=False,
        temperature=0,
    )
    return chain.run({"query": query})


def query_neo4j(graph, llm, query):
    json_filenames = [f for f in os.listdir("data_new/") if f.endswith('.json')]
    print(json_filenames)
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
            - The kb to be used is 'uss_kb_id' for USS or 'commAero_kb_id' for Commercial Aerospace. Take note of which kb to use.
            - Pick out words in the original query that can be found in the `section_source` attributes provided below for use in searching. 
            - Focus on retrieving `sec_chunks` related to company information with keywords like 'revenue', 'income', or 'earnings'.
            - [Optional] Given a key from the initial query, you can come up with similar meaning words to help with the search. Like how we can also use 'income' and 'earnings' from the original word 'revenue'. 
            - Limit the first result to 1 node based on strictly related departments, sectors, and other constraints, then limit the second results to 10 related nodes.
            - Ensure the query matches the schema and uses only valid properties.
            - Return the details of the nodes and their `section_source` attribute instead of `doc_id`.
            - Order the final results by `section_source`.

            Given the user's question: '{query}', the graph schema: '{graph.schema}', and the naming scheme for the original file names and `section_source` attribute in 'Section': {json_filenames}, generate a Cypher query following the example's structure exactly. Ensure:
            - The `WHERE` clause prioritizes `kb_id` and uses `CONTAINS` for `sec_chunks`, and the `section_source` attribute to limit the scope within documents of the same IDs if and only if applicable.
            - Use 'sector_id', 'department_id', or 'year' as an empty string ('') when not explicitly provided.
            - Final results are limited to 10 nodes.
            - The query matches the schema faithfully.

            Do NOT deviate from the example structure or introduce properties not in the schema.

            The template to follow uses the original file names and `section_source` provided: 'company_sectorid_departmentid_year' and keywords like: 'key_word'. Generate similar keywords to 'key_word' like: 'similar_word_1' and 'similar_word_2'.

            Thus, an example for keyword search, given that we know it is about USS, Satcom, Viasat, and year 2022 (directly asking about USS_Satcom_Viasat_2022 document):
            '''
            MATCH (root:Root)-[:HAS_SECTOR]->(:Sector)-[:HAS_DEPARTMENT]->(dept:Department)-[:IN_YEAR]->(year:Year)-[:COVERS]->(:Document_title)-[:HAS_SUMMARY]->(:Document_summ)-[:HAS_SECTION_TITLE]->(section:Section)
            WHERE dept.kb_id = 'uss_kb_id'
                AND (toLower(section.section_source) CONTAINS 'uss' OR 'uss' IS NULL)
                AND (toLower(section.section_source) CONTAINS 'satcom' OR 'satcom' IS NULL)
                AND (toLower(section.section_source) CONTAINS 'viasat' OR 'viasat' IS NULL)
                AND year.doc_year = '2022'
                AND (toLower(section.sec_chunks) CONTAINS 'revenue' OR toLower(section.sec_chunks) CONTAINS 'income' OR toLower(section.sec_chunks) CONTAINS 'earnings')
                
            WITH section

            OPTIONAL MATCH (section)-[:IS_RELATED_TO]->(related:Section)
            WITH section, collect(related) AS related_sections
            RETURN section AS primary_section, [r IN related_sections | r.section_source] AS related_section_sources
            ORDER BY section.section_source
            LIMIT 10
            '''

            If some fields are missing, and we know it is about USS, Viasat only, we can use:
            '''
            MATCH (root:Root)-[:HAS_SECTOR]->(:Sector)-[:HAS_DEPARTMENT]->(dept:Department)-[:IN_YEAR]->(year:Year)-[:COVERS]->(:Document_title)-[:HAS_SUMMARY]->(:Document_summ)-[:HAS_SECTION_TITLE]->(section:Section)
            WHERE dept.kb_id = 'uss_kb_id'
                AND (toLower(section.section_source) CONTAINS 'uss' OR 'uss' IS NULL)
                AND (toLower(section.section_source) CONTAINS 'viasat' OR 'viasat' IS NULL)
                AND (toLower(section.sec_chunks) CONTAINS 'revenue' OR toLower(section.sec_chunks) CONTAINS 'income' OR toLower(section.sec_chunks) CONTAINS 'earnings')
                
            WITH section

            OPTIONAL MATCH (section)-[:IS_RELATED_TO]->(related:Section)
            WITH section, collect(related) AS related_sections
            RETURN section AS primary_section, [r IN related_sections | r.section_source] AS related_section_sources
            ORDER BY section.section_source
            LIMIT 10
            '''
    """
    gen_cypher = generate_cypher_query(llm, graph, query, cypher_prompt)
    lines = gen_cypher.strip().split('\n') # Split into lines and strip whitespace
    cleaned_gen_q = '\n'.join(lines[1:-1]) 

    res = graph.query(cleaned_gen_q)

    grouped_sections = {}

    for record in res:
        primary_section = record["primary_section"]
        section_source = primary_section["section_source"]

        if section_source not in grouped_sections:
            grouped_sections[section_source] = []
        grouped_sections[section_source].append(primary_section)
    return grouped_sections