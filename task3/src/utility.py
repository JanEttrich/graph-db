import numpy as np
import pandas as pd
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from dbconfig import *

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))

# TODO maybe add option to fit box to loop with densest points in coordinate space
# TODO statistics on coordinate distribution, e.g. boxplots for x,y,z, respectively


def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df


def get_max_lifetime_loops():
    """Returns dataframe filled with loop global ids
    for which the lifetime is 9900 (maximum lifetime).
    Lifetime starts at 50 and ends at 9950
    """
    query = """
    match (l:Loop) with l.global_id as gid,
    min(l.time) as start_time,
    max(l.time) - min(l.time) as lifetime
    where lifetime = 9900
    return gid"""

    res = run_query(query, {})
    return res


def compute_box_constraints(p1, p2):
    """Compute 3d box constraints based on
    diagonal vector from p1 to p2.

    Args:
        p1 (point): point 1 of diagonal
        p2 (point): point 2 of diagonal

    Returns:
        constraints in order min_x, max_x, min_y, etc.
    """
    min_x = min(p1[0], p2[0])
    max_x = max(p1[0], p2[0])
    min_y = min(p1[1], p2[1])
    max_y = max(p1[1], p2[1])
    min_z = min(p1[2], p2[2])
    max_z = max(p1[2], p2[2])

    contraints = [min_x, max_x, min_y, max_y, min_z, max_z]
    return contraints


def check_same_box(p1, p2, p3, p4):
    """Check whether box defined by diagonal of p1, p2 and p3, p4 is the same.

    Args:
        p1 (point): point 1 of diagonal 1
        p2 (point): point 2 of diagonal 1
        p3 (point): point 1 of diagonal 2
        p4 (point): point 2 of diagonal 2
    """
    return compute_box_constraints(p1, p2) == compute_box_constraints(p3, p4)


def sort_by_distance(points, to, asc=True):
    """Return sorted list of points based on their euclidian distance
    to the point 'to'. Default order is ascending.

    Args:
        points (list): list of points to sort
        to (point): used for distance computation
        asc (bool): order of sorting
    """
    distances = [np.linalg.norm(to - point) for point in points]
    sorted_index = np.argsort(distances)
    if not asc:
        sorted_index = sorted_index[::-1]

    return [points[i] for i in sorted_index], sorted_index


def get_nodes_in_box(p1, p2, timestamp):
    """Return all nodes with coordinates in the box defined by p1 and p2.

    Args:
        p1 (point): point 1 in diagonal
        p2 (point): point 2 in diagonal
        timestamp (int): timestamp in database

    Returns:
        Dataframe with node ids, coordinates and corresponding loop candidates
    """
    constraints = compute_box_constraints(p1, p2)

    query_nodes = f"""
    match (n:Node{{time:{timestamp}}})--(l:Loop)
    where {constraints[0]} <= n.x <= {constraints[1]}
    and {constraints[2]} <= n.y <= {constraints[3]}
    and {constraints[4]} <= n.z <= {constraints[5]}
    return n.time as timestamp,
    n.id as node_id,
    n.x as x,
    n.y as y,
    n.z as z,
    collect(distinct l.global_id) as loop_candidates
    """

    res = run_query(query_nodes, {})
    return res


def convert_df_to_points(df: pd.DataFrame):
    points = []
    for _, row in df[["x", "y", "z"]].iterrows():
        x, y, z = row
        points.append(np.array([x, y, z]))

    return points


# TODO fit_box_to_query(query) --> fits box to nodes returned by this query


def fit_box_to_loop(loop_gid, timestamp):
    """Fit bounding box to specified loop. Takes the extremes of the
    loop-nodes to generate the bounding box.

    Args:
        loop_gid: global loop id
        timestamp (int): timestamp in database

    Returns:
        Diagonal points and constraints of the bounding box
    """

    query_loop_nodes = f"""
    match
    (n:Node{{time:{timestamp}}})--(l:Loop{{global_id:{loop_gid}, time:{timestamp}}})
    return n.time as timestamp,
    n.id as node_id,
    n.x as x,
    n.y as y,
    n.z as z
    """

    res = run_query(query_loop_nodes, {})
    if "x" in res.columns:
        min_x, min_y, min_z = res[["x", "y", "z"]].min()
        max_x, max_y, max_z = res[["x", "y", "z"]].max()

        p1 = np.array([min_x, min_y, min_z])
        p2 = np.array([max_x, max_y, max_z])
    else:
        print(
            f"Could not compute bounding box for loop {loop_gid} at time {timestamp} because dataframe columns are {res.columns}"
        )
        return None, None, None  # same number of values to unpack

    constraints = [min_x, max_x, min_y, max_y, min_z, max_z]
    assert compute_box_constraints(p1, p2) == constraints

    return p1, p2, constraints


def find_loops_in_box(p1, p2, timestamp):
    """Find all loops in bounding box defined by p1 and p2.
    Based on all nodes in bounding box,

    Args:
        p1 (point): point 1 of diagonal
        p2 (point): point 2 of diagonal

    Returns:
        contained_loops, loop_candidates
    """
    # first: return all nodes and loop candidates
    # for all loop candidates, query nodes and check if all nodes are contained in box
    # only return loop ids for which the entirety of nodes is in the bounding box
    node_df = get_nodes_in_box(p1, p2, timestamp)
    loop_candidates = []
    for row in node_df["loop_candidates"]:
        for e in row:
            loop_candidates.append(e)

    node_set = set(node_df["node_id"])
    loop_candidates = [*set(loop_candidates)]

    query = f"""
    match (n:Node)--(l:Loop{{time:{timestamp}}})
    where l.global_id in {loop_candidates}
    return n.time as timestamp,
    n.id as node_id,
    l.global_id as gid
    """
    loops_df = run_query(query, {})

    complete_loops_in_box = []
    for e in loop_candidates:
        if set(loops_df[loops_df["gid"] == e]["node_id"]).issubset(node_set):
            complete_loops_in_box.append(e)

    return complete_loops_in_box, loop_candidates


def plot_points(points, f_name):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    for x, y, z in points:
        ax.scatter(x, y, z, c="b", alpha=0.8)

    fig.savefig(f"../figures/{f_name}.pdf", format="pdf")


# NOTE: functions below maybe not necessary


def plot_bounding_box(p1, p2):
    """Plot bounding box in 3d space.
    Maybe add option to animate loops through time.

    Args:
        p1 (point): point 1 in diagonal
        p2 (point): point 2 in diagonal
    """
    # TODO implement
    pass
