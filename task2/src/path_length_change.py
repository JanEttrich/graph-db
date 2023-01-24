import pandas as pd
from neo4j import GraphDatabase
import numpy as np

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=("dbprak08", "penguin-region-iris-maxwell-baron-7173"))

def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df

query_check_length = """
Match (p:Path) Return (p.start_junc + "_"+ p.end_junc) as Paths, collect(p.path_length)
"""

query_check_lifetime = """
Match (p:Path) with p.start_junc as start_id, p.end_junc as end_id, max(p.time)-min(p.time) as Lifetime 
Return  (start_id+'_'+end_id) as Paths, Lifetime
"""

res = run_query(query_check_length, params={})
lifetime_res = run_query(query_check_lifetime, params={})
res.sort_values(by="Paths")
lifetime_res.sort_values(by="Paths")
res["Lifetime"] = lifetime_res["Lifetime"]
lifetime_res.sort_values
lst = []
for l in res["collect(p.path_length)"]:
    lst.append(l[-1] - l[0])

res["length_change"] = lst
print(res)
print(np.corrcoef(res["length_change"], res["Lifetime"]))

driver.close()