from apscheduler.schedulers.blocking import BlockingScheduler

from features.data_adapters.data_adapters import *
from utils.config import Config


def update_data():
    commit_data_source = Config.get_commit_data_source()
    deployment_data_source = Config.get_deployment_data_source()
    project_management_data_source = Config.get_project_management_data_source()
    automations_data_source = Config.get_automations_data_source()
    automations_history_data_source = Config.get_automations_history_data_source()

    CommitDataAdapter.fetch_data(commit_data_source, branch=Config.get_main_branch())
    DeploymentDataAdapter.fetch_data(deployment_data_source)
    ProjectManagementDataAdapter.fetch_data(project_management_data_source)
    AutomationDataAdapter.fetch_data(automations_data_source)
    AutomationHistoryDataAdapter.fetch_data(automations_history_data_source)


scheduler = BlockingScheduler()
scheduler.add_job(update_data, 'interval', hours=Config.get_update_interval_in_hours())
scheduler.start()
