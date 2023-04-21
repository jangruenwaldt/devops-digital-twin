from datetime import datetime

import pytest

from features.cockpit.cockpit import Cockpit

import unittest

from utils.neo4j import Neo4j


class IntegrationTest(unittest.TestCase):

    def test_smoke(self):
        Cockpit.construct_digital_twin(repo_url='https://github.com/jangruenwaldt/xss-escape-django',
                                       release_branch_name='master', debug_options={'enable_logs': True}, wipe_db=True)
        self.assertEqual(Neo4j.count_nodes(), 19)

        lead_time = Cockpit.calculate_dora_lead_time()
        self.assertEqual(lead_time.days, 1216)

        lead_time = Cockpit.calculate_dora_deployment_frequency()
        self.assertEqual(lead_time.days, 3)

        lead_time = Cockpit.calculate_dora_deployment_frequency(from_date=datetime(2023, 4, 12),
                                                                to_date=datetime(2023, 4, 14))
        self.assertEqual(lead_time.days, 0)

        cfr = Cockpit.calculate_dora_change_failure_rate(from_date=datetime(2023, 4, 1),
                                                         to_date=datetime(2023, 4, 30),
                                                         filter_issues='WHERE label.name IN ["bug"]')
        self.assertEqual(round(cfr, 2), 0.67)

        cfr = Cockpit.calculate_dora_change_failure_rate(filter_issues='WHERE label.name IN ["bug"]')
        self.assertEqual(round(cfr, 2), 0.67)

        mttr = Cockpit.calculate_dora_mean_time_to_recover(from_date=datetime(2023, 4, 1),
                                                           to_date=datetime(2023, 4, 30),
                                                           filter_issues='WHERE label.name IN ["bug"]')
        self.assertEqual(mttr.total_seconds(), 65)

        mttr = Cockpit.calculate_dora_mean_time_to_recover(filter_issues='WHERE label.name IN ["bug"]')
        self.assertEqual(mttr.total_seconds(), 65)


if __name__ == '__main__':
    unittest.main()
