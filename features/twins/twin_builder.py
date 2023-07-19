from datetime import datetime

from features.data_adapters.data_adapters import CommitDataAdapter, DeploymentDataAdapter, ProjectManagementDataAdapter, \
    AutomationDataAdapter, AutomationHistoryDataAdapter
from features.twins.twin_link_creator import TwinLinkCreator
from utils.config import Config
from utils.data_manager import DataManager
from utils.utils import Utils


class TwinBuilder:

    @staticmethod
    def build():
        TwinBuilder.fetch()
        TwinBuilder.construct_twin()
        TwinBuilder.print_usage_info()

    @staticmethod
    def construct_twin():
        if Config.get_enable_logs():
            print(f'Constructing twin in neo4j...'
                  f'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        # GitTwin.construct_from_json(commit_data)
        # DeploymentsTwin.construct_from_json(deployment_data)
        # ProjectManagementTwin.construct_from_json(issue_data)
        # AutomationsTwin.construct_from_json(automation_data, automation_history_data)
        # TwinLinkCreator.create_links()

    @staticmethod
    def fetch():
        if Config.get_enable_logs():
            print(f'Fetching/updating data for twin...'
                  f'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        DataManager.store_by_key('last_data_fetch', Utils.datetime_to_str(datetime.now()))

        commit_data_source = Config.get_commit_data_source()
        deployment_data_source = Config.get_deployment_data_source()
        project_management_data_source = Config.get_project_management_data_source()
        automations_data_source = Config.get_automations_data_source()
        automations_history_data_source = Config.get_automations_history_data_source()
        CommitDataAdapter.fetch_data(commit_data_source, branch=Config.get_main_branch())
        DeploymentDataAdapter.fetch_data(deployment_data_source)
        ProjectManagementDataAdapter.fetch_data(project_management_data_source)
        AutomationDataAdapter.fetch_data(automations_data_source)
        AutomationHistoryDataAdapter.fetch_data(automations_history_data_source)

    @staticmethod
    def print_usage_info():
        print(""""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@    DONE CONSTRUCTING TWIN    @@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        
Time to explore! Visit the graph at https://www.yworks.com/neo4j-explorer/
You might be interested in some queries:

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View everything (not recommended for > 1000 nodes): @
@                                                     @
@                 match (n) return n                  @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View releases:                                      @
@                                                     @
@            match (n:Deployment) return n            @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View relationships between releases and commits:    @
@                                                     @
@ MATCH (n)-[:LATEST_INCLUDED_COMMIT]->(l)            @
@ RETURN n, l                                         @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""")
