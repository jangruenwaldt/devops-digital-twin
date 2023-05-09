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
        add_deployed_in_attribute = f'''
CALL apoc.periodic.iterate(
"
    MATCH (deployment:{GraphNodes.DEPLOYMENT})
    OPTIONAL MATCH (latest_commit:{GraphNodes.COMMIT} {{hash: deployment.latest_included_commit}})

    WITH deployment
     ORDER BY deployment.published_at
     WHERE latest_commit is not null
    
    RETURN deployment
",
"
    WITH deployment
    
    MATCH (latest_commit:{GraphNodes.COMMIT} {{hash: deployment.latest_included_commit}})
    
    CALL apoc.path.subgraphAll(latest_commit, {{
     relationshipFilter: 'PARENT>',
     labelFilter: '+Commit'
    }})
    YIELD nodes
    
    WITH nodes, deployment
    
    FOREACH (node in nodes |
    SET node.deployed_in_version = CASE
     WHEN node.deployed_in_version IS NULL THEN [deployment.tag_name]
     ELSE node.deployed_in_version + deployment.tag_name
    END )
",
  {{batchSize: 50, parallel: false}}
)
YIELD batches, total
RETURN batches, total
'''
        result = Neo4j.run_query(add_deployed_in_attribute)
        print(result)

        add_initial_deploy_relationships = f'''
CALL apoc.periodic.iterate(
"
 MATCH (deployment:{GraphNodes.DEPLOYMENT})
 OPTIONAL MATCH (latest_commit:{GraphNodes.COMMIT} {{hash: deployment.latest_included_commit}})

 WITH deployment
   ORDER BY deployment.published_at
   WHERE latest_commit is not null

 RETURN deployment
",
"
   WITH deployment

   MATCH (n:{GraphNodes.COMMIT})
   WHERE deployment.tag_name IN n.deployed_in_version
   AND NOT (:{GraphNodes.DEPLOYMENT})-[:{GraphRelationships.INITIAL_DEPLOY}]->(n)

   MERGE (deployment)-[:{GraphRelationships.INITIAL_DEPLOY}]->(n)
",
{{batchSize: 1, parallel: false}})
YIELD batches, total
RETURN batches, total
'''
        result2 = Neo4j.run_query(add_initial_deploy_relationships)
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
    
    UNWIND range(1, size(deployments) - 1) AS i
    WITH deployments[i] AS deployment,
    deployments[i - 1] AS previous_deployment
    RETURN deployment, previous_deployment
",
"WITH deployment, previous_deployment
  MERGE (previous_deployment)-[:{GraphRelationships.SUCCEEDED_BY}]->(deployment)
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
