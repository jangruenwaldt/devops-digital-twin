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
    def get_paginated(url, request_headers=None):
        link_key = f'next_link:{url}'

        data = Cache.load(url)
        next_link = Cache.load(link_key)
        if data is None or next_link is None:
            response = requests.get(url, headers=request_headers)
            response.raise_for_status()

            data = response.json()
            next_link = response.links['next']['url']

            Cache.update(url, data)
            Cache.update(link_key, next_link)
        return data, next_link
