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
