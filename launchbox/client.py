import os
from os.path import dirname
import json

import boto
import requests

from launchbox.osutils import mkdirp
from launchbox.errors import *
from launchbox.output import log

def urljoin(*args):
    ret = args[0]
    for arg in args[1:]:
        if ret.endswith('/') and arg.startswith('/'):
            ret += arg[1:]
        elif not (ret.endswith('/') or arg.startswith('/')):
            ret = ret + '/' + arg
        else:
            ret += arg
    return ret

class CookbookClient(object):
    def __init__(self, download_cache, delegate):
        """ A delegate must implement the methods specified in
        CookbookClientRemoteDelegate """

        self.delegate = delegate
        self.download_cache = download_cache

    def _path(self, name, version, ext):
        return urljoin(self.download_cache, name, version, name + ext)

    def download_if_not_found(self, download_path, method, *args, **kw):
        if not os.path.isfile(download_path):
            mkdirp(dirname(download_path))
            with open(download_path, 'w') as f:
                try:
                    method(f, *args, **kw)
                except Exception as e:
                    f.close()
                    os.remove(download_path)
                    raise e
        return download_path

    def get_cookbook(self, name, version):
        """ returns the filename from where the cookbook can be read
        as a .tar.gz """
        path = self._path(name, version, '.tar.gz')
        return self.download_if_not_found(path, self.delegate.save_cookbook_to, name, version)

    def get_cookbook_metadata(self, name, version):
        """ returns the cookbook metadata """
        path = self._path(name, version, '.json')
        if self.download_if_not_found(path, self.delegate.save_cookbook_metadata_to, name, version):
            with open(path, 'r') as f:
                return json.load(f)

    def get_cookbook_versions(self, name):
        """ returns the list of available versions for this cookbook
        """
        path = urljoin(self.download_cache, name, 'versions.json')
        if self.download_if_not_found(path, self.delegate.save_cookbook_versions_to, name):
            with open(path, 'r') as f:
                return json.load(f)


class CookbookClientRemoteDelegate(object):
    """ this class pretends to be an interface in order to document
    the necessary methods """

    def save_cookbook_to(self, name, version, f):
        pass

    def save_cookbook_metadata_to(self, name, version, f):
        pass

    def get_available_cookbooks_versions(self, name):
        pass


class S3CookbookRemote(CookbookClientRemoteDelegate):
    """ fetches cookbooks from an S3 bucket, stored as
        cookbooks/name/version/name.(tar.gz|json)"""

    def __init__(self, access_key, secret_key, bucket_name):
        self.s3 = boto.connect_s3(access_key, secret_key)
        self.bucket = self.s3.get_bucket(bucket_name)

    def _key(self, name, version, ext):
        return urljoin('cookbooks', name, version, name + ext)

    def save_cookbook_to(self, f, name, version):
        key = self.bucket.get_key(self._key(name, version, '.tar.gz'))
        if not key:
            raise CookbookTarballNotFoundError("Cannot find %s:%s" % (name, version))
        key.get_contents_to_file(f)

    def save_cookbook_metadata_to(self, f, name, version):
        key = self.bucket.get_key(self._key(name, version, '.json'))
        if not key:
            raise CookbookMetadataNotFoundError("no metadata for %s:%s" % (name, version))
        key.get_contents_to_file(f)

    def save_cookbook_versions_to(self, f, name):
        """ Lists all the keys in cookbooks/<name> and extracts the
        found versions.

        This is done in order to avoid needing a
        versions file in S3 which might be hard to update
        atomatically."""
        prefix = urljoin('cookbooks', name)
        versions = set()
        for key in self.bucket.get_all_keys(prefix=prefix):
            ver = key.name.split('/')[2]
            versions.add(ver)
        json.dump(sorted(versions), f)


class HttpCookbookRemote(CookbookClientRemoteDelegate):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def _download(self, url, f):
        response = requests.get(url)
        if not response.ok:
            raise RequestError("request for %s failed" % f)
        for chunk in response.iter_content():
            f.write(chunk)

    def _url(self, name, version, ext):
        return urljoin(self.base_uri, name, version, name + ext)

    def save_cookbook_to(self, f, name, version):
        self._download(self._url(name, version, '.tar.gz'), f)

    def save_cookbook_metadata_to(self, f, name, version):
        self._download(self._url(name, version, '.json'), f)

    def save_cookbook_versions_to(self, f, name):
        self._download(urljoin(self.base_uri, name, 'versions.json'), f)
