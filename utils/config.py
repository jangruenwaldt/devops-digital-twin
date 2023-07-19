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


class Config:
    @staticmethod
    def get_pat():
        return CONFIG_DATA.get('personal_access_token', None)

    @staticmethod
    def get_enable_logs():
        return CONFIG_DATA.get('enable_logs', None) == 'true'

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
    def get_update_interval_in_hours():
        return CONFIG_DATA.get('update_interval_in_hours', None)

    @staticmethod
    def get_db_user():
        return CONFIG_DATA.get('db_user', None)

    @staticmethod
    def get_db_pw():
        return CONFIG_DATA.get('db_pw', None)

    @staticmethod
    def get_db_address():
        return CONFIG_DATA.get('db_address', None)

    @staticmethod
    def get_github_request_header():
        return {
            'Authorization': f'token {Config.get_pat()}',
            'Accept': 'application/vnd.github+json'
        }
