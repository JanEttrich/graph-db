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

query_check_lifetime = """
Match (p:Path) with p.start_junc as start_id, p.end_junc as end_id, max(p.time)-min(p.time) as Lifetime 
Return Lifetime, collect(start_id+'_'+end_id) as Paths
"""

res = run_query(query_check_lifetime, params={})
count = 0
for a in res['Paths']:
    count+=len(a)
print(count)
driver.close()