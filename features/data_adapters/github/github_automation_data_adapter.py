from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.constants.twin_constants import DataTypeFileNames


class GitHubAutomationDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url, automation_run_history_timeframe_in_months=6):
        super().__init__(repo_url)
        self.automation_run_history_timeframe_in_months = automation_run_history_timeframe_in_months

    def _fetch_workflows(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows'
        return self._fetch_from_paginated_counted_api(api_url, 'workflows')

    def fetch_data(self):
        workflows = self._fetch_workflows()
        automation_data = self._transform_api_response_to_data_format(self.enable_logs, workflows)
        self._export_as_json(automation_data, DataTypeFileNames.AUTOMATION_DATA_FILE_NAME)

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
            }
            if enable_logs:
                print(f'Workflow {wf_data["name"]} data added.')
            automation_data.append(data)
        return automation_data
