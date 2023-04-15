from features.cockpit.cockpit import Cockpit

# Using a small sample repository so the twin can be built fast.
Cockpit.construct_digital_twin(repo_url='https://github.com/jangruenwaldt/xss-escape-django',
                               release_branch_name='master', debug_options={'enable_logs': True}, wipe_db=True)
