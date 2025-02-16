import sys
import os
sys.path.append('C:/Users/limyo/anaconda3/envs/dsrag/Lib/site-packages/neo4j')
from neo4j import GraphDatabase
import json
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

class Neo4jDeletion:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j")
        except Exception as e:
            print("Connection failed:", e)

    def close(self):
        self.driver.close()

    def check_exists(self, session, label, attribute, value):
        with session.begin_transaction() as tx:
            query_bool = f'''
                OPTIONAL MATCH (n:{label} {{{attribute}: $value}})
                RETURN n IS NOT NULL AS Exists
            '''
            tx.run(query_bool, value=value)
        return query_bool

    def delete_node(self, session, ls):
        """
        label(node_label) = ls[0]
        attribute(primary key) = ls[1]
        value(primary_value) = ls[2]
        
        Success: Delete a particular node, together with its child nodes and its relationships --> connection close
        Failure: Node cannot be found --> prints error statement --> connection close
        """
        label = ls[0]
        attribute = ls[1]
        value = ls[2]
        # rm_dups = ls[3]
        if self.check_exists(session, label, attribute, value):  
            with session.begin_transaction() as tx:
                # Delete node, its relationships and its child nodes
                label = ls[0]
                attribute = ls[1]
                value = ls[2]
                
                # section_query = f'''
                #     MATCH path = (n:{label} {{{attribute}: $value}})-[*0..]->(x)
                #     WHERE all(node in nodes(path) WHERE node.doc_title = $value)
                #     WITH collect(x) AS nodesToDelete
                #     UNWIND nodesToDelete AS node
                #     OPTIONAL MATCH (node)-[r]->(other)
                #     DELETE r
                #     WITH node
                #     DETACH DELETE node
                # '''

                # Match the root node with the given label and attribute
                # Recursively match all child nodes connected to the root
                # Ensure all nodes in the path share the same property value
                # Collect all nodes and relationships to delete
                # Match relationships of nodes to delete
                # Explicitly delete the relationships
                # Then delete the nodes
                
                section_query = f'''
                    MATCH (n:{label} {{{attribute}: $value}})
                    OPTIONAL MATCH path = (n)-[*0..]->(x)
                    WHERE all(node IN nodes(path) WHERE node.{attribute} = $value)
                    WITH collect(DISTINCT x) AS childNodes, n
                    UNWIND childNodes + [n] AS nodesToDelete
                    OPTIONAL MATCH (nodesToDelete)-[r]-()
                    DELETE r
                    DETACH DELETE nodesToDelete
                '''
                
                res = tx.run(section_query, value=value)

                summary = res.consume()
                nodes_deleted = summary.counters.nodes_deleted
                relationships_deleted = summary.counters.relationships_deleted

                print(f"{nodes_deleted} nodes and {relationships_deleted} relationships deleted")

                # if rm_dups:
                #     self.rel_cleanup(session)
        else:
            print(f"Node label {label} with attribute: value {attribute}:{value} does not exist; 0 nodes and 0 relationships deleted")

    # def rel_cleanup(self, session):
    #     with session.begin_transaction() as tx:
    #         cleanup_query = f'''
    #                 MATCH (a)-[r]->(b)
    #                 WITH a, b, type(r) AS relType, collect(r) AS rels
    #                 WHERE size(rels) > 1
    #                 FOREACH (r IN tail(rels) | DELETE r)
    #         '''
                
    #         tx.run(cleanup_query)
    #         print("Clean up done")


if __name__ == "__main__":
    # Check if arguments are correct
    if len(sys.argv) < 4:
        print("Usage: python delete_graph.py label attribute value")
        sys.exit(1)

    label = sys.argv[1]
    attribute = sys.argv[2]
    value = sys.argv[3]
    # rm_dups = sys.argv[4]

    # Establish connection
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")  

    connection = Neo4jDeletion(uri, user, password)

    try:
        with connection.driver.session() as session:
            connection.delete_node(session, [label, attribute, value])
            print("Node successfully deleted")
    except Exception as e:
        print("Error occurred during node deletion:", e)

    connection.close()