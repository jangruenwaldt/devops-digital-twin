from utils.cache import Cache
from utils.request import Request


class CachedRequest:
    @staticmethod
    def get_json(url, headers=None):
        data = Cache.load(url)
        if data is None:
            data = Request.get_json(url, headers=headers)
            Cache.update(url, data)
        return data
