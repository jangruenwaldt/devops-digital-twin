from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.config import Config
from utils.constants.constants import DataTypes, DataSources
from utils.data_manager import DataManager


class GitHubAutomationHistoryDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url):
        super().__init__(repo_url)

    def _get_workflows(self):
        # relies on the fact that we always fetch the workflows before the workflow history
        return DataManager.retrieve_twin_data(DataTypes.AUTOMATION_DATA, self.owner, self.repo_name)

    def _fetch_automation_runs(self):
        workflows = self._get_workflows()

        raw_automation_history = []
        for wf_data in workflows:
            api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows/{wf_data["id"]}/runs' \
                      f'?per_page=100&created=>{Config.get_automation_history_since()}'

            workflow_runs = self._fetch_from_paginated_counted_api(api_url, 'workflow_runs')
            raw_automation_history.extend(workflow_runs)

        if self.enable_logs:
            print(f'Fetched {len(raw_automation_history)} automation runs')

        return raw_automation_history

    @staticmethod
    def _transform_api_response_to_data_format(data):
        return {
            'id': data['id'],
            'name': data['name'],
            'head_branch': data['head_branch'],
            'head_sha': data['head_sha'],
            'path': data['path'],
            'run_number': data['run_number'],
            'event': data['event'],
            'status': data['status'],
            'conclusion': data['conclusion'],
            'workflow_id': data['workflow_id'],
            'url': data['url'],
            'run_started_at': datetime.strptime(data['run_started_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0).isoformat(),
            'updated_at': datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0).isoformat(),
            'started_by': data.get('triggering_actor', {}).get('login', None),
            'run_attempt': data['run_attempt'],
        }

    def fetch_data(self):
        raw_automation_history = self._fetch_automation_runs()
        DataManager.store_raw_api_data(DataTypes.AUTOMATION_HISTORY, DataSources.GITHUB, self.owner, self.repo_name,
                                       raw_automation_history)

        automation_history = list(map(self._transform_api_response_to_data_format, raw_automation_history))
        DataManager.store_twin_data(DataTypes.AUTOMATION_HISTORY, self.owner, self.repo_name, automation_history)
