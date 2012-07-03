import tempfile
import unittest
from mock import Mock, patch, call

from launchbox.cookbooks import download_cookbooks, extract, package

class TestCookbooks(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.cookbooks = {'foo': dict(version='1.0'),
                          'bar': dict(version='2.1')}

    def test_download_cookbooks_retrives_cookbook_versions_from_client(self):
        download_cookbooks(self.client, self.cookbooks)
        self.client.get_cookbook.assert_has_calls([call('foo', '1.0'),
                                                   call('bar', '2.1')],
                                                  any_order=True)

    def test_download_cookbooks_returns_list_of_files(self):
        self.client.get_cookbook.side_effect = [1, 2]
        files = download_cookbooks(self.client, self.cookbooks)
        self.assertEqual([1,2], files)

    @patch('tarfile.TarFile.gzopen')
    @patch('tempfile.mkdtemp')
    def test_extracts_into_temporary_directory(self, mkdtemp, gzopen):
        tmpdir = '/foo/bar/baz'; mkdtemp.return_value = tmpdir
        paths = ['/foo', '/bar/baz']

        ret = extract(paths)

        gzopen.assert_has_calls([call(paths[0]),
                                 call().extractall(path=tmpdir),
                                 call(paths[1]),
                                 call().extractall(path=tmpdir)])
        self.assertEqual(ret, tmpdir)

    @patch('tarfile.TarFile.gzopen')
    @patch('shutil.rmtree')
    def test_package_creates_tarfile_of_cookbooks(self, rmtree, gzopen):
        bundle = Mock()

        context = Mock()
        context.__enter__ = Mock(return_value = bundle)
        context.__exit__ = Mock(return_value = False)

        gzopen.return_value = context

        bundlepath = '/foo/bar/baz/bundles'
        cookbookdir = '/foo/bar/baz'

        ret = package(cookbookdir, bundlepath)

        gzopen.assert_called_once_with(bundlepath, mode='w')
        bundle.add.assert_called_once_with(cookbookdir, arcname='cookbooks')
        rmtree.assert_called_once_with(cookbookdir)
        self.assertEqual(ret, bundlepath)
