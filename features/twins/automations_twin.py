from utils.neo4j import Neo4j


class AutomationsTwin:

    @staticmethod
    def construct_from_json(automations_json_url, automation_runs_json_url):
        print(f'Constructing AutomationsTwin from {automations_json_url} and {automation_runs_json_url}')
        AutomationsTwin._add_indices()

        AutomationsTwin._add_automation_nodes(automations_json_url)
        AutomationsTwin._add_automation_history(automation_runs_json_url)

    @staticmethod
    def _add_indices():
        Neo4j.get_graph().run('CREATE INDEX automation_id IF NOT EXISTS FOR (c:Automation) ON (c.id)')

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

    @staticmethod
    def _add_automation_history(json_url):
        add_automation_run_nodes_query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('{json_url}') YIELD value RETURN value as run_data
",
"
    MERGE (r:AutomationRun {{id: run_data.id}})
    SET
        r.name = run_data.name,
        r.head_branch = run_data.head_branch,
        r.head_sha = run_data.head_sha,
        r.path = run_data.path,
        r.run_number = run_data.run_number,
        r.event = run_data.event,
        r.status = run_data.status,
        r.conclusion = run_data.conclusion,
        r.automation_id = run_data.workflow_id,
        r.url = run_data.url,
        r.run_started_at = run_data.run_started_at,
        r.updated_at = run_data.updated_at,
        r.started_by = run_data.started_by,
        r.run_attempt = run_data.run_attempt
        
    WITH r
        OPTIONAL MATCH (c:Commit {{hash: coalesce(r.head_sha, 'none')}})
        FOREACH (ignoreMe in CASE WHEN c IS NOT NULL THEN [1] ELSE [] END |
          MERGE (r)-[:RAN_ON]->(c))
    
    WITH r
        OPTIONAL MATCH (next:AutomationRun {{run_number: r.run_number + 1, automation_id: r.automation_id}})
        FOREACH (ignoreMe in CASE WHEN next IS NOT NULL THEN [1] ELSE [] END |
          MERGE (next)-[:PREVIOUS_RUN]->(r))
    
    WITH r
      WHERE r.event = 'workflow_dispatch'
    MERGE (a:Author {{id: r.started_by}})
    MERGE (a)-[:STARTED_AUTOMATION]->(r)
",
{{batchSize: 1000, parallel: true}})
YIELD batches, total
RETURN batches, total
'''
        Neo4j.run_query(add_automation_run_nodes_query)

        add_latest_run_relationship = f'''
CALL apoc.periodic.iterate(
"
    MATCH (a:Automation)
    RETURN a
",
"
MATCH (r:AutomationRun {{automation_id: a.id}})

WITH r, a
    ORDER BY toInteger(r.run_number) DESC
    LIMIT 1

MERGE (a)-[:LATEST_RUN]->(r)
",
{{batchSize: 1, parallel: true}})
YIELD batches, total
RETURN batches, total
'''
        Neo4j.run_query(add_latest_run_relationship)
