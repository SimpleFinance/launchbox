import unittest
from mock import Mock, patch, call

from launchbox.client import HttpCookbookRemote

class TestHttpCookbookRemote(unittest.TestCase):

    def setUp(self):
        self.base = 'http://example.com/cookbooks'
        self.remote = HttpCookbookRemote(self.base)

    def u(self, path):
        return self.base + path

    @patch('requests.get')
    def test_downloading_a_url_to_file(self, p_get):
        url = self.u('/foo/bar/baz')
        response = Mock()
        f = Mock()

        p_get.return_value = response
        response.ok = True
        response.iter_content = lambda : ['foo', 'bar', 'baz']

        self.remote._download(url, f)

        p_get.assert_called_once_with(url)
        f.write.assert_has_calls([call('foo'), call('bar'), call('baz')])

    def test_url(self):
        url = self.remote._url('foo', '1.0', '.tar.gz')
        self.assertEqual(url, self.base + '/foo/1.0/foo.tar.gz')

    def test_save_cookbook_to(self):
        url = self.patch_internal_methods()
        f = Mock()

        self.remote.save_cookbook_to(f, 'foo', '1.0')

        self.remote._url.assert_called_once_with('foo', '1.0', '.tar.gz')
        self.remote._download.assert_called_once_with(url, f)

    def test_save_cookbook_metadata_to(self):
        url = self.patch_internal_methods()
        f = Mock()

        self.remote.save_cookbook_metadata_to(f, 'bar', '1.1')

        self.remote._url.assert_called_once_with('bar', '1.1', '.json')
        self.remote._download.assert_called_once_with(url, f)


    def test_save_cookbook_versions_to(self):
        self.patch_internal_methods()
        url = self.base + '/baz/versions.json'
        f = Mock()

        self.remote.save_cookbook_versions_to(f, 'baz')
        self.remote._download.assert_called_once_with(url, f)

    def patch_internal_methods(self):
        self.remote._url = Mock()
        self.remote._download = Mock()
        url = Mock()
        self.remote._url.return_value = url
        return url
