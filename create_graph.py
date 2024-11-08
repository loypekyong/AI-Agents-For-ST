import sys
import os
sys.path.append('C:/Users/limyo/anaconda3/envs/dsrag/Lib/site-packages/neo4j')
print(sys.executable)
from neo4j import GraphDatabase
import json
from collections import defaultdict

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

    # def create_data(session, data):
    #     # Create Document Node
    #     doc_query = f'''
    #     CREATE (d:Document {{
    #         kb_id: '{data["kb_id"]}',
    #         doc_id: '{data["doc_id"]}',
    #         doc_title: '{data["document_title"]}',
    #         doc_summary: '{data["document_summary"]}'
    #     }}) 
    #     '''
    #     session.run(doc_query)

    #     # Create Section Node
    #     section_query = f'''
    #     CREATE (s:Section {{
    #         sec_title: '{data["section_title"]}',
    #         sec_summary: '{data["section_summary"]}',
    #         sec_chunk_text: '{data["chunk_text"]}'
    #     }}) 
    #     '''
    #     session.run(section_query)

    #     # Create Relationship between Document and Section
    #     relationship_query = f'''
    #     MATCH (d:Document {{doc_id: '{data["doc_id"]}'}}), 
    #         (s:Section {{title: '{data["section_title"]}'}})
    #     CREATE (d)-[:CONTAINS]->(s)
    #     '''
    #     session.run(relationship_query)
    def load_json_files_from_directory(self, directory):
        grouped_data = defaultdict(list)
    
        # Traverse the directory recursively
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.json'):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r') as f:
                        try:
                            # Load the data from the JSON file
                            data = json.load(f)
                            # Check if data is a list
                            if isinstance(data, dict):
                                for kb_id, entry in data.items():
                                    for ind in range(len(entry)):
                                        if 'doc_id' in entry[ind]:
                                            print("key: ", entry[ind]["doc_id"])
                                            key = entry[ind]["doc_id"]
                                            grouped_data[key].append(entry[ind])
                                        else:
                                            print(f"Warning: 'kb_id' not found in entry: {entry}")
                            else:
                                # print(f"Warning: Expected a dict, got {type(data)} instead.")
                                print()

                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_path}: {e}")

        return grouped_data
    
    def create_data(self, session, data):
        with session.begin_transaction() as tx:
            for doc_id, entries in data.items():
                document_title = entries[0]['document_title']
                document_summary = entries[0]['document_summary']
                doc_year = doc_id.split(".")[0][-4:]
                kb_id = entries[0]["kb_id"]
                doc_id_sections = doc_id.split("_")
                print(doc_id_sections)
                print(doc_year)
                print("--------------")


                root_query = f'''
                MERGE (r:Root {{
                    root_id: $root_id
                }}) 
                ON CREATE SET r.kb_id=$kb_id
                '''
                tx.run(root_query, kb_id=kb_id, root_id=doc_id_sections[0])
                

                ########################################################################
                

                sector_query = f'''
                MERGE (sc:Sector {{
                    sector_id: $sector_id
                }}) 
                ON CREATE SET sc.kb_id=$kb_id
                '''
                tx.run(sector_query, kb_id=kb_id, sector_id=doc_id_sections[1])

                relationship_query = f'''
                MATCH (r:Root {{kb_id: $kb_id}}),
                    (sc:Sector {{sector_id: $sector_id}}) 
                MERGE (r)-[:HAS_SECTOR]->(sc)
                '''
                tx.run(relationship_query, kb_id=kb_id, sector_id=doc_id_sections[1])
            

                ########################################################################


                department_query = f'''
                MERGE (dp:Department {{
                    department_id: $department_id
                }}) 
                ON CREATE SET dp.kb_id=$kb_id
                '''
                tx.run(department_query, kb_id=kb_id, department_id=doc_id_sections[2])

                relationship_query = f'''
                MATCH (sc:Sector {{kb_id: $kb_id}}),
                    (dp:Department {{department_id: $department_id}}) 
                MERGE (sc)-[:HAS_DEPARTMENT]->(dp)
                '''
                tx.run(relationship_query, kb_id=kb_id, department_id=doc_id_sections[2])
            

                # # ########################################################################


                doc_query = f'''
                MERGE (d:Document {{
                    doc_id: $doc_id
                }}) 
                ON CREATE SET d.department_id=$department_id
                '''
                tx.run(doc_query, department_id=doc_id_sections[2], doc_id=doc_id.split(".")[0][:-4])

                relationship_query = f'''
                MATCH (dp:Department {{department_id: $department_id}}),
                    (d:Document {{doc_id: $doc_id}}) 
                MERGE (dp)-[:HAS_DOCUMENT]->(d)
                '''
                tx.run(relationship_query, department_id=doc_id_sections[2], doc_id=doc_id.split(".")[0][:-4])

                # ########################################################################


                year_query = f'''
                MERGE (y:Year {{
                    doc_year: $doc_year
                }}) 
                ON CREATE SET y.doc_id=$doc_id
                '''
                tx.run(year_query, doc_id=doc_id.split(".")[0][:-4], doc_year=doc_year)
        
                relationship_query = f'''
                MATCH (d:Document {{doc_id: $doc_id}}),
                    (y:Year {{doc_year: $doc_year}}) 
                MERGE (d)-[:IN_YEAR]->(y)
                '''
                tx.run(relationship_query, doc_id=doc_id.split(".")[0][:-4], doc_year=doc_year)
            
                # ########################################################################

            
                doc_title = f'''
                MERGE (dt:Document_title {{
                    doc_title: $doc_title
                }}) 
                ON CREATE SET dt.doc_id=$doc_id, dt.doc_year=$doc_year
                '''
                tx.run(doc_title, doc_id=doc_id.split(".")[0][:-4], doc_title=document_title, doc_year=doc_year)

                relationship_query = f'''
                MATCH (y:Year {{doc_year: $doc_year}}),
                    (dt:Document_title {{doc_title: $doc_title}}) 
                MERGE (y)-[:COVERS]->(dt)
                '''
                tx.run(relationship_query, doc_year=doc_year, doc_title=document_title)

            

                # ########################################################################


                doc_summ = f'''
                MERGE (ds:Document_summ {{
                    doc_summary: $doc_summary
                }}) 
                ON CREATE SET ds.doc_title=$doc_title
                '''
                tx.run(doc_summ, doc_title=document_title, doc_summary=document_summary)

                relationship_query = f'''
                MATCH (dt:Document_title {{doc_title: $doc_title}}),
                    (ds:Document_summ {{doc_summary: $doc_summary}}) 
                MERGE (dt)-[:HAS_SUMMARY]->(ds)
                '''
                tx.run(relationship_query, doc_title=document_title, doc_summary=document_summary)
            

                ########################################################################


                for entry in entries:
                    # Create Section Node
                    sec_title = entry["section_title"]
                    if sec_title is None:
                        sec_title = ""
                    section_title = f'''
                    MERGE (s:Section {{
                        sec_title: $sec_title,
                        sec_summary: $sec_summary
                    }})
                    ON CREATE SET s.doc_summary=$doc_summary, s.doc_title=$doc_title
                    '''
                    tx.run(section_title, sec_summary=entry["section_summary"], sec_title=sec_title, doc_summary=document_summary, doc_title=document_title)

                    # Create Relationship between Document and Section
                    relationship_query = f'''
                    MATCH (ds:Document_summ {{doc_summary: $doc_summary}}), 
                        (s:Section {{sec_title: $sec_title, doc_title: $doc_title}})
                    MERGE (ds)-[:HAS_SECTION_TITLE]->(s)
                    '''
                    tx.run(relationship_query, doc_summary=document_summary, sec_title=sec_title, doc_title=document_title)


                    ########################################################################


                    # s.sec_summary=$sec_summary, s.sec_chunk_text=$sec_chunk_text 
                    # sec_summary=entry["section_summary"], sec_chunk_text=entry["chunk_text"]


