from utils.config import Config
from utils.neo4j import Neo4j


class TwinMetaDataManager:

    @staticmethod
    def add_metadata():
        print(f'Adding meta data to twin')

        TwinMetaDataManager._add_commits_links()
        TwinMetaDataManager._add_meta_data_node()

    @staticmethod
    def _add_commits_links():
        query = f'''
        MATCH (c:Commit)
        
        WITH c
        LIMIT 1
        
        // We only import data of one branch currently, so just add one node based on any commits branch
        MERGE (b:Branch {{name: c.branch}})
        
        WITH b
        MATCH (latest_commit:Commit)
        WHERE NOT(()-[:PARENT]->(latest_commit))
        
        MERGE (b)-[:LATEST_COMMIT]-(latest_commit)
'''
        result = Neo4j.run_query(query)
        print(result)

    @staticmethod
    def _add_meta_data_node():
        deployment_automation_name_wrapped = TwinMetaDataManager._wrap_in_quotes(
            Config.get_deployment_automation_name())
        test_automation_names_wrapped = map(TwinMetaDataManager._wrap_in_quotes, Config.get_test_automation_names())

        query = f'''
                MERGE (m:TwinMetaData)
                SET
                    m.main_branch = '{Config.get_main_branch()}',
                    m.project_management_bug_categories = {Config.project_management_bug_categories()},
                    m.deployment_automation_name = {deployment_automation_name_wrapped},
                    m.test_automation_names = [{', '.join(test_automation_names_wrapped)}],
                    m.commit_data_source = '{Config.get_commit_data_source()}',
                    m.deployment_data_source = '{Config.get_deployment_data_source()}',
                    m.project_management_data_source = '{Config.get_project_management_data_source()}',
                    m.automations_data_source = '{Config.get_automations_data_source()}',
                    m.automations_history_data_source = '{Config.get_automations_history_data_source()}'
        '''
        result = Neo4j.run_query(query)
        print(result)

    # wrap in double quotes but escape double quotes beforehand
    @staticmethod
    def _wrap_in_quotes(input_string):
        input_string_with_escaped_quotes = input_string.replace('"', '\\"')
        return f'"{input_string_with_escaped_quotes}"'
