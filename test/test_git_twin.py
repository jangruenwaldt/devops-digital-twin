import unittest
from unittest.mock import MagicMock, patch

from features.twins.git_twin import GitTwin
from utils.graph.graph_relationships import GraphRelationships


class TestGitTwin(unittest.TestCase):

    @patch('features.twins.git_twin.Repo')
    @patch('features.twins.git_twin.Neo4j.get_graph')
    @patch('features.twins.git_twin.Relationship')
    def test_construct_from_repo_path(self, _mock_relationship, mock_get_graph, mock_git_repo):
        # Mock the git repository
        commit_1 = MagicMock(hexsha='sha_commit1', message='Commit 1', committed_datetime='2022-01-01', parents=[])
        commit_2 = MagicMock(hexsha='sha_commit2', message='Commit 2', committed_datetime='2023-01-01',
                             parents=[commit_1])
        mock_git_repo_instance = MagicMock()
        mock_git_repo_instance.iter_commits.return_value = [commit_1, commit_2]
        mock_git_repo.return_value = mock_git_repo_instance

        # Mock the neo4j graph
        mock_graph = MagicMock()
        mock_graph.nodes.match.return_value.first.side_effect = [None, None, commit_1]
        mock_get_graph.return_value = mock_graph

        GitTwin.construct_from_repo_path('example/path', 'main',
                                         repo_url='https://github.com/jangruenwaldt/xss-escape-django',
                                         debug_options={'enable_logs': True})

        mock_git_repo.assert_called_with('example/path')
        mock_git_repo_instance.git.checkout.assert_called_with('main')
        mock_git_repo_instance.remotes.origin.pull.assert_called_once()

        self.assertEqual(mock_graph.create.call_count, 3)  # 2 nodes and 1 relationship

        # Check commit 1 node for right values
        commit_1_node = mock_graph.create.call_args_list[0].args[0]
        self.assertEqual(commit_1_node['message'], 'Commit 1')
        self.assertEqual(commit_1_node['hash'], 'sha_commit1')
        self.assertEqual(commit_1_node['date'], '2022-01-01')
        self.assertEqual(commit_1_node['branch'], 'main')
        self.assertEqual(commit_1_node['url'], 'https://github.com/jangruenwaldt/xss-escape-django/commit/sha_commit1')

        relationship = mock_graph.create.call_args_list[2]
        relationship.assert_called_once_with(commit_1, GraphRelationships.PARENT, commit_2)


if __name__ == '__main__':
    unittest.main()
