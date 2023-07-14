import json
import os

from features.data_adapters.github.utils.github_utils import GitHubUtils
from utils.config import Config
from utils.request import Request


class GitHubDataFetcher:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.owner, self.repo_name = GitHubUtils.get_owner_and_repo_name(repo_url)
        self.enable_logs = Config.get_enable_logs()

    @staticmethod
    def _fetch_from_paginated_api(api_url):
        data = []
        headers = Config.get_github_request_header()
        if '?' in api_url:
            api_url += '&per_page=100'
        else:
            api_url += '?per_page=100'

        while api_url is not None:
            new_data, api_url = Request.get_paginated(api_url, headers=headers)
            data.extend(new_data)

        return data

    # Use with APIs that do not return arrays but instead an object with
    #     # {
    #     #   "total_count": 2,
    #     #   "data": [..]
    #     # }
    @staticmethod
    def _fetch_from_paginated_counted_api(api_url, data_object_key):
        data = []
        headers = Config.get_github_request_header()
        if '?' in api_url:
            api_url += '&per_page=100'
        else:
            api_url += '?per_page=100'

        while api_url is not None:
            new_data, api_url = Request.get_paginated(api_url, headers=headers)
            data.extend(new_data[data_object_key])

        return data
