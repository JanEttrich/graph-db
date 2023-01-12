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
    (n)<-[:CONSISTS_OF]-(l:Loop)-[:CONSISTS_OF]->(m), 
    (j)-[:CONSISTS_OF]->(:Node)--(l)--(:Node)<-[:CONSISTS_OF]-(i)
    MERGE (n)<-[:STARTS_WITH]-(p:Path{time:n.time,start_junc:j.global_id, end_junc:i.global_id, path_length:length(len)-2, loop_id:l.id})-[:ENDS_WITH]->(m)
    """

query_add_distance_to_paths = """
    MATCH (p:Path)-[:STARTS_WITH]->(n:Node), 
    relations=(n)-[:SEGMENT*{is_junction:$is_junction}]->(m:Node), 
    (m)<-[:ENDS_WITH]-(p) 
    SET p.distance=reduce(distance=0, r in relationships(relations) | distance + r.distance)
    """

params = {"is_junction": False}
for time in range(50,10000,50):
    params.update({"time":time})
    run_query(query_create_path_nodes, params)
run_query(query_add_distance_to_paths, params)
driver.close()