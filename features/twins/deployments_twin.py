from datetime import datetime

from py2neo import Node, Relationship

from features.data_adapters.github_data_adapter import GitHubDataAdapter
from utils.constants.graph_nodes import GraphNodes
from utils.constants.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class DeploymentsTwin:

    @staticmethod
    def construct_from_json(json_url):
        query = f'''
CALL apoc.load.json('{json_url}') YIELD value AS deployment

WITH deployment
ORDER BY deployment.published_at ASC
WITH collect(deployment) AS deployments

UNWIND range(0, size(deployments) - 1) AS i
WITH 
deployments[i] AS deploy_data,
CASE WHEN i > 0 THEN deployments[i - 1].id ELSE null END AS previous_deploy_id

MERGE (added_deploy:{GraphNodes.DEPLOYMENT} {{id: deploy_data.id}})
ON CREATE SET
added_deploy.tag_name = deploy_data.tag_name,
added_deploy.latest_included_commit = deploy_data.latest_included_commit,
added_deploy.published_at = deploy_data.published_at,
added_deploy.release_url = deploy_data.release_url,
added_deploy.commit_url = deploy_data.commit_url

WITH added_deploy, previous_deploy_id, deploy_data.latest_included_commit AS latest_commit_hash
OPTIONAL MATCH (prev:{GraphNodes.DEPLOYMENT} {{id: previous_deploy_id}})
FOREACH (i in CASE WHEN prev IS NOT NULL THEN [1] ELSE [] END |
    MERGE (prev)-[:{GraphRelationships.SUCCEEDED_BY}]->(added_deploy)
)

WITH added_deploy as deployment, latest_commit_hash
OPTIONAL MATCH (latestCommit:Commit {{hash: latest_commit_hash}})-[:PARENT*]->(parentCommit:Commit)
WHERE NOT EXISTS(()-[:INITIAL_DEPLOY]->(parentCommit))

WITH deployment, latestCommit, collect(DISTINCT parentCommit) AS parent_commits
FOREACH (commit IN parent_commits |
    MERGE (deployment)-[:INITIAL_DEPLOY]->(commit)
)

WITH deployment, latestCommit
WHERE latestCommit IS NOT NULL
MERGE (deployment)-[:INITIAL_DEPLOY]->(latestCommit)

RETURN 1
'''
        Neo4j.get_graph().run(query)
