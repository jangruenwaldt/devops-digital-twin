import json
import os

from destinations import DATA_EXPORT_DIR


class TwinDataRetriever:
    @staticmethod
    def retrieve(data_type):
        file_path = os.path.join(DATA_EXPORT_DIR, data_type + '.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        else:
            return None
