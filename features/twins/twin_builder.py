import os
from datetime import datetime

from destinations import TWIN_DATA_EXPORT_DIR
from features.data_adapters.data_adapters import CommitDataAdapter, DeploymentDataAdapter, ProjectManagementDataAdapter, \
    AutomationDataAdapter, AutomationHistoryDataAdapter
from features.twins.automations_twin import AutomationsTwin
from features.twins.deployments_twin import DeploymentsTwin
from features.twins.git_twin import GitTwin
from features.twins.project_management_twin import ProjectManagementTwin
from features.twins.twin_meta_data_manager import TwinMetaDataManager
from utils.config import Config
from utils.constants.constants import DataTypes
from utils.data_manager import DataManager
from utils.utils import Utils


class TwinBuilder:

    @staticmethod
    def build():
        TwinBuilder.fetch()
        TwinBuilder.construct_twin()
        TwinMetaDataManager.add_metadata()
        TwinBuilder.print_usage_info()

    @staticmethod
    def construct_twin():
        if Config.get_enable_logs():
            print(f'Constructing twin in neo4j...'
                  f'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        data_dir = os.path.join(TWIN_DATA_EXPORT_DIR, Config.get_twin_owner(), Config.get_twin_name())

        commit_data = os.path.join(data_dir, f'{DataTypes.COMMIT_DATA}.json')
        deployment_data = os.path.join(data_dir, f'{DataTypes.DEPLOYMENT_DATA}.json')
        project_management_data = os.path.join(data_dir, f'{DataTypes.PROJECT_MANAGEMENT_DATA}.json')
        automation_data = os.path.join(data_dir, f'{DataTypes.AUTOMATION_DATA}.json')
        automation_history_data = os.path.join(data_dir, f'{DataTypes.AUTOMATION_HISTORY}.json')

        GitTwin.construct_from_json(commit_data)
        DeploymentsTwin.construct_from_json(deployment_data)
        ProjectManagementTwin.construct_from_json(project_management_data)
        AutomationsTwin.construct_from_json(automation_data, automation_history_data)

        TwinMetaDataManager.add_metadata()

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
