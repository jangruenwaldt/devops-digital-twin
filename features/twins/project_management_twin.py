import json
from datetime import datetime

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
            label_id = label['id']
            if existing_label is None:
                node_to_add = Node(GraphNodes.ISSUE_LABEL,
                                   id=label_id,
                                   url=label['url'],
                                   name=label['name'],
                                   color=label['color'],
                                   description=label['description'])
                graph.create(node_to_add)
                if enable_logs:
                    print(f'Added issue label {label_id}')
            else:
                if enable_logs:
                    print(f'Issue label {label_id} was already added')

            label_node = graph.nodes.match(GraphNodes.ISSUE_LABEL, id=label['id']).first()
            has_label_relationship = Relationship(issue_node, GraphRelationships.HAS_LABEL, label_node)
            graph.create(has_label_relationship)
            if enable_logs:
                print(f'Added relationship from issue {issue_node.get("id")} to label {label_id}')

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
            if max_nodes is not None and added_nodes > max_nodes:
                break

            issue_node = Node(GraphNodes.ISSUE,
                              url=issue['url'],
                              id=issue['id'],
                              title=issue['title'],
                              state=issue['state'],
                              locked=issue['locked'],
                              user=json.dumps(issue['user']) if issue['user'] is not None else None,
                              assignee=json.dumps(issue['assignee']) if issue['assignee'] is not None else None,
                              milestone=json.dumps(issue['milestone']) if issue['milestone'] is not None else None,
                              comments=issue['comments'],
                              created_at=datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                                  microsecond=0).isoformat(),
                              updated_at=issue['updated_at'],
                              closed_at=datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                                  microsecond=0).isoformat() if issue['closed_at'] is not None else None,
                              body=issue['body'])
            graph.create(issue_node)
            if enable_logs:
                print(f'Added issue with id {issue["id"]}')

            ProjectManagementTwin._add_issue_labels(enable_logs, issue, issue_node)
