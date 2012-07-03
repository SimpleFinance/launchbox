import tempfile
import unittest
from mock import Mock, patch

from launchbox.client import CookbookClient

class TestClient(unittest.TestCase):
    def setUp(self):
        self.delegate = Mock()
        self.download_cache = '/foo/bar'
        self.client = CookbookClient(self.download_cache, self.delegate)

    def test_path_returns_download_cache_path(self):
        self.assertEqual("/foo/bar/baz/1.0.0/baz.json",
                         self.client._path('baz', '1.0.0', '.json'))

    @patch('launchbox.osutils.mkdirp')
    @patch('os.path.isfile')
    @patch('__builtin__.open')
    def test_dinf_calls_method_if_cache_is_not_found(self, p_open, isfile, mkdirp):
        path = '/foo/bar/baz'
        method = Mock()
        isfile.return_value = False
        f = tempfile.TemporaryFile()
        p_open.return_value = f
        self.client.download_if_not_found(path, method, [], {})
        method.assert_called_once_with(f, [], {})


    @patch('os.path.isfile')
    def test_dinf_does_not_call_method_if_found(self, isfile):
        path = '/foo/bar/baz'
        method = Mock()
        method.side_effect = Exception("Not supposed to be called")
        isfile.return_value = True
        ret = self.client.download_if_not_found(path, method, [], {})
        self.assertEqual(path, ret)

    def test_get_cookbook_downloads_targz(self):
        client = self.mock_client_methods()
        client._path.return_value = '/foo/bar/baz'

        save_cookbook_to = Mock()
        self.delegate.save_cookbook_to = save_cookbook_to

        client.get_cookbook('baz', '1.0')

        client._path.assert_called_once_with('baz', '1.0', '.tar.gz')
        client.download_if_not_found.assert_called_once_with('/foo/bar/baz',
                                                             save_cookbook_to,
                                                             'baz',
                                                             '1.0')
    @patch('json.load')
    @patch('__builtin__.open')
    def test_get_cookbook_metadata_downloads_json(self, p_open, p_json_load):
        client = self.mock_client_methods()
        client._path.return_value = '/foo/bar/baz'

        save_cookbook_metadata_to = Mock()
        self.delegate.save_cookbook_metadata_to = save_cookbook_metadata_to

        client.get_cookbook_metadata('baz', '2.0')

        client._path.assert_called_once_with('baz', '2.0', '.json')
        client.download_if_not_found.assert_called_once_with('/foo/bar/baz',
                                                             save_cookbook_metadata_to,
                                                             'baz',
                                                             '2.0')

    @patch('json.load')
    @patch('__builtin__.open')
    def test_get_cookbook_versions_downloads_versions_json(self, p_open, p_json_load):
        client = self.mock_client_methods()

        save_cookbook_versions_to = Mock()
        self.delegate.save_cookbook_versions_to = save_cookbook_versions_to

        client.get_cookbook_versions('baz')

        path = self.download_cache + '/baz/versions.json'
        client.download_if_not_found.assert_called_once_with(path,
                                                             save_cookbook_versions_to,
                                                             'baz')

    def mock_client_methods(self):
        self.client._path = Mock()
        self.client.download_if_not_found = Mock()
        return self.client
