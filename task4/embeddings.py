import pandas as pd
from neo4j import GraphDatabase
from collections import Counter
from dbconfig import *
import json
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import time

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))


def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df


drop_graph_query = """CALL gds.graph.drop('eloops', false) YIELD graphName"""


def projection_query(time, limit): return f"""
CALL gds.graph.project.cypher(
  'eloops',
  'MATCH (n:EmLoop{{time:{time}}}) RETURN id(n) AS id, n.jtypes AS jtypes LIMIT {limit}',
  'MATCH (n)-[r:CONNECTION]-(m:EmLoop{{time:{time}}}) RETURN id(n) AS source, id(m) AS target',
  {{
  validateRelationships: false
  }})
YIELD
  graphName AS graph, nodeQuery, nodeCount AS nodes, relationshipQuery, relationshipCount AS rels
"""


fastRP_query = """
CALL gds.fastRP.stream(
'eloops',
{
embeddingDimension:256,
iterationWeights: [2]
}
)
YIELD
nodeId as loop,
embedding
"""


def get_jtypes_query(ids): return f"""
  MATCH (e:EmLoop)
  WHERE id(e) IN {ids}
  RETURN id(e) AS loop, e.jtypes AS jtypes
"""


def generateEmbedding(timestep, show_jtypes, strategy, limit):
    
    # Ensure that old projected graph is removed
    _ = run_query(drop_graph_query, {})

    # Project the graph
    _ = run_query(projection_query(timestep, limit), {})

    # Generate embeddings
    result = run_query(fastRP_query, {})
    jtypes = run_query(get_jtypes_query(list(result["loop"])), {})
    occurences = jtypes.explode('jtypes')['jtypes'].value_counts()
    occurence_dict = dict(occurences)
    embedding_arr = np.asarray(list(result.embedding))
    loop_dict = {key: pd.DataFrame(columns=["loop","x", "y"]) for key in occurence_dict.keys()}

    X_embedded = TSNE(
        n_components=2, random_state=6).fit_transform(embedding_arr)

    loop = result.loop
    tsne_df = pd.DataFrame(data={
        "loop": loop,
        "x": [value[0] for value in X_embedded],
        "y": [value[1] for value in X_embedded]
    })

    for _, row in tsne_df.iterrows():
        loop_id = row["loop"]
        embedding_row = tsne_df[tsne_df["loop"] == loop_id]
        loop_jtypes_list = list(jtypes[jtypes["loop"] == loop_id]["jtypes"])[0]
        count = Counter(loop_jtypes_list)
        most_common = count.most_common()
        max_count = most_common[0][1]
        most_common_list = [item for item, count in most_common if count == max_count]
        filtered_occurences = {key: value for key, value in occurence_dict.items() if key in most_common_list}

        if (strategy == "md"):
          assigned_jtype = max(filtered_occurences, key=filtered_occurences.get)
        else:
          assigned_jtype = min(filtered_occurences, key=filtered_occurences.get)

        loop_dict[assigned_jtype] = pd.concat([loop_dict[assigned_jtype], embedding_row])

    fig, ax = plt.subplots()
    for jtype, df in loop_dict.items():
      if jtype in show_jtypes:
        ax.scatter(df["x"], df["y"], label=jtype, s=5)

    ax.legend(loc='upper right',title="Junction\nType")
    plt.savefig(f"out/{round(time.time())}.png")
    plt.close()
