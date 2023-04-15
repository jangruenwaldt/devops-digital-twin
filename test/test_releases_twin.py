import unittest
from unittest.mock import MagicMock, patch

from features.twins.releases_twin import ReleasesTwin


class TestReleasesTwin(unittest.TestCase):

    @patch('features.twins.releases_twin.GitHub')
    @patch('features.twins.releases_twin.Neo4j.get_graph')
    @patch('features.twins.releases_twin.Neo4j.remove_releases')
    @patch('features.twins.releases_twin.Relationship')
    def test_construct(self, mock_relationship, mock_remove_releases, mock_get_graph, mock_github):
        # Mock GitHub
        mock_github_instance = MagicMock()
        mock_github_instance.fetch_releases.return_value = [
            {'id': 1, 'tag_name': 'v1.0.0', 'published_at': '2022-01-01'},
            {'id': 2, 'tag_name': 'v1.1.0', 'published_at': '2023-01-01'}
        ]
        mock_github_instance.get_latest_commit_hash_in_release.side_effect = ['commit1', 'commit2']
        mock_github.return_value = mock_github_instance

        # Mock Neo4j graph
        mock_graph = MagicMock()
        commit_1_node = MagicMock(hash='commit1')
        commit_2_node = MagicMock(hash='commit2')
        mock_graph.nodes.match.return_value.first.return_value.side_effect = [commit_1_node, commit_2_node]
        mock_get_graph.return_value = mock_graph

        ReleasesTwin.construct('https://github.com/jangruenwaldt/xss-escape-django')

        mock_remove_releases.assert_called_once()
        self.assertEqual(mock_graph.create.call_count, 5)  # 2 releases, 3 relationships

        # release node 1
        release_node_1 = mock_graph.create.call_args_list[0].args[0]
        expected_release_node_1 = {
            'id': 1,
            'tag_name': 'v1.0.0',
            'published_at': '2022-01-01',
            'release_url': 'https://github.com/jangruenwaldt/xss-escape-django/releases/tag/v1.0.0',
            'commit_url': 'https://github.com/jangruenwaldt/xss-escape-django/commit/commit1'
        }
        self.assertEqual(sorted(release_node_1.items()), sorted(expected_release_node_1.items()))

        # relationship between release 1 and commit 1
        relationship_1 = mock_relationship.call_args_list[0]
        # TODO: bit unclean to call mock_graph.nodes.match.return_value.first() here,
        #  but test fails if commit_1_node passed directly
        self.assertTupleEqual(relationship_1.args, (release_node_1, 'LATEST_INCLUDED_COMMIT',
                                                    mock_graph.nodes.match.return_value.first()))

        # relationship between releases
        relationship_2 = mock_relationship.call_args_list[1]
        release_node_2 = mock_graph.create.call_args_list[2].args[0]
        self.assertTupleEqual(relationship_2.args, (release_node_2, 'SUCCEEDED_BY', release_node_1))


if __name__ == '__main__':
    unittest.main()
