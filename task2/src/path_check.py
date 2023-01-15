import pandas as pd
from neo4j import GraphDatabase
from dbconfig import *
import matplotlib.pyplot as plt

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df

query_check_lifetime = """
Match (p:Path) with p.start_junc as start_id, p.end_junc as end_id, max(p.time)-min(p.time) as Lifetime 
Return Lifetime, collect(start_id+'_'+end_id) as Paths order by Lifetime
"""

res = run_query(query_check_lifetime, params={})
# res is df where second column is np array of lists of strings
driver.close()

counts = [len(a) for a in res['Paths']]
df_plot = pd.DataFrame({"lifetime":res['Lifetime'].to_numpy(), "count":counts})

first_x = 120

plt.scatter(df_plot['lifetime'][0:first_x] ,df_plot['count'][0:first_x])
plt.xlabel("Path lifetime")
plt.ylabel("Path count")
plt.savefig("pathcount_per_lifetime")