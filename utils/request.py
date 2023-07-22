import time

import requests

from utils.config import Config


class Request:
    RATE_LIMIT_BACKOFF_SECONDS = 3600

    @staticmethod
    def _rate_limit_reached(response):
        return response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers[
            'X-RateLimit-Remaining'] == '0'

    @staticmethod
    def _handle_rate_limit():
        print("Rate limit exceeded. Backing off for 1 hour...")
        time.sleep(Request.RATE_LIMIT_BACKOFF_SECONDS)

    @staticmethod
    def _make_request(url, headers=None):
        if Config.get_enable_logs():
            print(f'Fetching from {url}')
        response = requests.get(url, headers=headers)
        while Request._rate_limit_reached(response):
            Request._handle_rate_limit()
            response = requests.get(url, headers=headers)

        response.raise_for_status()
        return response

    @staticmethod
    def get_json(url, headers=None):
        response = Request._make_request(url, headers=headers)
        return response.json()

    @staticmethod
    def get_paginated(url, headers=None, stopping_condition=None):
        response = Request._make_request(url, headers=headers)
        data = response.json()

        next_link = None
        should_stop = stopping_condition is not None and stopping_condition(data)
        if 'next' in response.links and not should_stop:
            next_link = response.links['next']['url']

        return data, next_link if next_link != '' else None
