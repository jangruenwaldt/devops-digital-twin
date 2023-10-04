import time

import requests

from utils.config import Config


class Request:
    RATE_LIMIT_BACKOFF_SECONDS = 3600

    @staticmethod
    def _rate_limit_reached(response):
        rate_limit_readable = response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers
        if rate_limit_readable:
            limit_remaining = response.headers['X-RateLimit-Remaining']
            print(f'Remaining rate limit: {limit_remaining}')
            return limit_remaining == '0'
        else:
            return False

    @staticmethod
    def _handle_rate_limit():
        print("Rate limit exceeded. Backing off for 1 hour...")
        time.sleep(Request.RATE_LIMIT_BACKOFF_SECONDS)

    @staticmethod
    def _make_request(url, headers=None):
        if Config.get_enable_logs():
            print(f'Fetching from {url}')

        max_retries = 3
        retries = 0
        backoff_seconds = 5

        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers)
                while Request._rate_limit_reached(response):
                    Request._handle_rate_limit()
                    response = requests.get(url, headers=headers)

                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                print(f"Retry attempt {retries + 1} in {backoff_seconds} seconds...")

                retries += 1
                if retries < max_retries:
                    time.sleep(backoff_seconds)
                else:
                    print(f"Max retries reached. Request failed: {url}")
                    raise e

        return None

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
