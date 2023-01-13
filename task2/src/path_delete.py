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

query_delete_paths = "MATCH(p:Path{time:$time}) DETACH DELETE p"
params = {}
for time in range(50,10000,50):
    params.update({"time":time})
    run_query(query_delete_paths, params)
driver.close()