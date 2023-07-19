from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.cache import Cache
from utils.constants.constants import DataTypes, DataSources
from utils.data_manager import DataManager


class GitHubCommitDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url, branch='main'):
        super().__init__(repo_url)
        self.branch = branch

    @staticmethod
    def _get_commit_author(commit):
        # GitHub API 'quirk', sometimes only committer is set and author is None,
        # and sometimes author is set but committer is 'web-flow' when done via web UI, so we
        # give priority to the author field unless it is None.
        if commit['author'] is None:
            if commit['committer'] is None:
                author = "unknown"
            else:
                author = commit['committer']['login']
        else:
            author = commit['author']['login']

        # In some cases, it is still web-flow. Then, we use the ['commit]['author']['name'] field instead
        if author == 'web-flow' or author == 'unknown':
            return commit['commit']['author']['name']
        return author

    def _fetch_commits(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/commits?sha={self.branch}'

        cached_data = Cache.load(api_url)
        if cached_data is not None:
            return cached_data

        all_commits = self._fetch_from_paginated_api(api_url)
        Cache.update(api_url, all_commits)
        return all_commits

    def fetch_data(self):
        commits = self._fetch_commits()
        DataManager.store_raw_api_data(DataTypes.COMMIT_DATA, self.owner, self.repo_name, DataSources.GITHUB, commits)

        export_data = self._transform_api_response_to_data_format(commits, self.enable_logs)
        DataManager.store_twin_data(DataTypes.COMMIT_DATA, self.owner, self.repo_name, export_data)

    def _transform_api_response_to_data_format(self, commits, enable_logs):
        export_data = []
        for commit in reversed(commits):
            author = self._get_commit_author(commit)
            commit_data = {
                'message': commit['commit']['message'],
                'hash': commit['sha'],
                'author': author,
                'date': datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'branch': self.branch,
                'url': (self.repo_url + f'/commit/{commit["sha"]}'),
                'parents': list(map(lambda c: c['sha'], commit['parents']))
            }
            export_data.append(commit_data)
            if enable_logs:
                print(f'Added commit with hash {commit["sha"]}.')
        return export_data
