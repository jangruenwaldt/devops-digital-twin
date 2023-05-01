import json
import os
from datetime import datetime

from git import Repo

from destinations import LOCAL_DATA_DIR, DATA_EXPORT_DIR
from utils.cache import Cache
from utils.cached_request import CachedRequest
from utils.config import Config


class GitHubDataAdapter:
    def __init__(self, repo_url, branch='main'):
        self.repo_url = repo_url
        self.branch = branch
        if not os.path.exists(LOCAL_DATA_DIR):
            os.makedirs(LOCAL_DATA_DIR)

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
                    'url': label['url'],
                    'name': label['name'],
                    'color': label['color'],
                    'description': label['description'],
                }
                label_list.append(label_data)
            issue_data['labels'] = label_list

            issue_data_list.append(issue_data)
            if enable_logs:
                print(f'Added issue with id {issue["id"]}')

        with open(os.path.join(DATA_EXPORT_DIR, 'issues.json'), 'w') as output_file:
            json.dump(issue_data_list, output_file)

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

        with open(os.path.join(DATA_EXPORT_DIR, 'deployments.json'), 'w') as output_file:
            json.dump(deployment_data, output_file)

    def export_commit_data_as_json(self, debug_options=None):
        if not os.path.exists(DATA_EXPORT_DIR):
            os.makedirs(DATA_EXPORT_DIR)

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
            if enable_logs:
                print(f'Added commit with hash {commit.hexsha}.')
        repo.close()

        with open(os.path.join(DATA_EXPORT_DIR, 'commits.json'), 'w') as output_file:
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

    def fetch_releases(self):
        owner, repo_name = self.get_owner_and_repo_name()
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}/releases'
        initial_url = api_url

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
