from features.twins.git_twin import GitTwin
from features.twins.releases_twin import ReleasesTwin
from utils.neo4j import Neo4j

# This is a small sample repository so the twin can be built fast.
repo_url = 'https://github.com/jangruenwaldt/xss-escape-django'
release_branch_name = 'master'

debug_options = {'enable_logs': True}
Neo4j.wipe_database()
GitTwin.construct_from_github_url(repo_url, branch_name=release_branch_name, debug_options=debug_options)
ReleasesTwin.construct(repo_url, debug_options=debug_options)
