from utils.constants.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class GitTwin:

    @staticmethod
    def construct_from_json(json_url):
        query = f'''
CALL apoc.load.json({json_url}) YIELD value

MERGE (c:Commit {{hash: value.hash}})
ON CREATE SET
c.message = value.message,
c.date = value.date,
c.branch = value.branch,
c.url = value.url

FOREACH (parentHash IN value.parents |
  MERGE (p:Commit {{hash: parentHash}})
  MERGE (c)-[:{GraphRelationships.PARENT}]->(p)
)
'''
        Neo4j.get_graph().run(query)
