import unittest
from unittest.mock import MagicMock, patch

from features.github.github import GitHub


class TestGitHub(unittest.TestCase):

    def setUp(self):
        self.github = GitHub('https://github.com/jangruenwaldt/xss-escape-django')

    @patch('features.github.github.requests.get')
    @patch('features.github.github.Cache.load')
    @patch('features.github.github.Cache.update')
    def test_fetch_releases(self, mock_cache_update, mock_cache_load, mock_get):
        example_release = {
            "url": "https://api.github.com/repos/microsoft/PowerToys/releases/assets/16568816",
            "id": 16568816,
            "node_id": "MDEyOlJlbGVhc2VBc3NldDE2NTY4ODE2",
            "name": "PowerToysSymbols.v0.11.0.zip",
            "label": None,
            "uploader": {
                "login": "enricogior",
                "id": 3206696,
            },
            "content_type": "application/x-zip-compressed",
            "state": "uploaded",
            "size": 23242119,
            "download_count": 9155,
            "created_at": "2019-12-03T17:04:00Z",
            "updated_at": "2019-12-03T17:04:06Z",
            "browser_download_url": "https://github.com/microsoft/PowerToys/releases/download/v0.11.0/PowerToysSymbols.v0.11.0.zip"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = [example_release]
        mock_get.return_value = mock_response

        mock_cache_load.return_value = None
        mock_cache_update.return_value = None

        releases = self.github.fetch_releases()
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0], example_release)

    def test_get_owner_and_repo_name(self):
        owner, repo_name = self.github.get_owner_and_repo_name()
        self.assertEqual(owner, 'jangruenwaldt')
        self.assertEqual(repo_name, 'xss-escape-django')

    @patch('features.github.github.CachedRequest.get_json')
    def test_get_latest_commit_hash_in_release(self, mock_get_json):
        mock_get_json.return_value = {
            'object': {
                'sha': '123'
            }
        }

        commit_hash = self.github.get_latest_commit_hash_in_release('v1.0.1')
        self.assertEqual(commit_hash, '123')


if __name__ == '__main__':
    unittest.main()
