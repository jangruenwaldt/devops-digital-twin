import requests


class Request:
    @staticmethod
    def get_json(url, headers=None):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_paginated(url, headers=None, stopping_condition=None):
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        next_link = None
        should_stop = stopping_condition is not None and stopping_condition(data)
        if 'next' in response.links and not should_stop:
            next_link = response.links['next']['url']

        return data, next_link if next_link != '' else None
