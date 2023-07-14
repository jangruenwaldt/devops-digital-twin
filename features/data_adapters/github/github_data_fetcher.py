import json
import os

from destinations import DATA_EXPORT_DIR
from utils.cached_request import CachedRequest
from utils.config import Config
from utils.github_utils import GitHubUtils


class GitHubDataFetcher:
    def __init__(self, repo_url, debug_options):
        self.repo_url = repo_url
        self.owner, self.repo_name = GitHubUtils.get_owner_and_repo_name(repo_url)
        self.debug_options = debug_options or {}
        self.enable_logs = 'enable_logs' in self.debug_options and self.debug_options['enable_logs']

    def _export_as_json(self, data, file_name):
        data_dir = os.path.join(DATA_EXPORT_DIR, self.owner, self.repo_name)
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, file_name), 'w') as output_file:
            json.dump(data, output_file)

    @staticmethod
    def _fetch_from_paginated_api(api_url):
        data = []
        headers = Config.get_github_request_header()
        if '?' in api_url:
            api_url += '&per_page=100'
        else:
            api_url += '?per_page=100'

        while api_url is not None:
            new_data, api_url = CachedRequest.get_paginated(api_url, headers=headers)
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
            new_data, api_url = CachedRequest.get_paginated(api_url, headers=headers)
            data.extend(new_data[data_object_key])

        return data
