import pandas as pd
from neo4j import GraphDatabase
from dbconfig import *
import json

uri = "bolt://localhost:7689"
driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query, params):
    with driver.session() as session:
        result = session.run(query, params)
        df = pd.DataFrame(result.data())
    return df

drop_graph_query = """CALL gds.graph.drop('eloops', false) YIELD graphName"""

projection_query = lambda time, limit: f"""
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

get_jtypes_query = lambda ids: f"""
  MATCH (e:EmLoop)
  WHERE id(e) IN {ids}
  RETURN id(e), e.jtypes
"""

def generateEmbedding(time, jtypes, strategy, limit):
  # Ensure that old projected graph is removed
  _ = run_query(drop_graph_query, {})

  # Project the graph
  _ = run_query(projection_query(time, limit), {})

  # Generate embeddings
  result = run_query(fastRP_query, {})
  jtypes = run_query(get_jtypes_query(list(result["loop"])), {})
  print(result)
  print(jtypes)   


generateEmbedding(300, [], [], 50)