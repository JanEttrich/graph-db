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

def compute_box_corners(p1, p2):
    """Compute 3d box corners based on diagonal vector

    Args:
        p1 (point): point 1 of diagonal
        p2 (point): point 2 of diagonal
    """
    pass

def sort_points_by_distance(points, to, asc: True):
    """Return sorted list of points based on their euclidian distance
    to the point 'to'. Default order is ascending.

    Args:
        points (list): list of points to sort
        to (point): used for distance computation
        asc (bool): order of sorting
    """
    pass

def fit_box_to_loop(loop_gid):
    """Fit bounding box to specified loop. Takes the extremes of the
    loop-nodes to generate the bounding box.

    Args:
        loop_gid: global loop id
    
    Returns:
        Corners of the bounding box.
    """    
    return 