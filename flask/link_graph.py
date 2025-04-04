import sys
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j")
        except Exception as e:
            print("Connection failed:", e)

    def close(self):
        self.driver.close()

    def get_nodes_with_section_title(self, session):
        query = """
        MATCH (n)
        WHERE n.sec_title IS NOT NULL
        RETURN n
        """
        result = session.run(query)
        return [record["n"] for record in result]

    def link_sections(self, session):
        # # Iterate over all pairs of nodes
        session.run("""
        CALL apoc.periodic.iterate(
            "MATCH (n:Section) WHERE n.sec_title IS NOT NULL RETURN n",
            "WITH n
            MATCH (m:Section)
            WITH n, m, apoc.text.sorensenDiceSimilarity(m.sec_title, n.sec_title) AS similarity
            WHERE similarity >= 0.7
            AND NOT ((m)-[:IS_RELATED_TO]->(n) OR (n)-[:IS_RELATED_TO]->(m))
            CREATE (m)-[:IS_RELATED_TO {similarity: similarity}]->(n)",
            {batchSize: 100, parallel: False}
            )
        """)

        session.run("""
        MATCH (a:Section)-[rel:IS_RELATED_TO]->(a) 
        DELETE rel;            
        """)

        # To unlink graphs
        # def link_sections(self, session):
        # # # Iterate over all pairs of nodes
        # session.run("""
        # CALL apoc.periodic.iterate(
        #     "MATCH (n:Section) WHERE n.sec_title IS NOT NULL RETURN n",
        #     "WITH n
        #     MATCH (m:Section) 
        #     WITH n, m, apoc.text.sorensenDiceSimilarity(m.sec_title, n.sec_title) AS similarity
        #     WHERE similarity >= 0.7
        #     MERGE (m)-[:IS_RELATED_TO {similarity: similarity}]->(n)
        #     ON CREATE SET rel.similarity = similarity
        #     ON MATCH SET rel.similarity = GREATEST(rel.similarity, similarity)",
        #     {batchSize: 100, parallel: False}
        # )
        # """)

        # session.run("""
        # MATCH (a:Section)-[rel:IS_RELATED_TO]->(b:Section)
        # WHERE a <> b
        # DELETE rel;            
        # """)

if __name__ == "__main__":
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")  

    connection = Neo4jConnection(uri, user, password)

    try:
        with connection.driver.session() as session:
            print("Linking sections based on similarity...")
            connection.link_sections(session)
            print("Done linking sections based on similarity.")
    except Exception as e:
        print("Error occurred during data creation:", e)
    finally:
        connection.close()