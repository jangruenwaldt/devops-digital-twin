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

        cached_data = DataManager.retrieve_raw_api_data(DataTypes.AUTOMATION_HISTORY, DataSources.GITHUB, self.owner,
                                                        self.repo_name)
        raw_automation_history = []
        for wf in workflows:
            data = self._fetch_history_of_workflow(cached_data, wf)
            raw_automation_history.extend(data)
            # Store results here to not lose progress if it fails later.
            DataManager.store_raw_api_data(DataTypes.AUTOMATION_HISTORY, DataSources.GITHUB, self.owner, self.repo_name,
                                           raw_automation_history)

        if self.enable_logs:
            print(f'Total: {len(raw_automation_history)} automation runs')

        return raw_automation_history

    def _fetch_history_of_workflow(self, all_workflows_history_cache, wf):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/actions/workflows/{wf["id"]}/runs' \
                  f'?created=>{Config.get_automation_history_since()}'

        cached_data = []
        if all_workflows_history_cache is not None:
            cached_data = [el for el in all_workflows_history_cache if el['workflow_id'] == wf['id']]

        if cached_data is not None and len(cached_data) > 0:
            latest_workflow_run = max(cached_data, key=lambda x: x.get('updated_at', ''))

            fetch_limit_changed = DataManager.retrieve_by_key(
                'automation_history_fetched_since') != Config.get_automation_history_since()
            if fetch_limit_changed:
                print('Fetch limit changed since last time, re-fetching all workflows in relevant timeframe.')
                print(
                    f'Was before: {DataManager.retrieve_by_key("automation_history_fetched_since")},'
                    f' is now: {Config.get_automation_history_since()}')
            else:
                print(f'Fetch limit unchanged: {Config.get_automation_history_since()}')

            def check_if_existing_wf_reached(new_data):
                # Have to re-fetch all data as settings changed (would be possible to optimize by skipping existing)
                if fetch_limit_changed:
                    return False
                runs = new_data['workflow_runs']
                return latest_workflow_run['id'] in map(lambda x: x.get('id', ''), runs)

            newly_fetched_data = self._fetch_from_paginated_counted_api(api_url, 'workflow_runs',
                                                                        stopping_condition=check_if_existing_wf_reached)
            if self.enable_logs:
                print(
                    f'Fetched {len(newly_fetched_data)} workflow runs from GitHub API,'
                    f' found {len(cached_data)} workflow runs in cache.')
            return self._merge_data(cached_data, newly_fetched_data, merge_key='id')
        else:
            data = self._fetch_from_paginated_counted_api(api_url, 'workflow_runs')
            if self.enable_logs:
                print(f'Fetched {len(data)} workflow runs from GitHub API')
            return data

    @staticmethod
    def _transform_api_response_to_data_format(data):
        triggering_actor = data.get('triggering_actor', {})
        if triggering_actor is not None:
            started_by = triggering_actor.get('login', None)
        else:
            started_by = None
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
            'started_by': started_by,
            'run_attempt': data['run_attempt'],
        }

    def fetch_data(self):
        raw_automation_history = self._fetch_automation_runs()
        DataManager.store_raw_api_data(DataTypes.AUTOMATION_HISTORY, DataSources.GITHUB, self.owner, self.repo_name,
                                       raw_automation_history)
        DataManager.store_by_key('automation_history_fetched_since', Config.get_automation_history_since())

        automation_history = list(map(self._transform_api_response_to_data_format, raw_automation_history))
        DataManager.store_twin_data(DataTypes.AUTOMATION_HISTORY, self.owner, self.repo_name, automation_history)
