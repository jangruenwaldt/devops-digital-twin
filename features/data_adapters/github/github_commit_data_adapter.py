from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.constants.constants import DataTypes, DataSources
from utils.data_manager import DataManager
from utils.utils import Utils


class GitHubCommitDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url, branch='main'):
        super().__init__(repo_url)
        self.branch = branch

    def _fetch_commits(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/commits?sha={self.branch}'

        cached_data = DataManager.retrieve_raw_api_data(DataTypes.COMMIT_DATA, DataSources.GITHUB, self.owner,
                                                        self.repo_name)
        if cached_data is not None:
            latest_commit = cached_data[0]  # relies on correct ordering!

            def stop_if_existing_commit_reached(new_data):
                return latest_commit['sha'] in map(lambda x: x.get('sha', ''), new_data)

            newly_fetched_data = self._fetch_from_paginated_api(api_url,
                                                                stopping_condition=stop_if_existing_commit_reached)
            if self.enable_logs:
                print(
                    f'Fetched {len(newly_fetched_data)} commits from GitHub API,'
                    f' found {len(cached_data)} commits in cache.')
            return self._merge_data(cached_data, newly_fetched_data, merge_key='sha')
        else:
            data = self._fetch_from_paginated_api(api_url)

            if self.enable_logs:
                print(f'Fetched {len(data)} commits from GitHub API')

            return data

    def fetch_data(self):
        commits = self._fetch_commits()
        DataManager.store_raw_api_data(DataTypes.COMMIT_DATA, DataSources.GITHUB, self.owner, self.repo_name, commits)
        print(f'API returned {len(commits)} commits. Mapping and storing in JSON now.')

        export_data = self._transform_api_response_to_data_format(commits, self.enable_logs)
        DataManager.store_twin_data(DataTypes.COMMIT_DATA, self.owner, self.repo_name, export_data)

    def _transform_api_response_to_data_format(self, commits, enable_logs):
        export_data = []
        for commit in reversed(commits):
            commit_data = {
                'message': commit['commit']['message'],
                'hash': commit['sha'],
                'author': Utils.deep_get(commit, 'author.login', default='unknown'),
                'committer': Utils.deep_get(commit, 'committer.login', default='unknown'),
                'date': datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'branch': self.branch,
                'url': (self.repo_url + f'/commit/{commit["sha"]}'),
                'parents': list(map(lambda c: c['sha'], commit['parents']))
            }
            export_data.append(commit_data)
        return export_data
