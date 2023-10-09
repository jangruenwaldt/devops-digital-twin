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
            print(f'Found {len(cached_data)} workflows in cache for workflow "{wf["name"]}",'
                  f'latest one at: {latest_workflow_run}')

            fetch_limit_changed = DataManager.retrieve_by_key(
                'automation_history_fetched_since') != Config.get_automation_history_since()
            if fetch_limit_changed:
                print('Fetch limit changed since last time, re-fetching all workflows from fetch limit to now.')
                print(
                    f'Was before: {DataManager.retrieve_by_key("automation_history_fetched_since")},'
                    f' is now: {Config.get_automation_history_since()}')
            else:
                print(f'Fetch limit unchanged: {Config.get_automation_history_since()}. Fetching only workflows'
                      f'after {latest_workflow_run}, as all previous already fetched.')
                api_url_without_query_param = api_url.split('?')[0]
                api_url = api_url_without_query_param + f'?created>={latest_workflow_run}'

            newly_fetched_data = self._fetch_from_workflow_history_api(api_url)

            if self.enable_logs:
                print(
                    f'Fetched {len(newly_fetched_data)} workflow runs from GitHub API.')
                if fetch_limit_changed:
                    print(f'Previously: {len(cached_data)} workflow runs in cache (but fetch limit changed).')
                else:
                    print(f'Now merging with {len(cached_data)} workflow runs in cache.')
            return self._merge_data(cached_data, newly_fetched_data, merge_key='id')
        else:
            print(f'Found no existing data in cache for workflow "{wf["name"]}", fetching from scratch.')
            data = self._fetch_from_workflow_history_api(api_url)
            if self.enable_logs:
                print(f'Fetched {len(data)} workflow runs from GitHub API')
            return data

    def _fetch_from_workflow_history_api(self, api_url):
        # Unfortunately, GitHub API only gives us the first 10 pages. Page 11 will be empty. Therefore, once page 10
        # is reached, we have to adjust our fetching URL to filter by created earlier than the last run that was
        # returned to us.
        newly_fetched_data = []
        while True:
            data = self._fetch_from_paginated_counted_api(api_url, 'workflow_runs')
            newly_fetched_data.extend(data)

            # Perfect 1000 results most likely means page limit was reached, even if not, no problem.
            if (len(newly_fetched_data) % 1000) == 0 and len(data) != 0:
                oldest_el = newly_fetched_data[-1]['run_started_at']
                api_url_without_query_param = api_url.split('?')[0]
                api_url = api_url_without_query_param + f'?created={Config.get_automation_history_since()}..{oldest_el}'
            else:
                break
        return newly_fetched_data

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
        print(f'API returned {len(raw_automation_history)} automation runs. Mapping and storing in JSON now.')

        automation_history = list(map(self._transform_api_response_to_data_format, raw_automation_history))
        DataManager.store_twin_data(DataTypes.AUTOMATION_HISTORY, self.owner, self.repo_name, automation_history)
