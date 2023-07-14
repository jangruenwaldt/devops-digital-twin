import requests


class Request:
    @staticmethod
    def get_json(url, headers=None):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_paginated(url, headers=None):
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        next_link = None
        if 'next' in response.links:
            next_link = response.links['next']['url']

        return data, next_link if next_link != '' else None
