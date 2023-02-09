import os
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


loop_query = """MATCH (l:Loop{time:$time}) RETURN l.global_id as id"""
junction_query = """MATCH (j:Junction{time: $time}) RETURN j.global_id, j.type"""
create_eloop_query = """CREATE (:ELoop{time: $time, id:$id, jtypes:$jtypes})"""
create_connections_query = """
MATCH (l1:ELoop{time: $time1, id:$id1}), (l2:ELoop{time: $time2, id:$id2})
MERGE (l1)-[:CONNECTION]-(l2)"""

final_df = pd.read_csv("out/dataframe.csv")
final_df.set_index(["id", "time"], inplace=True)
final_df["jtypes"] = [x.strip("[]").split(",") for x in final_df["jtypes"]]
final_df["connected_loops"] = [
    x.strip("[]").split(",") for x in final_df["connected_loops"]
]

# curr_time = 50
# for index, row in final_df.iterrows():
#     run_query(create_eloop_query, {
#               "id": index[0], "time": index[1], "jtypes": row["jtypes"]})
#     if (index[1] != curr_time):
#         curr_time = index[1]
#         print(curr_time)

curr_time = 50
for index, row in final_df.iterrows():
    for loop in row["connected_loops"]:
        run_query(
            create_connections_query,
            {"id1": index[0], "time1": index[1], "id2": loop, "time2": index[1]},
        )
    if index[1] != curr_time:
        curr_time = index[1]
        print(curr_time)
