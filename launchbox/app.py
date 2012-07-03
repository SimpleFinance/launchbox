from functools import partial
import hashlib
import logging
from os.path import join
import sys

from .output import log
from .osutils import mkdirp
from .errors import *
from .cookbooks import *
from .roles import *
from .client import CookbookClient, S3CookbookRemote, HttpCookbookRemote

def thrush(data, *fns):
    ret = data
    for fn in fns:
        ret = fn(ret)
    return ret

def sign(fname):
    h = hashlib.sha256()
    with open(fname) as f:
        while True:
            buf = f.read(4096)
            if not buf : break
            h.update(buf)
    with open(fname + ".sha256", 'w') as f:
        f.write(h.hexdigest())

def launchbox(params):
    """Params is a dictionary that should look like

    {'--access-key': None,
     '--bucket': 'your.bucket.name',
     '--cache-dir': './cache',
     '--help': False,
     '--secret-key': None,
     '--source': './src',
     '--target': './target',
     '--url': None,
     '--version': False,
     '<role>': ['bar'],
     'clean': False,
     'deps': True,
     'package': False
     }
     """

    cache_dir = params['--cache-dir']
    input_dir = params['--source']
    output_dir = params['--target']

    if params['clean']:
        shutil.rmtree(cache_dir)
        shutil.rmtree(output_dir)
        return 0

    log.level = logging.DEBUG
    mkdirp(cache_dir)
    mkdirp(output_dir)

    if params['--bucket']:
        access_key = params['--access-key']
        secret_key = params['--secret-key']
        bucket = params['--bucket']
        delegate = S3CookbookRemote(access_key, secret_key, bucket)
    else:
        delegate = HttpCookbookRemote(params['--url'])

    client = CookbookClient(cache_dir, delegate)

    download = partial(download_cookbooks, client)


    role_paths, mixin_paths = find_roles_and_mixins(input_dir)

    all_roles = thrush(mixin(load_data_from_files(role_paths),
                             load_data_from_files(mixin_paths)),
                       transform_cookbooks,
                       transform_runlist)
    roles = {}
    if params['<role>']:
        for role in params['<role>']:
            roles[role] = all_roles[role]
    else:
        roles = all_roles

    if params['deps']:
        data = {}
        for name, role in roles.items():
            cookbooks = role['cookbooks']
            _, dep_tree = resolve_dependencies(client, cookbooks, allow_not_found=True)
            data[name] = dep_tree
        print json.dumps(data, indent=4)
        return 0
    elif params['package']:
        for name, role in roles.items():
            cookbooks = role.pop('cookbooks')
            json_fname = join(output_dir, "%s.json" % name)
            tarball_fname = join(output_dir, "%s.tar.gz" % name)
            dump_to_json(role, json_fname)
            package(extract(download(cookbooks)), tarball_fname)
            sign(json_fname)
            sign(tarball_fname)



def run(params):
    if params['--access-key'] == '$AWS_ACCESS_KEY_ID':
        params['--access-key'] = os.environ['AWS_ACCESS_KEY_ID']
    if params['--secret-key'] == '$AWS_SECRET_ACCESS_KEY':
        params['--secret-key'] = os.environ['AWS_SECRET_ACCESS_KEY']
    try:
        sys.exit(launchbox(params))
    except Error as e:
        log.error('ERROR: %s', e.message)
        sys.exit(128)
