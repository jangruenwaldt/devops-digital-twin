import json
import os
from datetime import datetime

from destinations import ROOT_DIR

CONFIG_PATH = f'{ROOT_DIR}/config.json'
CONFIG_DATA = {}

# when running tests we do not want to fetch the config as all is mocked
if os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        CONFIG_DATA = json.load(f)


# TODO: Should probably add ConfigChecker class that reports if all mandatory attributes are added.
class Config:

    @staticmethod
    def get_deployment_filter_regex():
        return CONFIG_DATA.get('deployment_regex', None)

    @staticmethod
    def get_pat():
        return CONFIG_DATA.get('personal_access_token', None)

    @staticmethod
    def get_twin_owner():
        return CONFIG_DATA.get('twin_owner', None)

    @staticmethod
    def get_twin_name():
        return CONFIG_DATA.get('twin_name', None)

    @staticmethod
    def project_management_bug_categories():
        return CONFIG_DATA.get('project_management_bug_categories', None)

    @staticmethod
    def get_test_automation_names():
        return CONFIG_DATA.get('test_automation_names', None)

    @staticmethod
    def get_ci_automation_names():
        return CONFIG_DATA.get('ci_automation_names', None)

    @staticmethod
    def get_deployment_automation_name():
        return CONFIG_DATA.get('deployment_automation_name', None)

    @staticmethod
    def get_force_update_on_first_launch():
        return CONFIG_DATA.get('force_update_on_first_launch', None) == 'true'

    @staticmethod
    def get_enable_logs():
        return CONFIG_DATA.get('enable_logs', None) == 'true'

    @staticmethod
    def get_override_existing_data():
        return CONFIG_DATA.get('override_existing_data', None) == 'true'

    @staticmethod
    def get_automation_history_since():
        config_value = CONFIG_DATA.get('automation_history_since', None)
        if config_value is not None:
            return datetime.strptime(config_value, '%Y-%m-%d').isoformat()
        return None

    @staticmethod
    def get_main_branch():
        return CONFIG_DATA.get('main_branch', None)

    @staticmethod
    def get_commit_data_source():
        return CONFIG_DATA.get('commit_data_source', None)

    @staticmethod
    def get_deployment_data_source():
        return CONFIG_DATA.get('deployment_data_source', None)

    @staticmethod
    def get_project_management_data_source():
        return CONFIG_DATA.get('project_management_data_source', None)

    @staticmethod
    def get_automations_data_source():
        return CONFIG_DATA.get('automations_data_source', None)

    @staticmethod
    def get_automations_history_data_source():
        return CONFIG_DATA.get('automations_history_data_source', None)

    @staticmethod
    def update_interval_in_minutes():
        config_value = CONFIG_DATA.get('update_interval_in_minutes', None)
        if config_value is not None:
            return int(config_value)
        return 60

    # db connection hardcoded as db is run via Docker
    @staticmethod
    def get_db_user():
        return 'neo4j'

    @staticmethod
    def get_db_pw():
        return 'password'

    @staticmethod
    def get_db_address():
        return 'bolt://neo4j:7687'

    @staticmethod
    def get_github_request_header():
        return {
            'Authorization': f'token {Config.get_pat()}',
            'Accept': 'application/vnd.github+json'
        }
