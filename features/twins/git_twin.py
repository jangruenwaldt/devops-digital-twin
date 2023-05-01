from utils.constants.graph_nodes import GraphNodes
from utils.constants.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class GitTwin:

    @staticmethod
    def construct_from_json(json_url):
        query = f'''
CALL apoc.load.json('{json_url}') YIELD value

MERGE (c:{GraphNodes.COMMIT} {{hash: value.hash}})
ON CREATE SET
c.message = value.message,
c.date = value.date,
c.branch = value.branch,
c.url = value.url

FOREACH (parentHash IN value.parents |
  MERGE (p:{GraphNodes.COMMIT} {{hash: parentHash}})
  MERGE (c)-[:{GraphRelationships.PARENT}]->(p)
)
RETURN 1
'''
        Neo4j.get_graph().run(query)
