from features.data_adapters.github.github_automation_data_adapter import GitHubAutomationDataAdapter
from features.data_adapters.github.github_automation_history_data_adapter import GitHubAutomationHistoryDataAdapter
from features.data_adapters.github.github_commit_data_adapter import GitHubCommitDataAdapter
from features.data_adapters.github.github_deployment_data_adapter import GitHubDeploymentDataAdapter
from features.data_adapters.github.github_project_management_data_adapter import GitHubProjectManagementDataAdapter


class AutomationDataAdapter:

    @staticmethod
    def fetch_data(url):
        if url.startswith('https://github.com/'):
            return GitHubAutomationDataAdapter(url).fetch_data()
        else:
            raise Exception('Unsupported data source')


class AutomationHistoryDataAdapter:
    @staticmethod
    def fetch_data(url):
        if url.startswith('https://github.com/'):
            return GitHubAutomationHistoryDataAdapter(url).fetch_data()
        else:
            raise Exception('Unsupported data source')


class CommitDataAdapter:
    @staticmethod
    def fetch_data(url, branch='main'):
        if url.startswith('https://github.com/'):
            return GitHubCommitDataAdapter(url, branch).fetch_data()
        else:
            raise Exception('Unsupported data source')


class DeploymentDataAdapter:
    @staticmethod
    def fetch_data(url):
        if url.startswith('https://github.com/'):
            return GitHubDeploymentDataAdapter(url).fetch_data()
        else:
            raise Exception('Unsupported data source')


class ProjectManagementDataAdapter:
    @staticmethod
    def fetch_data(url):
        if url.startswith('https://github.com/'):
            return GitHubProjectManagementDataAdapter(url).fetch_data()
        else:
            raise Exception('Unsupported data source')
