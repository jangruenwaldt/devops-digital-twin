import json
import os

from destinations import ROOT_DIR

CACHE_DIR = f'{ROOT_DIR}/.api_cache'


class Cache:
    @staticmethod
    def get_cache_file_path(key):
        return os.path.join(CACHE_DIR, f'{key}.json')

    @staticmethod
    def load(key):
        cache_file_path = Cache.get_cache_file_path(key)

        if not os.path.isfile(cache_file_path):
            print(f'Cache miss for {key}')
            return None

        with open(cache_file_path, 'r') as cache_file:
            print(f'Cache hit for {key}')
            return json.load(cache_file)

    @staticmethod
    def update(key, data):
        print(f'Saving {key} into cache')

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        cache_file_path = Cache.get_cache_file_path(key)
        with open(cache_file_path, 'w') as cache_file:
            json.dump(data, cache_file)
