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


query_count_loops_in_timeslice = """
    MATCH (n:Loop {time:$time})
    RETURN count(n)
    """

params = {"time": 50}
result = run_query(query_count_loops_in_timeslice, params)
driver.close()
print(result)