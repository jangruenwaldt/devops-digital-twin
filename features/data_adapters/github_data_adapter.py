import json
import os
from datetime import datetime

from git import Repo

from destinations import LOCAL_DATA_DIR, DATA_EXPORT_DIR
from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config
from utils.constants.twin_constants import TwinConstants
from utils.github_utils import GitHubUtils


class GitHubDataAdapter:
    def __init__(self, repo_url, branch='main'):
        self.repo_url = repo_url
        self.branch = branch
        self.owner, self.repo_name = GitHubUtils.get_owner_and_repo_name(repo_url)
        if not os.path.exists(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)

    def _export_as_json(self, data, file_name):
        data_dir = os.path.join(DATA_EXPORT_DIR, self.owner, self.repo_name)

        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, file_name), 'w') as output_file:
            json.dump(data, output_file)

    def fetch_twin_data(self, debug_options=None):
        self.export_commit_data_as_json(debug_options=debug_options)
        self.export_deployment_data_as_json(debug_options=debug_options)
        self.export_issue_data_as_json(debug_options=debug_options)

    def export_issue_data_as_json(self, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        issues = self.fetch_issues()
        issue_data_list = []
        for issue in issues:
            issue_data = {
                'url': issue['url'],
                'id': issue['id'],
                'title': issue['title'],
                'state': issue['state'],
                'locked': issue['locked'],
                'user': issue['user'] if issue['user'] is not None else None,
                'assignee': issue['assignee'] if issue['assignee'] is not None else None,
                'milestone': issue['milestone'] if issue['milestone'] is not None else None,
                'comments': issue['comments'],
                'created_at': datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'updated_at': issue['updated_at'],
                'closed_at': datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat() if issue['closed_at'] is not None else None,
                'body': issue['body']
            }

            label_list = []
            for label in issue['labels']:
                label_id = label['id']
                label_data = {
                    'id': label_id,
                    'url': f'{self.repo_url}/labels/{label["name"]}',
                    'name': label['name'],
                    'color': label['color'],
                    'description': label['description'],
                }
                label_list.append(label_data)
            issue_data['labels'] = label_list

            issue_data_list.append(issue_data)
            if enable_logs:
                print(f'Added issue with id {issue["id"]}')

        self._export_as_json(issue_data_list, TwinConstants.ISSUES_DATA_FILE_NAME)

    def export_deployment_data_as_json(self, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        releases = self.fetch_releases()

        deployments_sorted = sorted(releases, key=lambda r: datetime.strptime(r['published_at'], '%Y-%m-%dT%H:%M:%SZ'))
        deployment_data = []
        for release in deployments_sorted:
            tag_name = release['tag_name']

            latest_commit_hash = self.get_latest_commit_hash_in_release(tag_name)
            release_url = self.repo_url + f'/releases/tag/{tag_name}'
            commit_url = self.repo_url + f'/commit/{latest_commit_hash}'
            publish_date = release['published_at']
            deployment = {
                'id': release['id'],
                'tag_name': tag_name,
                'published_at': datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'release_url': release_url,
                'commit_url': commit_url,
                'latest_included_commit': latest_commit_hash,
                'previous_deployment': None if len(deployment_data) == 0 else deployment_data[-1]['tag_name'],
            }
            if enable_logs:
                print(f'Deployment with tag {tag_name} added.')
            deployment_data.append(deployment)

        self._export_as_json(deployment_data, TwinConstants.DEPLOYMENT_DATA_FILE_NAME)

    def export_commit_data_as_json(self, debug_options=None):
        if not os.path.exists(DATA_EXPORT_DIR):
            os.makedirs(DATA_EXPORT_DIR)

        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        commits = self.fetch_commits()
        export_data = []
        for commit in commits:
            # GitHub API 'quirk', sometimes only committer is set and author is None,
            # and sometimes author is set but committer is 'web-flow' when done via web UI, so we
            # give priority to the author field unless it is None.
            if commit['author'] is None:
                author = commit['committer']['login']
            else:
                author = commit['author']['login']
            commit_data = {
                'message': commit['commit']['message'],
                'hash': commit['sha'],
                'author': author,
                'date': datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').replace(
                    microsecond=0).isoformat(),
                'branch': self.branch,
                'url': (self.repo_url + f'/commit/{commit["sha"]}'),
                'parents': list(map(lambda c: c['url'], commit['parents']))
            }
            export_data.append(commit_data)
            if enable_logs:
                print(f'Added commit with hash {commit["sha"]}.')

        self._export_as_json(export_data, TwinConstants.COMMIT_DATA_FILE_NAME)

    def fetch_issues(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/issues?state=all'
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

    def fetch_releases(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/releases'
        initial_url = api_url

        cached_data = Cache.load(api_url)
        if cached_data is not None:
            return cached_data

        all_releases = self.fetch_from_paginated_api(api_url)
        Cache.update(initial_url, all_releases)
        return all_releases

    def fetch_commits(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/commits?sha={self.branch}'
        initial_url = api_url

        cached_data = Cache.load(api_url)
        if cached_data is not None:
            return cached_data

        all_commits = self.fetch_from_paginated_api(api_url)
        Cache.update(initial_url, all_commits)
        return all_commits

    def get_latest_commit_hash_in_release(self, tag_name):
        tag_object = CachedRequest.get_json(
            f'https://api.github.com/repos/{self.owner}/{self.repo_name}/git/refs/tags/{tag_name}',
            headers=Config().get_github_request_header())
        return tag_object['object']['sha']
