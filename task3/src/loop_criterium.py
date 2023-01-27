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


## step 1: find loops with nodes closest to origin of (6187.5, 6187.5, 6187.5)
origin = np.array([6187.5, 6187.5, 6187.5])
displacement = lambda x: np.array([x, x, x])
amount = 500

nearest_nodes: pd.DataFrame = get_nodes_in_box(
    origin - displacement(amount), origin + displacement(amount), 50
)

points = convert_df_to_points(nearest_nodes)
_, sorted_indexes = sort_by_distance(points, origin)
nearest_nodes = nearest_nodes.reindex()  # df now sorted by distance (ascending)

loop_candidates = []
for _, row in nearest_nodes.iterrows():
    for e in row["loop_candidates"]:
        loop_candidates.append(e)

max_lifetime_loops = list(get_max_lifetime_loops()[
    "gid"
])  # we only want loops with max lifetime
# line below does not work if above is not list, because of pandas indexing
nearest_loops = [c for c in loop_candidates if c in max_lifetime_loops]
nearest_loops = [*set(nearest_loops)]  # remove duplicates


## step 2: compute bounding boxes for every time step for first x loops in list
num_max_loops = 10
nearest_loops = nearest_loops[:num_max_loops]
print("nearest loops:", nearest_loops)
step_bboxes = defaultdict(list)

print("starting time step bounding boxes computation")
ctime = time.time()
for ts in range(50, 10000, 50):
    for loop_gid in nearest_loops:
        p1, p2, _ = fit_box_to_loop(loop_gid, ts)
        step_bboxes[loop_gid].append([tuple(p1), tuple(p2)])

    print(ts, ": timestep computed after", round(time.time() - ctime), "seconds.")

print("Terminated time step bounding boxes computation.\n")
print(step_bboxes)
with open("../output/loop_criterium_res.txt", "w") as f:
    f.write(json.dumps(step_bboxes))
