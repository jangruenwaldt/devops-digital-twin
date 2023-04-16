import json
import os

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
            'Authorization': f'token {Config.get_pat()}'
        }
