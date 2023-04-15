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

        previous_release = None
        for release in releases:
            tag_name = release['tag_name']

            latest_commit_hash = gh.get_latest_commit_hash_in_release(tag_name)
            release_url = github_url + f'/releases/tag/{tag_name}'
            commit_url = github_url + f'/commit/{latest_commit_hash}'
            publish_date = release['published_at']
            release_node = Node(GraphNodes.RELEASE, id=release['id'], tag_name=tag_name,
                                published_at=datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%SZ').replace(
                                    microsecond=0).isoformat(),
                                release_url=release_url,
                                commit_url=commit_url)
            graph.create(release_node)
            if enable_logs:
                print(f'Added release {release_node}')

            if previous_release is not None:
                # Note that previous release just means previously iterated, it factually is a higher release
                relation = Relationship(release_node, GraphRelationships.SUCCEEDED_BY, previous_release)
                graph.create(relation)

            commit_node = graph.nodes.match(GraphNodes.COMMIT, hash=latest_commit_hash).first()
            if commit_node is not None:
                relation = Relationship(release_node, GraphRelationships.LATEST_INCLUDED_COMMIT, commit_node)
                graph.create(relation)
            else:
                graph.run(f"""MATCH (n {{tag_name: '{tag_name}'}})
                    SET n.note = 'No relationship to commit added as the commit that was deployed is not part of the 
                    main branch anymore.'
                    """)

            previous_release = release_node
