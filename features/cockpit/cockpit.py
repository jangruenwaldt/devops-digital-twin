from features.twins.git_twin import GitTwin
from features.twins.releases_twin import ReleasesTwin
from utils.neo4j import Neo4j


# The cockpit of a digital twin is a layer above the data itself, it usually includes a user interface, for now
# it is just code that works on twin data.
class Cockpit:
    @staticmethod
    def calculate_average_lead_time():
        # TODO
        return 0

    @staticmethod
    def construct_digital_twin(repo_url, release_branch_name, debug_options=None, wipe_db=True):
        if wipe_db:
            Neo4j.wipe_database()

        GitTwin.construct_from_github_url(repo_url, branch_name=release_branch_name, debug_options=debug_options)
        ReleasesTwin.construct(repo_url, debug_options=debug_options)
