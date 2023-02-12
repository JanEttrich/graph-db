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

projection_query = """
MATCH (l: ELoop{time: 50})
WITH collect(l) AS loops
CALL gds.graph.project(
  'eloops',
  'loops',
  {
    CONNECTION: {
      orientation: 'UNDIRECTED',
    }
  },
  { nodeProperties: ['jtypes'] }
)
"""

fastRP_query = """
CALL gds.fastRP.stream(
  graphName: eloops,
  configuration: {
    embeddingDimension: 256,
    iterationWeights: 2,
  }
) YIELD
  nodeId: Integer,
  embedding: List of Float
"""
params = {}
result = run_query(projection_query, params)
print(result)
