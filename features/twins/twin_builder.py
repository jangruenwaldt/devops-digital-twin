import os

from features.twins.deployments_twin import DeploymentsTwin
from features.twins.git_twin import GitTwin
from features.twins.project_management_twin import ProjectManagementTwin
from utils.github_utils import GitHubUtils
from utils.neo4j import Neo4j
from utils.constants.twin_constants import TwinConstants


class TwinBuilder:

    @staticmethod
    def construct_from_github_data_repo(repo_url, debug_options=None, wipe_db=False):
        if debug_options is None:
            debug_options = {}
        enable_logs = 'enable_logs' in debug_options and debug_options['enable_logs']

        if wipe_db:
            Neo4j.wipe_database()
            if enable_logs:
                print(f'Wiped DB')

        raw_file_link = os.path.join(GitHubUtils.get_raw_file_link(repo_url), TwinConstants.DATA_EXPORT_DIR)

        commit_data = os.path.join(raw_file_link, TwinConstants.COMMIT_DATA_FILE_NAME)
        deployment_data = os.path.join(raw_file_link, TwinConstants.DEPLOYMENT_DATA_FILE_NAME)
        issue_data = os.path.join(raw_file_link, TwinConstants.ISSUES_DATA_FILE_NAME)
        if enable_logs:
            print(f'Building twin from data source in {repo_url} using the following '
                  f'files:\n{commit_data}\n{deployment_data}\n{issue_data}')

        GitTwin.construct_from_json(commit_data)
        DeploymentsTwin.construct_from_json(deployment_data)
        ProjectManagementTwin.construct_from_json(issue_data)
        TwinBuilder.print_usage_info()

    @staticmethod
    def print_usage_info():
        print(""""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@    DONE CONSTRUCTING TWIN    @@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        
Time to explore! Visit the graph at https://www.yworks.com/neo4j-explorer/
You might be interested in some queries:

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View everything (not recommended for > 1000 nodes): @
@                                                     @
@                 match (n) return n                  @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View releases:                                      @
@                                                     @
@            match (n:Deployment) return n            @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View relationships between releases and commits:    @
@                                                     @
@ MATCH (n)-[:LATEST_INCLUDED_COMMIT]->(l)            @
@ RETURN n, l                                         @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""")
