import pandas as pd
from neo4j import GraphDatabase
from dbconfig import *

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df


query_create_path_nodes = """
    MATCH len=(j:Junction)-[:CONSISTS_OF]->(n:Node{time:$time})-[:SEGMENT*{is_junction:$is_junction}]->(m:Node)<-[:CONSISTS_OF]-(i:Junction), 
    (n)<-[:CONSISTS_OF]-(l:Loop)-[:CONSISTS_OF]->(m) 
    MERGE (n)<-[:IN_PATH]-(p:Path{time:n.time,id:toString(n.id)+"-"+toString(m.id), path_length:length(len)-2})-[:IN_PATH]->(m)
    """

params = {"is_junction": False, "time": 50}
result = run_query(query_create_path_nodes, params)
driver.close()