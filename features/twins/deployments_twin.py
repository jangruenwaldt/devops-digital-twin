from datetime import datetime

from py2neo import Node, Relationship

from features.github.github import GitHub
from utils.graph.graph_nodes import GraphNodes
from utils.graph.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class DeploymentsTwin:
    @staticmethod
    def construct(github_url, enable_cache=True, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        gh = GitHub(github_url)
        releases = gh.fetch_releases(enable_cache=enable_cache)
        graph = Neo4j.get_graph()
        Neo4j.remove_releases()

        previous_deployment = None
        releases_sorted = sorted(releases, key=lambda r: datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'))
        for release in releases_sorted:
            tag_name = release['tag_name']

            latest_commit_hash = gh.get_latest_commit_hash_in_release(tag_name)
            release_url = github_url + f'/releases/tag/{tag_name}'
            commit_url = github_url + f'/commit/{latest_commit_hash}'
            publish_date = release['published_at']
            deployment_node = Node(GraphNodes.DEPLOYMENT, id=release['id'], tag_name=tag_name,
                                   published_at=datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%SZ').replace(
                                       microsecond=0).isoformat(),
                                   release_url=release_url,
                                   commit_url=commit_url,
                                   latest_included_commit=latest_commit_hash)
            graph.create(deployment_node)
            if enable_logs:
                print(f'Added deployment {deployment_node}')

            if previous_deployment is not None:
                relation = Relationship(previous_deployment, GraphRelationships.SUCCEEDED_BY, deployment_node)
                graph.create(relation)

            commit_node = graph.nodes.match(GraphNodes.COMMIT, hash=latest_commit_hash).first()
            if commit_node is not None:
                relation = Relationship(deployment_node, GraphRelationships.LATEST_INCLUDED_COMMIT, commit_node)
                graph.create(relation)
                DeploymentsTwin.add_initial_deploy_relationship(latest_commit_hash)
            else:
                graph.run(f"""MATCH (n {{tag_name: '{tag_name}'}})
                    SET n.note = 'No relationship to commit added as the commit that was deployed is not part of the 
                    main branch anymore.'
                    """)

            previous_deployment = deployment_node

    @staticmethod
    def add_initial_deploy_relationship(latest_commit_hash):
        query = f"""
        MATCH (deployment:Deployment {{latest_included_commit: '{latest_commit_hash}'}}), 
        (latestCommit:Commit {{hash: '{latest_commit_hash}'}})
        
        MATCH (latestCommit)-[:PARENT*]->(parentCommit:Commit)
        WHERE NOT EXISTS(()-[:INITIAL_DEPLOY]->(parentCommit))
        
        WITH deployment, collect(DISTINCT parentCommit) AS parent_commits
        FOREACH (commit IN parent_commits |
            CREATE (deployment)-[:INITIAL_DEPLOY]->(commit)
        )
        """
        return Neo4j.get_graph().run(query).evaluate()
