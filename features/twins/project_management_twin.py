from utils.neo4j import Neo4j


class ProjectManagementTwin:

    @staticmethod
    def construct_from_json(path):
        print(f'Constructing ProjectManagementTwin from {path}')
        ProjectManagementTwin._add_indices()

        ProjectManagementTwin._add_issue_nodes(path)

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX issue_id IF NOT EXISTS FOR (c:Issue) ON (c.id)')
        Neo4j.get_graph().run('CREATE INDEX issue_label_id IF NOT EXISTS FOR (c:IssueLabel) ON (c.id)')

    @staticmethod
    def _add_issue_nodes(path):
        query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('file://{path}') YIELD value RETURN value as issue_data
",
"
    MERGE (i:Issue {{id: issue_data.id}})
    SET
    i.title = issue_data.title,
    i.state = issue_data.state,
    i.locked = issue_data.locked,
    i.comments = issue_data.comments,
    i.url = issue_data.url,
    i.created_at = issue_data.created_at,
    i.updated_at = issue_data.updated_at,
    i.closed_at = issue_data.closed_at,
    i.body = issue_data.body,
    i.created_by = issue_data.user.login,
    i.assignee = apoc.convert.toJson(issue_data.assignee),
    i.milestone = apoc.convert.toJson(issue_data.milestone),
    i.state_reason = issue_data.state_reason
    
    MERGE (author:Author {{id: issue_data.user.login}})
    MERGE (author)-[r:CREATED_ISSUE]->(i)
    SET
    r.date = issue_data.created_at
    
    WITH i, issue_data.labels AS labels
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
