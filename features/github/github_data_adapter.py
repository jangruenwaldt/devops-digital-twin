import json
import os

from git import Repo

from destinations import LOCAL_DATA_DIR, TWIN_DATA_EXPORT_DIR
from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config


class GitHubDataAdapter:
    def __init__(self, repo_url, branch='main'):
        self.repo_url = repo_url
        self.branch = branch

    @staticmethod
    def setup():
        if not os.path.exists(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)

    def export_commit_data_as_json(self, debug_options=None):
        self.setup()
        if not os.path.exists(TWIN_DATA_EXPORT_DIR):
            os.makedirs(TWIN_DATA_EXPORT_DIR)

        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        repo_owner_slash_name = self.repo_url.split("https://github.com/")[1]
        repo_dir = f'{LOCAL_DATA_DIR}/{repo_owner_slash_name}'

        if not os.path.exists(repo_dir):
            if enable_logs:
                print('repo did not exist locally yet, cloning now')
            Repo.clone_from(self.repo_url, repo_dir)
        elif enable_logs:
            print('found repo locally')

        repo = Repo(repo_dir)
        repo.git.checkout(self.branch)
        repo.remotes.origin.pull()

        commits = []
        for commit in repo.iter_commits(self.branch, reverse=True):
            commit_data = {
                'message': commit.message,
                'hash': commit.hexsha,
                'author': commit.author.email,
                'date': commit.committed_datetime.replace(microsecond=0).isoformat(),
                'branch': self.branch,
                'url': (self.repo_url + f'/commit/{commit.hexsha}'),
                'parents': list(map(lambda c: c.hexsha, commit.parents))
            }
            commits.append(commit_data)
        repo.close()

        with open(os.path.join(TWIN_DATA_EXPORT_DIR, 'commits.json'), 'w') as output_file:
            json.dump(commits, output_file)

    def fetch_issues(self):
        owner, repo_name = self.get_owner_and_repo_name()
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}/issues?state=all'
        return self.fetch_from_paginated_api(api_url)

    @staticmethod
    def fetch_from_paginated_api(api_url):
        data = []
        headers = Config.get_github_request_header()
        if '?' in api_url:
            api_url += '&per_page=100'
        else:
            api_url += '?per_page=100'

        while api_url is not None:
            new_data, api_url = CachedRequest.get_paginated(api_url, request_headers=headers)
            data.extend(new_data)

        return data

    def fetch_releases(self, enable_cache=True):
        owner, repo_name = self.get_owner_and_repo_name()
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}/releases'
        initial_url = api_url

        if enable_cache:
            cached_data = Cache.load(api_url)
            if cached_data is not None:
                return cached_data

        all_releases = self.fetch_from_paginated_api(api_url)
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
