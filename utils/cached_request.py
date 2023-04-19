import json

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

    @staticmethod
    def get(url, request_headers=None):
        header_key = f'headers:{url}'

        data = Cache.load(url)
        response_headers = Cache.load(header_key)
        if data is None or response_headers is None:
            response = requests.get(url, headers=request_headers)
            response.raise_for_status()

            data = response.json()
            response_headers = response.headers

            Cache.update(url, data)
            Cache.update(header_key, dict(response_headers))
        return data, response_headers
