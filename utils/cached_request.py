import requests

from utils.cache import Cache
from utils.config import Config


class CachedRequest:
    @staticmethod
    def get_json(url):
        data = Cache.load(url)
        if data is None:
            response = requests.get(url, headers=Config().get_request_header())
            response.raise_for_status()
            data = response.json()
            Cache.update(url, data)
        return data
