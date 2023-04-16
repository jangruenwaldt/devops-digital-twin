import json
import os

from destinations import ROOT_DIR

CACHE_FILE = f'{ROOT_DIR}/api_cache.json'


class Cache:
    @staticmethod
    def load(key):
        if not os.path.isfile(CACHE_FILE):
            return None

        with open(CACHE_FILE, 'r') as cache_file:
            cache_data = json.load(cache_file)
            if key in cache_data:
                print(f'Cache hit for {key}')
                val = cache_data[key]
                del cache_data  # might save some memory
                return val

        print(f'Cache miss for {key}')
        return None

    @staticmethod
    def update(key, data):
        print(f'Saving {key} into cache')

        if not os.path.isfile(CACHE_FILE):
            with open(CACHE_FILE, 'w') as cache_file:
                json.dump({}, cache_file)

        with open(CACHE_FILE, 'r') as cache_file:
            cache_data = json.load(cache_file)

        cache_data[key] = data
        with open(CACHE_FILE, 'w') as cache_file:
            json.dump(cache_data, cache_file)
            del cache_data  # might save some memory
