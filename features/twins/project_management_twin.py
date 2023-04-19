from py2neo import Node, Relationship

from features.github.github import GitHub
from utils.graph.graph_nodes import GraphNodes
from utils.graph.graph_relationships import GraphRelationships
from utils.neo4j import Neo4j


class ProjectManagementTwin:
    @staticmethod
    def _add_issue_labels(enable_logs, issue, issue_node):
        graph = Neo4j.get_graph()

        for label in issue['labels']:
            existing_label = graph.nodes.match(GraphNodes.ISSUE_LABEL, id=label['id']).first()
            if existing_label is None:
                node_to_add = Node(GraphNodes.ISSUE_LABEL,
                                   id=label['id'],
                                   url=label['url'],
                                   name=label['name'],
                                   color=label['color'],
                                   description=label['description'])
                graph.create(node_to_add)
                if enable_logs:
                    print(f'Added issue label {label["description"]}')
            else:
                if enable_logs:
                    print(f'Issue label {label["description"]} already found')

            issue_label_node = graph.nodes.match(GraphNodes.ISSUE_LABEL, id=label['id']).first()
            has_label_relationship = Relationship(issue_node, GraphRelationships.HAS_LABEL, issue_label_node)
            graph.create(has_label_relationship)
            if enable_logs:
                print(f'Added relationship from {issue_node} to {issue_label_node}')

    @staticmethod
    def construct(github_url, enable_cache=True, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']
        max_nodes = debug_options['max_nodes'] if 'max_nodes' in debug_options else None

        gh = GitHub(github_url)
        issues = gh.fetch_issues(enable_cache=enable_cache)
        graph = Neo4j.get_graph()
        Neo4j.remove_issues_and_labels()

        added_nodes = 0
        for issue in issues:
            added_nodes += 1
            if added_nodes > max_nodes:
                break

            issue_node = Node(GraphNodes.ISSUE,
                              url=issue['url'],
                              id=issue['id'],
                              title=issue['title'],
                              state=issue['state'],
                              locked=issue['locked'],
                              assignee=issue['assignee'],
                              milestone=issue['milestone'],
                              comments=issue['comments'],
                              created_at=issue['created_at'],
                              updated_at=issue['updated_at'],
                              closed_at=issue['closed_at'],
                              body=issue['body'])
            graph.create(issue_node)
            if enable_logs:
                print(f'Added issue {issue_node}')

            ProjectManagementTwin._add_issue_labels(enable_logs, issue, issue_node)
