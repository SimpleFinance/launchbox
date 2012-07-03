from os.path import join, isfile, dirname
import shutil
import tarfile
import tempfile

import requests

from .errors import *
from .osutils import mkdirp
from .versions import highest_version_match

NOTFOUND = 'NOT FOUND'

def fill_in_dep_tree(tree, all_cookbook_versions, this_level, children, seen=None):
    if seen == None: seen = set()
    for cookbook in this_level:
        version = all_cookbook_versions[cookbook]['version']
        key = ':'.join([cookbook, version])
        if key in seen:
            tree[key] = 'CYCLE'
        else:
            seen.add(key)
        tree[key] = {}
        fill_in_dep_tree(tree[key], all_cookbook_versions, children[cookbook], children, seen)
        seen.remove(key)
    return tree

def resolve_dependencies(client, cookbooks, allow_not_found=False):
    files = []
    children = {}

    seen = dict()
    to_walk = cookbooks.items()

    i = 0
    while i < len(to_walk):
        cookbook, cdata = to_walk[i]; i += 1
        version = cdata['version']
        exclude = set(cdata.get('exclude', []))
        children[cookbook] = []
        seen[cookbook] = version
        if version == NOTFOUND:
            continue
        metadata = client.get_cookbook_metadata(cookbook, version)
        for dep, verspec in metadata['dependencies'].items():
            if dep in exclude:
                continue
            children[cookbook].append(dep)
            if dep in seen:
                continue
            versions = client.get_cookbook_versions(dep)
            match = highest_version_match(verspec, versions)
            if match:
                to_walk.append((dep, dict(version=match)))
            else:
                if allow_not_found:
                    to_walk.append((dep, dict(version=NOTFOUND)))
                else:
                    raise DependencyNotFoundError("Can't find cookbook matching %s %s" % (dep, verspec))

    resolved_dependencies = dict(to_walk)
    dep_tree = fill_in_dep_tree({}, resolved_dependencies, cookbooks.keys(), children)

    return resolved_dependencies, dep_tree

def download_cookbooks(client, cookbooks):
    files = []
    for cookbook, cdata in cookbooks.items():
        version = cdata['version']
        f = client.get_cookbook(cookbook, version)
        files.append(f)
    return files

def extract(paths):
    tmpdir = tempfile.mkdtemp()
    for path in paths:
        tar = tarfile.TarFile.gzopen(path)
        tar.extractall(path=tmpdir)
    return tmpdir

def package(cookbookdir, bundlepath):
    with tarfile.TarFile.gzopen(bundlepath, mode='w') as bundle:
        bundle.add(cookbookdir, arcname='cookbooks')
    shutil.rmtree(cookbookdir)
    return bundlepath
