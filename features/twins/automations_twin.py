from utils.neo4j import Neo4j


class AutomationsTwin:

    @staticmethod
    def construct_from_json(json_url):
        print(f'Constructing AutomationsTwin from {json_url}')
        AutomationsTwin._add_indices()

        AutomationsTwin._add_automation_nodes(json_url)

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX workflow_id IF NOT EXISTS FOR (c:Workflow) ON (c.id)')

    @staticmethod
    def _add_automation_nodes(json_url):
        query = f'''
    CALL apoc.load.json('{json_url}') YIELD value as automation_data
    
    WITH automation_data
    MERGE (a:Automation {{id: automation_data.id}})
    SET
        a.name = automation_data.name,
        a.path = automation_data.path,
        a.state = automation_data.state,
        a.created_at = automation_data.created_at,
        a.updated_at = automation_data.updated_at,
        a.url = automation_data.url
    RETURN 1
'''
        result = Neo4j.run_query(query)
        print(result)
