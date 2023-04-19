from py2neo import Node

from features.github.github import GitHub
from utils.graph.graph_nodes import GraphNodes
from utils.neo4j import Neo4j


class ProjectManagementTwin:
    @staticmethod
    def construct(github_url, enable_cache=True, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        gh = GitHub(github_url)
        issues = gh.fetch_issues(enable_cache=enable_cache)
        graph = Neo4j.get_graph()
        Neo4j.remove_issues_and_labels()

        for issue in issues:
            issue_node = Node(GraphNodes.ISSUE_LABEL)
            graph.create(issue_node)
            if enable_logs:
                print(f'Added issue {issue_node}')
