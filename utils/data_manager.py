import json
import os

from destinations import TWIN_DATA_EXPORT_DIR, RAW_API_DATA_EXPORT_DIR, KEY_VALUE_DATA_EXPORT_DIR


class DataManager:
    @staticmethod
    def store_by_key(key, value):
        return DataManager._store_file(KEY_VALUE_DATA_EXPORT_DIR, 'data', 'keys', f'{key}.json', {'data': value})

    @staticmethod
    def retrieve_by_key(key):
        data = DataManager._retrieve_file(KEY_VALUE_DATA_EXPORT_DIR, 'data', 'keys', f'{key}.json')
        if data is not None:
            return data['data']
        return None

    @staticmethod
    def retrieve_twin_data(data_type, owner, repo):
        return DataManager._retrieve_file(TWIN_DATA_EXPORT_DIR, owner, repo, f'{data_type}.json')

    @staticmethod
    def retrieve_raw_api_data(data_type, data_source, owner, repo):
        return DataManager._retrieve_file(RAW_API_DATA_EXPORT_DIR, owner, repo, f'{data_source}_{data_type}.json')

    @staticmethod
    def store_twin_data(data_type, owner, repo, data):
        return DataManager._store_file(TWIN_DATA_EXPORT_DIR, owner, repo, f'{data_type}.json', data)

    @staticmethod
    def store_raw_api_data(data_type, data_source, owner, repo, data):
        return DataManager._store_file(RAW_API_DATA_EXPORT_DIR, owner, repo, f'{data_source}_{data_type}.json', data)

    @staticmethod
    def _retrieve_file(directory, owner, repo, file_name):
        file_path = os.path.join(directory, owner, repo, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        else:
            return None

    @staticmethod
    def _store_file(directory, owner, repo, file_name, data):
        data_dir = os.path.join(directory, owner, repo)
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, file_name), 'w') as output_file:
            json.dump(data, output_file)
