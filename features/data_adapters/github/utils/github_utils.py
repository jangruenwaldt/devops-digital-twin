from utils.cached_request import CachedRequest
from utils.config import Config


class GitHubUtils:
    @staticmethod
    def get_owner_and_repo_name(repo_url):
        data = repo_url.replace('https://github.com/', '').split('/')
        return [data[0], data[1]]

    @staticmethod
    def get_raw_file_link(repo_url):
        repo_info = GitHubUtils.fetch_repo_info_from_api(repo_url)
        owner, repo_name = GitHubUtils.get_owner_and_repo_name(repo_url)
        default_branch = repo_info['default_branch']
        return f'https://raw.githubusercontent.com/{owner}/{repo_name}/{default_branch}/'

    @staticmethod
    def fetch_repo_info_from_api(repo_url):
        owner, repo_name = GitHubUtils.get_owner_and_repo_name(repo_url)
        api_url = f'https://api.github.com/repos/{owner}/{repo_name}'
        return CachedRequest.get_json(api_url, headers=Config.get_github_request_header())
