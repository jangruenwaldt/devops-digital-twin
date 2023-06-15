import unittest
from datetime import datetime

from features.cockpit.cockpit import Cockpit
from features.twins.twin_builder import TwinBuilder
from utils.neo4j import Neo4j


class IntegrationTest(unittest.TestCase):

    def test_smoke(self):
        TwinBuilder.construct_from_github_data_repo('https://github.com/jangruenwaldt/twin-data-2',
                                                    twin_name='integration_test', wipe_db=True)
        self.assertEqual(Neo4j.count_nodes(), 27)

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
