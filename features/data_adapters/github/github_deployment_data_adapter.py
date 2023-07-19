from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config
from utils.constants.constants import DataTypes, DataSources
from utils.data_manager import DataManager


class GitHubDeploymentDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url):
        super().__init__(repo_url)

    def _get_latest_commit_hash_in_release(self, tag_name):
        tag_object = CachedRequest.get_json(
            f'https://api.github.com/repos/{self.owner}/{self.repo_name}/git/refs/tags/{tag_name}',
            headers=Config().get_github_request_header())
        return tag_object['object']['sha']

    def _fetch_releases(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/releases'

        cached_data = DataManager.retrieve_raw_api_data(DataTypes.DEPLOYMENT_DATA, DataSources.GITHUB, self.owner,
                                                        self.repo_name)
        if cached_data is not None:
            latest_release = max(cached_data, key=lambda x: x.get('published_at', ''))

            def check_if_existing_release_reached(new_data):
                return max(new_data, key=lambda x: x.get('published_at', ''))['tag_name'] == latest_release['tag_name']

            newly_fetched_data = self._fetch_from_paginated_api(api_url,
                                                                stopping_condition=check_if_existing_release_reached)
            return self._merge_data(cached_data, newly_fetched_data, merge_key='tag_name')
        else:
            return self._fetch_from_paginated_api(api_url)

    def fetch_data(self):
        releases = self._fetch_releases()
        DataManager.store_raw_api_data(DataTypes.DEPLOYMENT_DATA, DataSources.GITHUB, self.owner, self.repo_name,
                                       releases)

        deployment_data = self._transform_api_response_to_data_format(self.enable_logs, releases)
        DataManager.store_twin_data(DataTypes.DEPLOYMENT_DATA, self.owner, self.repo_name, deployment_data)

    def _transform_api_response_to_data_format(self, enable_logs, releases):
        deployments_sorted = sorted(releases, key=lambda r: datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'))
        deployment_data = []
        for release in deployments_sorted:
            name = release['tag_name']

            latest_commit_hash = self._get_latest_commit_hash_in_release(name)
            url = self.repo_url + f'/releases/tag/{name}'
            commit_url = self.repo_url + f'/commit/{latest_commit_hash}'
            publish_date = release['published_at']
            deployment = {
                'id': release['id'],
                'name': name,
                'published_at': datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'url': url,
                'commit_url': commit_url,
                'latest_included_commit': latest_commit_hash,
                'previous_deployment': None if len(deployment_data) == 0 else deployment_data[-1]['name'],
            }
            if enable_logs:
                print(f'Deployment with tag {name} added.')
            deployment_data.append(deployment)
        return deployment_data
