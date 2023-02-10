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
create_connections_query = (
    lambda time, id1, connections: f"""
MATCH (l1:ELoop{{time: {time}, id:{id1}}}), (l2:ELoop)
WHERE l2.time=50 AND l2.id IN {connections}
MERGE (l1)-[:CONNECTION]-(l2)"""
)

final_df = pd.read_csv("out/optimized_dataframe.csv")
final_df.set_index(["id", "time"], inplace=True)
final_df["jtypes"] = [x.strip("[]").split(",") for x in final_df["jtypes"]]
final_df["jtypes"] = [[int(e) for e in l if e != ""] for l in final_df["jtypes"]]
final_df["connected_loops"] = [
    x.strip("[]").split(", ") for x in final_df["connected_loops"]
]
final_df["connected_loops"] = [
    [int(e) for e in l if e != ""] for l in final_df["connected_loops"]
]

curr_time = 50
for index, row in final_df.iterrows():
    run_query(create_eloop_query, {
              "id": index[0], "time": index[1], "jtypes": row["jtypes"]})
    if (index[1] != curr_time):
        curr_time = index[1]
        print(curr_time)

# # sort df such that for each time step, longest list of connected loops is first
# final_df.reset_index(inplace=True)
# final_df["len"] = final_df["connected_loops"].apply(lambda x: len(x))
# final_df = final_df.sort_values(by=["time","len"], ascending=[True,False])
# final_df.drop(labels="len", axis=1, inplace=True)
# final_df.set_index(["id", "time"], inplace=True)
#
# # optimize dataframe adjacency matrix
# for row in final_df.itertuples():
#     loop_from = row.Index[0]
#     t = row.Index[1]
#     for loop_to in row.connected_loops:
#         final_df["connected_loops"][loop_to, t].remove(loop_from)
#
# # eliminate all rows with empty connected loops list
# final_df = final_df[final_df["connected_loops"].apply(lambda x: len(x) != 0)]
# final_df.to_csv("out/optimized_dataframe.csv")

curr_time = 50
for row in final_df.itertuples():
    q = create_connections_query(
        row.Index[1], row.Index[0], [int(x) for x in row.connected_loops]
    )
    run_query(q, {})
    if row.Index[1] != curr_time:
        curr_time = row.Index[1]
        print(curr_time)
