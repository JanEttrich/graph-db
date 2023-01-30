from utility import *
import pandas as pd
from collections import defaultdict
import time
import json

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))


def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df


def generate_bb(points):
    """Generates a bounding box given a list of points"""
    return np.asarray([np.asarray(points).min(0), np.asarray(points).max(0)])


def union_bb(bounding_boxes):
    """Generates a bounding box given a list of points"""
    return np.asarray([np.asarray(points).min(0), np.asarray(points).max(0)])


# Junction types can be the numbers 1-7
junction_types = range(1, 8)

closest_junction_query = """MATCH (n: Node)-[]–(j: Junction{type:$type, time:$time})-[]-(m:Node) 
WITH j,n,m, point({x: n.x, y: n.y, z: n.z}) as p1, 
point({x: 6187.5, y: 6187.5, z: 6187.5}) as p2 
RETURN j,n,m ORDER BY point.distance(p1,p2) ASC LIMIT 1"""

start_time = time.time()
bounding_boxes = {}
union_nodes = []

for ts in range(50, 20000, 50):
    timestep_nodes = []
    for type in junction_types:
        params = {"type": type, "time": ts}
        result = run_query(closest_junction_query, params)
        first_node = result["n"].iloc[0]
        second_node = result["m"].iloc[0]
        for node in [first_node, second_node]:
            timestep_nodes.append(np.array([node["x"], node["y"], node["z"]]))

    ts_bb = generate_bb(timestep_nodes)
    bounding_boxes[str(time)] = ts_bb
    union_nodes.append(ts_bb[0])
    union_nodes.append(ts_bb[1])
    print(ts_bb)

    print(
        f"Bounding box for timestep {ts} calculated. Elapsed time: {round(time.time() - start_time)} seconds")

final_bb = generate_bb(union_nodes)
print(final_bb)
print(
    f"Final bounding box {ts} calculated. Elapsed time: {round(time.time() - start_time)} seconds")

with open("../output/all_junction_types_timesteps_res.json", "w") as f:
    f.write(json.dumps(bounding_boxes))

with open("../output/all_junction_types_final_res.json", "w") as f:
    f.write(json.dumps(final_bb))

print("Results saved!")