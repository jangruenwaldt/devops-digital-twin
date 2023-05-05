from datetime import datetime

from py2neo import Node, Relationship

from features.data_adapters.github_data_adapter import GitHubDataAdapter
from utils.constants.graph_nodes import GraphNodes
from utils.constants.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class DeploymentsTwin:

    @staticmethod
    def construct_from_json(json_url):
        print(f'Constructing DeploymentsTwin from {json_url}')
        Neo4j.get_graph().run('CREATE INDEX commit_hash IF NOT EXISTS FOR (c:Commit) ON (c.hash)')
        Neo4j.get_graph().run('CREATE INDEX deployment_id '
                              'IF NOT EXISTS FOR (d:Deployment) ON (d.id)')

        add_deployment_nodes_query = f'''
CALL apoc.periodic.iterate(
"
CALL apoc.load.json('{json_url}') YIELD value RETURN value
",
"
WITH value AS deploy_data
 MERGE (added_deploy:{GraphNodes.DEPLOYMENT} {{id: deploy_data.id}})
 ON CREATE SET
   added_deploy.tag_name = deploy_data.tag_name,
   added_deploy.latest_included_commit = deploy_data.latest_included_commit,
   added_deploy.published_at = deploy_data.published_at,
   added_deploy.release_url = deploy_data.release_url,
   added_deploy.commit_url = deploy_data.commit_url
",
{{batchSize: 1000, parallel: true}})
YIELD batches, total
RETURN batches, total
'''
        result = Neo4j.run_large_query(add_deployment_nodes_query)
        print(result)

        add_succeeded_by_relationship_query = f'''
CALL apoc.periodic.iterate(
  "
    MATCH (d:{GraphNodes.DEPLOYMENT})
    WITH d
    ORDER BY d.published_at
    WITH COLLECT(d) AS deployments
    
    UNWIND range(1, size(deployments) - 2) AS i
    WITH deployments[i].id AS deployment_id,
    deployments[i - 1].id AS previous_deployment_id
    RETURN deployment_id, previous_deployment_id
  ",
  "
  MATCH (d1:{GraphNodes.DEPLOYMENT} {{id: previous_deployment_id}}),
  (d2:{GraphNodes.DEPLOYMENT} {{id: deployment_id}})
  MERGE (d1)-[:{GraphRelationships.SUCCEEDED_BY}]->(d2)
  ",
  {{batchSize: 1000, parallel: true}}
)
YIELD batches, total
RETURN batches, total
'''
        result2 = Neo4j.run_large_query(add_succeeded_by_relationship_query)
        print(result2)
