from datetime import datetime

from dateutil.relativedelta import relativedelta

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.constants.twin_constants import TwinConstants


class GitHubAutomationHistoryDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url, automation_run_history_timeframe_in_months=6):
        super().__init__(repo_url)
        self.automation_run_history_timeframe_in_months = automation_run_history_timeframe_in_months

    def _fetch_workflows(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows'

        return self._fetch_from_paginated_counted_api(api_url, 'workflows')

    def _fetch_automation_runs(self):
        workflows = self._fetch_workflows()
        automation_history = []
        for wf_data in workflows:
            earliest_valid_date = (datetime.now() - relativedelta(
                months=self.automation_run_history_timeframe_in_months)).isoformat()

            api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows/{wf_data["id"]}/runs' \
                      f'?per_page=100&created=>{earliest_valid_date}'

            workflow_runs = self._fetch_from_paginated_counted_api(api_url, 'workflow_runs')
            data = list(map(self._github_run_history_to_data_model, workflow_runs))

            automation_history.extend(data)

        return automation_history

    @staticmethod
    def _github_run_history_to_data_model(data):
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

    def fetch_data(self, debug_options=None):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        automation_runs = self._fetch_automation_runs()

        if enable_logs:
            print(f'Fetched {len(automation_runs)} automation runs')

        self._export_as_json(automation_runs, TwinConstants.AUTOMATION_HISTORY_FILE_NAME)
