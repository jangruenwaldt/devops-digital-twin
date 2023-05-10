from utils.neo4j import Neo4j


class ProjectManagementTwin:

    @staticmethod
    def construct_from_json(json_url):
        print(f'Constructing ProjectManagementTwin from {json_url}')
        ProjectManagementTwin._add_indices()

        ProjectManagementTwin._add_issue_nodes(json_url)

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX issue_id IF NOT EXISTS FOR (c:Issue) ON (c.id)')
        Neo4j.get_graph().run('CREATE INDEX issue_label_id IF NOT EXISTS FOR (c:IssueLabel) ON (c.id)')

    @staticmethod
    def _add_issue_nodes(json_url):
        query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('{json_url}') YIELD value RETURN value
",
"
    MERGE (i:Issue {{id: value.id}})
    SET
    i.title = value.title,
    i.state = value.state,
    i.locked = value.locked,
    i.comments = value.comments,
    i.url = value.url,
    i.created_at = value.created_at,
    i.updated_at = value.updated_at,
    i.closed_at = value.closed_at,
    i.body = value.body,
    i.user = apoc.convert.toJson(value.user),
    i.assignee = apoc.convert.toJson(value.assignee),
    i.milestone = apoc.convert.toJson(value.milestone)
    
    WITH i, value.labels AS labels
    UNWIND labels AS label
    
    MERGE (l:IssueLabel {{id: label.id}})
    SET 
    l.name = label.name,
    l.color = label.color,
    l.description = label.description,
    l.url = label.url
    MERGE (i)-[:HAS_LABEL]->(l)
    RETURN 1
",
{{batchSize: 500, parallel: false}})
YIELD batch
'''
        result = Neo4j.run_query(query)
        print(result)
