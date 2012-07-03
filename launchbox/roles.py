from copy import deepcopy
import json
import os
from os.path import basename, join

import yaml


def load_data_from_files(paths):
    store = {}
    for path in paths:
        with open(path) as f:
            for name, role in yaml.load(f).items():
                store[name] = role
    return store

def find_roles_and_mixins(basepath):
    roles = []
    mixins = []
    for root, dirs, files in os.walk(basepath):
        for fname in files:
            if not (fname.endswith('yml') or fname.endswith('yaml')):
                continue
            if basename(root) == "mixins":
                mixins.append(join(root, fname))
            elif basename(root) == "roles":
                roles.append(join(root, fname))
    return roles, mixins

def transform_runlist(roles):
    data = deepcopy(roles)
    for name, role in data.items():
        if 'run_list' in role:
            role['run_list'] = ["recipe[%s]" % v for v in role['run_list']]
    return data

def transform_cookbooks(roles):
    data = deepcopy(roles)
    for name, role in data.items():
        for name, cdata in role['cookbooks'].items():
            if not isinstance(cdata, dict):
                role['cookbooks'][name] = dict(version=cdata)
    return data

def mixin(roles, mixins):
    data = {}
    for name, role in roles.items():
        data[name] = role_data = {}
        for mixin in role.get('include_mixins', []):
            role_data.update(mixins[mixin])
        role_data.update(role)
        role_data.pop('include_mixins', None)
    return data

def dump_to_json(role, output_fname):
    with open(output_fname, 'w') as out:
        json.dump(role, out, indent=4)
