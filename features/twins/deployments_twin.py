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
        DeploymentsTwin._add_indices()

        DeploymentsTwin._add_deployment_nodes(json_url)
        DeploymentsTwin._add_succeeded_by_relationship()
        DeploymentsTwin._add_initial_deploy_relationship()

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX commit_hash IF NOT EXISTS FOR (c:Commit) ON (c.hash)')
        Neo4j.get_graph().run('CREATE INDEX deployment_id '
                              'IF NOT EXISTS FOR (d:Deployment) ON (d.id)')

    @staticmethod
    def _add_initial_deploy_relationship():
        add_relationship_only_to_referenced_nodes = f'''
MATCH (deployment:{GraphNodes.DEPLOYMENT})
OPTIONAL MATCH (latest_commit:{GraphNodes.COMMIT} {{hash: deployment.latest_included_commit}})
SET latest_commit.deployment_id = deployment.id
'''
        result = Neo4j.run_query(add_relationship_only_to_referenced_nodes)
        print(result)

        add_relationship_to_all_nodes = '''
CALL apoc.periodic.iterate(
"
    MATCH (deploy_commit:Commit)
    WHERE deploy_commit.deployment_id IS NOT NULL
    
    MATCH (deploy_commit)-[:PARENT]->(search_start)
    MATCH (deployment_node:Deployment {id: deploy_commit.deployment_id})
    RETURN search_start, deploy_commit, deployment_node
",
"    
    MATCH (search_start)-[:PARENT*]->(c:Commit)
    WHERE c.deployment_id IS NULL
    
    MERGE (deployment_node)-[:INITIAL_DEPLOY]->(c)
)
",
  {{batchSize: 50, parallel: true}}
)
YIELD batches, total
RETURN batches, total
'''
        result2 = Neo4j.run_query(add_relationship_to_all_nodes)
        print(result2)

    @staticmethod
    def _add_succeeded_by_relationship():
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
        result2 = Neo4j.run_query(add_succeeded_by_relationship_query)
        print(result2)

    @staticmethod
    def _add_deployment_nodes(json_url):
        add_deployment_nodes_query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('{json_url}') YIELD value RETURN value
",
"
    WITH value AS deploy_data
    MERGE (added_deploy:{GraphNodes.DEPLOYMENT} {{id: deploy_data.id}})
    SET
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
        result = Neo4j.run_query(add_deployment_nodes_query)
        print(result)
