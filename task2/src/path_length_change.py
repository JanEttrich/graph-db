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

query_check_length = """
Match (p:Path) Return (p.start_junc + "_"+ p.end_junc), collect(p.path_length)
"""

res = run_query(query_check_length, params={})
print(res)
driver.close()