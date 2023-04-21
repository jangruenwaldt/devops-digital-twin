import statistics
from datetime import timedelta, datetime
from typing import Callable

from features.twins.deployments_twin import DeploymentsTwin
from features.twins.git_twin import GitTwin
from features.twins.project_management_twin import ProjectManagementTwin
from utils.neo4j import Neo4j


# The cockpit of a digital twin is a layer above the data itself, it usually includes a user interface, for now
# it is just code that works on twin data.
class Cockpit:

    @staticmethod
    def get_deployments(from_date=None, to_date=None):
        date_filter = ''
        if from_date is not None or to_date is not None:
            date_filter += 'WHERE '
            if from_date is not None:
                date_filter += f'datetime(deployment.published_at) >= datetime("{from_date.isoformat()}")'
            if to_date is not None:
                if from_date is not None:
                    date_filter += ' AND '
                date_filter += f'datetime(deployment.published_at) <= datetime("{to_date.isoformat()}")'

        query = f"""
            MATCH (deployment:Deployment)
            {date_filter}
            RETURN deployment.tag_name as tag_name, deployment.published_at as published_at, deployment.id as id
            """
        releases = Neo4j.get_graph().run(query).data()
        return sorted(releases, key=lambda r: datetime.fromisoformat(r['published_at']))

    @staticmethod
    def calculate_dora_deployment_frequency(from_date=None, to_date=None):
        """
        Deployment frequency: how often code is deployed
        [Source: https://www.researchgate.net/publication/318018911_DORA_Platform_DevOps_Assessment_and_Benchmarking]
        :return: the average time between deployments
        """
        deployment_dates = Cockpit.get_deployments(from_date=from_date, to_date=to_date)

        if len(deployment_dates) <= 1:
            raise Exception('Not enough data to calculate deployment frequency.')

        parsed_dates = list(map(lambda x: datetime.fromisoformat(x['published_at']), deployment_dates))
        time_between_releases = [parsed_dates[i] - parsed_dates[i - 1] for i in range(1, len(parsed_dates))]

        return sum(time_between_releases, timedelta()) / (len(time_between_releases))

    @staticmethod
    def calculate_dora_lead_time(deployment_tag=None, excluded_tags=None):
        """
        Lead time: how long it takes an organization to go from code commit to code successfully running
        in production or in a releasable state.
        [Source: https://www.researchgate.net/publication/318018911_DORA_Platform_DevOps_Assessment_and_Benchmarking]
        :param deployment_tag:
        :param excluded_tags: deployments that should be excluded (possibly due to outliers)
        :return:
        """
        filter_deployment = ''
        if deployment_tag is not None:
            filter_deployment = f" {{tag_name: '{deployment_tag}'}}"

        filter_tags = ''
        if excluded_tags is not None:
            excluded_tag_string = ','.join(list(map(lambda s: f"'{s}'", excluded_tags)))
            filter_tags = f" WHERE NOT deployment.tag_name IN [{excluded_tag_string}]"

        query = f"""
        MATCH (deployment:Deployment {filter_deployment})-[:INITIAL_DEPLOY]->(deployed_commit:Commit)
        {filter_tags}
        WITH duration.inSeconds(datetime(deployed_commit.date), datetime(deployment.published_at)) as lead_time
        RETURN lead_time
        """
        duration_list = Neo4j.get_graph().run(query).data()

        seconds_array = list(map(lambda d: d['lead_time'].seconds, duration_list))
        lead_time_in_s = statistics.mean(seconds_array) if len(seconds_array) > 0 else 0
        return timedelta(seconds=lead_time_in_s)

    @staticmethod
    def calculate_dora_change_failure_rate(filter_issues):
        """
        Change failure rate (CFR): the percentage of changes that result in degraded service or subsequently require
        remediation (e.g., lead to service impairment, service outage, require a hotfix, fix forward, patch).
        [Source: https://www.researchgate.net/publication/318018911_DORA_Platform_DevOps_Assessment_and_Benchmarking]

        :returns CFR for the given timerange, calculated as: |deployments that had an incident| / |all deployments|
        A deployment with an incident is defined as
        """
        query = f"""
        MATCH (issue:Issue)-[:HAS_LABEL]-(label:IssueLabel)
        {filter_issues}
        RETURN issue
        """
        issues = [d['issue'] for d in Neo4j.get_graph().run(query).data()]
        deployments = [{'date': datetime.fromisoformat(d['published_at']), 'id': d['id']} for d in
                       Cockpit.get_deployments()]

        deployments_with_incident = set()
        for issue in issues:
            created_date = datetime.fromisoformat(issue['created_at'])
            latest_deploy_before_incident = next(
                (d[idx - 1] if idx > 0 else None for idx, d in enumerate(deployments) if
                 d['date'] > created_date), None)
            if latest_deploy_before_incident is not None:
                deployments_with_incident.add(latest_deploy_before_incident['id'])
            # It may be the case the latest deployment happened before the issue was created, which we miss in the
            # previous expression as we find the first deployment that is larger and then go back one step.
            elif deployments[-1]['date'] <= created_date:
                deployments_with_incident.add(deployments[-1]['id'])
        return len(deployments_with_incident) / len(deployments)

    @staticmethod
    def calculate_dora_mean_time_to_restore_service(from_date=None, to_date=None):
        """
        MTTR: how long it generally takes to restore service when a service incident occurs
        (e.g., unplanned outage, service impairment)
        [Source: https://www.researchgate.net/publication/318018911_DORA_Platform_DevOps_Assessment_and_Benchmarking]
        """
        return timedelta(seconds=152)

    @staticmethod
    def construct_digital_twin(repo_url, release_branch_name, debug_options=None, wipe_db=True):
        if wipe_db:
            Neo4j.wipe_database()

        GitTwin.construct_from_github_url(repo_url, branch_name=release_branch_name, debug_options=debug_options)
        DeploymentsTwin.construct(repo_url, debug_options=debug_options)
        ProjectManagementTwin.construct(repo_url, debug_options=debug_options)
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
@            match (n:Deployment) return n            @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ View relationships between releases and commits:    @
@                                                     @
@ MATCH (n)-[:LATEST_INCLUDED_COMMIT]->(l)            @
@ RETURN n, l                                         @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""")
