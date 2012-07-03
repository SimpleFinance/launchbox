import unittest
from mock import Mock, patch

from launchbox.client import S3CookbookRemote

def k(name):
    key = Mock()
    key.name = name
    return key

class TestS3CookbookRemote(unittest.TestCase):
    @patch('boto.connect_s3')
    def setUp(self, connect_s3):
        self.s3 = Mock()
        self.bucket = Mock()
        connect_s3.return_value = self.s3
        self.s3.get_bucket.return_value = self.bucket
        self.remote = S3CookbookRemote('foo', 'bar', 'baz')
        connect_s3.assert_called_once_with('foo', 'bar')
        self.s3.get_bucket.assert_called_once_with('baz')

    def test_key_joins_cookbooks_to_name_version_and_name_ext(self):
        ret = self.remote._key('foo', 'bar', '.baz')
        self.assertEqual('cookbooks/foo/bar/foo.baz', ret)

    def test_save_cookbook_to(self):
        f = Mock()
        key = self.patch_get_key()

        self.remote.save_cookbook_to(f, "baz", "1.0")

        self.bucket.get_key.assert_called_once_with('cookbooks/baz/1.0/baz.tar.gz')
        key.get_contents_to_file.assert_called_once_with(f)

    def test_save_cookbook_metadata_to(self):
        f = Mock()
        key = self.patch_get_key()

        self.remote.save_cookbook_metadata_to(f, "baz", "1.1")

        self.bucket.get_key.assert_called_once_with('cookbooks/baz/1.1/baz.json')
        key.get_contents_to_file.assert_called_once_with(f)

    @patch('json.dump')
    def test_save_cookbook_versions_to(self, p_json_dump):
        f = Mock()
        get_all_keys = Mock()
        self.bucket.get_all_keys = get_all_keys
        get_all_keys.return_value = [k('cookbooks/foobar/1.0/foobar.tgz'),
                                     k('cookbooks/foobar/1.0/foobar.json'),
                                     k('cookbooks/foobar/1.1/foobar.tgz'),
                                     k('cookbooks/foobar/1.1/foobar.json')]

        self.remote.save_cookbook_versions_to(f, 'foobar')

        get_all_keys.assert_called_once_with(prefix='cookbooks/foobar')
        p_json_dump.assert_called_once_with(['1.0', '1.1'], f)

    def patch_get_key(self):
        key = Mock()
        self.bucket.get_key.return_value = key
        return key
