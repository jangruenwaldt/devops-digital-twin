import requests

from utils.cache import Cache


class CachedRequest:
    @staticmethod
    def get_json(url, headers=None):
        data = Cache.load(url)
        if data is None:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            Cache.update(url, data)
        return data
