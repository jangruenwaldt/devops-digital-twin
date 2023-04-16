from features.cockpit.cockpit import Cockpit

import unittest

from utils.neo4j import Neo4j


class IntegrationTest(unittest.TestCase):

    def test_smoke(self):
        Cockpit.construct_digital_twin(repo_url='https://github.com/jangruenwaldt/xss-escape-django',
                                       release_branch_name='master', debug_options={'enable_logs': True}, wipe_db=True)
        self.assertEqual(Neo4j.count_nodes(), 13)


if __name__ == '__main__':
    unittest.main()
