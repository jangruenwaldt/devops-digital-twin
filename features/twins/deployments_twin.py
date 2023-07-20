from utils.neo4j import Neo4j


class DeploymentsTwin:

    @staticmethod
    def construct_from_json(path):
        print(f'Constructing DeploymentsTwin from {path}')
        DeploymentsTwin._add_indices()

        DeploymentsTwin._add_deployment_nodes(path)
        DeploymentsTwin._add_succeeds_relationship()
        DeploymentsTwin._add_initial_deploy_relationship()

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX commit_hash IF NOT EXISTS FOR (c:Commit) ON (c.hash)')
        Neo4j.get_graph().run('CREATE INDEX deployment_id '
                              'IF NOT EXISTS FOR (d:Deployment) ON (d.id)')

    @staticmethod
    def _add_initial_deploy_relationship():
        result2 = Neo4j.run_query('''
CALL apoc.periodic.iterate(
"
    MATCH (deployment:Deployment)
    OPTIONAL MATCH (latest_commit:Commit {hash: deployment.latest_included_commit})
    
    WITH deployment
    ORDER BY deployment.published_at
    WHERE latest_commit is not null
    
    RETURN deployment
",
"
    WITH deployment
    
    MATCH (latest_commit:Commit {hash: deployment.latest_included_commit})
    
    CALL apoc.path.subgraphAll(latest_commit, {
     relationshipFilter: 'PARENT>',
     labelFilter: '+Commit'
    })
    YIELD nodes AS all_commits_deployed_in_this_deployment
    
    UNWIND all_commits_deployed_in_this_deployment as commit
    
    WITH commit, deployment
    WHERE NOT EXISTS((:Deployment)-[:INITIAL_DEPLOY]->(commit))

    MERGE (deployment)-[:INITIAL_DEPLOY]->(commit)
",
{batchSize: 1, parallel: false})
YIELD batches, total
RETURN batches, total
''')
        print(result2)

    @staticmethod
    def _add_succeeds_relationship():
        query = '''
CALL apoc.periodic.iterate(
"
    MATCH (d:Deployment)
    WITH d
    ORDER BY d.published_at
    WITH COLLECT(d) AS deployments
    
    UNWIND range(1, size(deployments) - 1) AS i
    RETURN deployments[i] AS deployment,
    deployments[i - 1] AS previous_deployment
",
"
    WITH deployment, previous_deployment
    MERGE (deployment)-[:SUCCEEDS]->(previous_deployment)
",
  {batchSize: 1000, parallel: true}
)
YIELD batches, total
RETURN batches, total
'''
        result2 = Neo4j.run_query(query)
        print(result2)

    @staticmethod
    def _add_deployment_nodes(path):
        add_deployment_nodes_query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('file://{path}') YIELD value RETURN value
",
"
    WITH value AS deploy_data
    MERGE (added_deploy:Deployment {{id: deploy_data.id}})
    SET
    added_deploy.name = deploy_data.name,
    added_deploy.latest_included_commit = deploy_data.latest_included_commit,
    added_deploy.published_at = deploy_data.published_at,
    added_deploy.url = deploy_data.url,
    added_deploy.commit_url = deploy_data.commit_url
",
{{batchSize: 1000, parallel: true}})
YIELD batches, total
RETURN batches, total
'''
        result = Neo4j.run_query(add_deployment_nodes_query)
        print(result)