if __name__ == "__main__":
    uri = "neo4j+s://0406f932.databases.neo4j.io"
    user = "neo4j"
    password = "0vLIefc9JZtISxmsbPrAhMGZDtnZ8HY681j2HVjmZyQ"  

    connection = Neo4jConnection(uri, user, password)

    # Load data from JSON file
    # with open('test_data.json', 'r') as f:
    #     data = json.load(f)
    directory_path = 'data/'  # Change to your directory
    data = connection.load_json_files_from_directory(directory_path)

    # data = {
    #     'kb_id': 'st_eng_1h2023',
    #     'doc_id': 'st-engineering-1h2023-financial-statement',
    #     'section_title': 'Consolidated Income Statement for the First Half-Year',
    #     'section_summary': '',
    #     'chunk_text': "1 CONSOLIDATED INCOME STATEMENT FOR THE FIRST HALF -YEAR  ENDED 30 JUNE 2023...",
    #     'document_title': 'CONDENSED INTERIM FINANCIAL STATEMENTS FOR THE FIRST HALF -YEAR ENDED 30 JUNE 2023',
    #     'document_summary': "This document is about: ..."
    # }
    # print(len(data))
    # with open(f'data/out.json', 'w') as f:
    #         json.dump(data, f)
    try:
        with connection.driver.session() as session:
            connection.create_data(session, data)
            print("Done")
    except Exception as e:
        print("Error occurred during data creation:", e)

    # connection.close()