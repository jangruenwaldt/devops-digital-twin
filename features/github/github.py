import requests

from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config


class GitHub:
    def __init__(self, repo_url):
        self.repo_url = repo_url

    def fetch_issues(self, enable_cache=True):
        owner, repo_name = self.get_owner_and_repo_name()
        return []

    def fetch_releases(self, enable_cache=True):
        owner, repo_name = self.get_owner_and_repo_name()
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}/releases'
        initial_url = api_url

        if enable_cache:
            cached_data = Cache.load(api_url)
            if cached_data is not None:
                return cached_data

        all_releases = []
        headers = Config.get_github_request_header()
        while api_url is not None:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            releases = response.json()
            all_releases.extend(releases)

            # Check if we need to make another request as API is paginated
            api_url = None
            link_header = response.headers.get('Link')
            if link_header is not None:
                links = link_header.split(',')
                for link in links:
                    if 'rel="next"' in link:
                        api_url = link[link.index('<') + 1:link.index('>')]
                        break

        Cache.update(initial_url, all_releases)
        return all_releases

    def get_owner_and_repo_name(self):
        return self.repo_url.split('/')[-2:]

    def get_latest_commit_hash_in_release(self, tag_name):
        owner, repo_name = self.get_owner_and_repo_name()
        tag_object = CachedRequest.get_json(
            f'https://api.github.com/repos/{owner}/{repo_name}/git/refs/tags/{tag_name}',
            headers=Config().get_github_request_header())
        return tag_object['object']['sha']
