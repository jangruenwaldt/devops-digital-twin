from features.cockpit.cockpit import Cockpit

print('MTTR:')
print(Cockpit.calculate_dora_mean_time_to_recover(filter_issues='WHERE label.name IN ["bug"]'))
print('')
print('Change Failure Rate:')
print(Cockpit.calculate_dora_change_failure_rate(filter_issues='WHERE label.name IN ["bug"]'))
print('')
print('Deployment frequency (time between releases):')
print(Cockpit.calculate_dora_deployment_frequency())
print('')
print('Lead time:')
print(Cockpit.calculate_dora_lead_time())

# On some projects, if releases are only used after a certain time, use excluded tags to exclude from the average
# print(Cockpit.calculate_dora_lead_time(excluded_tags=['0.18.0']))

# Cockpit.construct_digital_twin(repo_url='https://github.com/jangruenwaldt/xss-escape-django',
#                                release_branch_name='master', debug_options={'enable_logs': True}, wipe_db=True)

# Cockpit.construct_digital_twin(repo_url='https://github.com/microsoft/PowerToys',
#                               release_branch_name='main', debug_options={'enable_logs': True}, wipe_db=True)
