import json

from destinations import ROOT_DIR

CONFIG_PATH = f'{ROOT_DIR}/config.json'

with open(CONFIG_PATH, 'r') as f:
    CONFIG_DATA = json.load(f)
    print(f'Using config: {CONFIG_DATA}')


class Config:
    @staticmethod
    def get_pat():
        return CONFIG_DATA['personal_access_token']

    @staticmethod
    def get_db_user():
        return CONFIG_DATA['db_user']

    @staticmethod
    def get_db_pw():
        return CONFIG_DATA['db_pw']

    @staticmethod
    def get_db_address():
        return CONFIG_DATA['db_address']

    @staticmethod
    def get_github_request_header():
        return {
            'Authorization': f'token {Config.get_pat()}'
        }
