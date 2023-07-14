import json
import os

from destinations import TWIN_DATA_EXPORT_DIR, RAW_API_DATA_EXPORT_DIR


class DataManager:
    @staticmethod
    def retrieve_twin_data(data_type, owner, repo):
        return DataManager._retrieve_file(TWIN_DATA_EXPORT_DIR, data_type, owner, repo)

    @staticmethod
    def retrieve_raw_api_data(data_type, owner, repo):
        return DataManager._retrieve_file(RAW_API_DATA_EXPORT_DIR, data_type, owner, repo)

    @staticmethod
    def store_twin_data(data_type, owner, repo, data):
        return DataManager._store_file(TWIN_DATA_EXPORT_DIR, data_type, owner, repo, data)

    @staticmethod
    def store_raw_api_data(data_type, owner, repo, data):
        return DataManager._store_file(RAW_API_DATA_EXPORT_DIR, data_type, owner, repo, data)

    @staticmethod
    def _retrieve_file(directory, data_type, owner, repo):
        file_path = os.path.join(directory, owner, repo, data_type + '.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        else:
            return None

    @staticmethod
    def _store_file(directory, data_type, owner, repo, data):
        data_dir = os.path.join(directory, owner, repo)
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, data_type + '.json'), 'w') as output_file:
            json.dump(data, output_file)
