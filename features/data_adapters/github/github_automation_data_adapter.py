from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.config import Config
from utils.constants.constants import DataTypes, DataSources
from utils.data_manager import DataManager


class GitHubAutomationDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url, automation_run_history_timeframe_in_months=6):
        super().__init__(repo_url)
        self.automation_run_history_timeframe_in_months = automation_run_history_timeframe_in_months

    def _fetch_workflows(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows'
        data = self._fetch_from_paginated_counted_api(api_url, 'workflows')

        if self.enable_logs:
            print(f'Fetched {len(data)} workflows from GitHub API')

        return data

    def fetch_data(self):
        workflows = self._fetch_workflows()
        # No caching here, as workflows can not be cached since they might always have changed

        automation_data = self._transform_api_response_to_data_format(self.enable_logs, workflows)
        DataManager.store_twin_data(DataTypes.AUTOMATION_DATA, self.owner, self.repo_name, automation_data)

    @staticmethod
    def _transform_api_response_to_data_format(enable_logs, workflows):
        automation_data = []
        for wf_data in workflows:
            data = {
                'id': wf_data['id'],
                'name': wf_data['name'],
                'path': wf_data['path'],
                'created_at': datetime.strptime(wf_data['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').replace(
                    microsecond=0).isoformat(),
                'updated_at': datetime.strptime(wf_data['updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z').replace(
                    microsecond=0).isoformat(),
                'url': wf_data['url'],
                'is_deployment': wf_data['name'] == Config.get_deployment_automation_name()
            }
            if enable_logs:
                print(f'Workflow {wf_data["name"]} data added.')
            automation_data.append(data)
        return automation_data
