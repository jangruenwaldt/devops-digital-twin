from datetime import datetime

from features.data_adapters.github.github_data_fetcher import GitHubDataFetcher
from utils.constants.twin_constants import DataTypes, DataTypeFileNames
from utils.twin_data_retriever import TwinDataRetriever


class GitHubProjectManagementDataAdapter(GitHubDataFetcher):
    def __init__(self, repo_url):
        super().__init__(repo_url)

    def _fetch_issues(self):
        api_url = f'https://api.github.com/repos/{self.owner}/{self.repo_name}/issues?state=all'

        old_data = TwinDataRetriever.retrieve(DataTypes.ISSUES_DATA)
        if old_data is not None:
            # Get the latest edited issue in the old data
            latest_edited_issue = max(old_data, key=lambda x: x.get('updated_at', ''))
            since_date = latest_edited_issue.get('updated_at', '')

            # Send a new query with since parameter
            new_api_url = f'{api_url}&since={since_date}'
            new_data = self._fetch_from_paginated_api(new_api_url)

            # Combine the two into one data object
            combined_data = old_data + new_data
            return combined_data
        else:
            return self._fetch_from_paginated_api(api_url)

    def fetch_data(self):
        issues = self._fetch_issues()
        issue_data_list = self._transform_api_response_into_data_format(self.enable_logs, issues)
        self._export_as_json(issue_data_list, DataTypeFileNames.ISSUES_DATA_FILE_NAME)

    def _transform_api_response_into_data_format(self, enable_logs, issues):
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
        return issue_data_list
