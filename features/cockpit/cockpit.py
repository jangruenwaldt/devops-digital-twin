import statistics
from datetime import timedelta

from features.twins.git_twin import GitTwin
from features.twins.deployments_twin import DeploymentsTwin
from utils.neo4j import Neo4j


# The cockpit of a digital twin is a layer above the data itself, it usually includes a user interface, for now
# it is just code that works on twin data.
class Cockpit:
    @staticmethod
    def calculate_lead_time_from_commit_to_deployment(commit_hash, deployment_tag):
        return Neo4j.get_graph().run(f"""
        MATCH (deployment:Deployment {{tag_name: '{deployment_tag}'}}), 
        (commit:Commit {{hash: '{commit_hash}'}})
        RETURN duration.between(datetime(deployment.published_at), datetime(commit.date))
        """).evaluate()

    @staticmethod
    def calculate_lead_time(deployment_tag=None):
        filter_deployment = ''
        if deployment_tag is not None:
            filter_deployment = f" {{tag_name: '{deployment_tag}'}}"

        duration_list = Neo4j.get_graph().run(f"""
        MATCH (deployment:Deployment {filter_deployment})
        MATCH (deployment)-[:INITIAL_DEPLOY]->(deployed_commit:Commit)
        WITH duration.inSeconds(datetime(deployed_commit.date), datetime(deployment.published_at)) as lead_time
        RETURN lead_time
        """).data()

        seconds_array = list(map(lambda d: d['lead_time'].seconds, duration_list))
        lead_time_in_s = statistics.mean(seconds_array)
        return timedelta(seconds=lead_time_in_s)

    @staticmethod
    def construct_digital_twin(repo_url, release_branch_name, debug_options=None, wipe_db=True):
        if wipe_db:
            Neo4j.wipe_database()

        GitTwin.construct_from_github_url(repo_url, branch_name=release_branch_name, debug_options=debug_options)
        DeploymentsTwin.construct(repo_url, debug_options=debug_options)
        Cockpit.print_usage_info()

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
@              match (n:Release) return n             @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View relationships between releases and commits:    @
@                                                     @
@ MATCH (n)-[:LATEST_INCLUDED_COMMIT]->(l)            @
@ RETURN n, l                                         @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""")
