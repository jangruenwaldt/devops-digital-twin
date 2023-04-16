from features.cockpit.cockpit import Cockpit

print(Cockpit.calculate_lead_time(excluded_tags=['0.18.0']))

releases = Cockpit.get_all_releases()
for r in releases:
    print(r)
    print(Cockpit.calculate_lead_time(deployment_tag=r))
    print()

# Cockpit.construct_digital_twin(repo_url='https://github.com/microsoft/PowerToys',
#                               release_branch_name='main', debug_options={'enable_logs': True}, wipe_db=True)
