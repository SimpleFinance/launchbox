def pad_to_3(components):
    return components + ([0] * (3 - len(components)))

def matches_version_constraint(constraint, target, version):
    """ See http://wiki.opscode.com/display/chef/Version+Constraints

    Do not pad the target to 3 (it would change the meaning of ~>)
    """
    version = pad_to_3(version) # just in case
    if constraint == '~>':
        high = pad_to_3(target[:-2] + [(target[-2] + 1), 0])
        low = pad_to_3(target)
        return low <= version < high
    else:
        target = pad_to_3(target)

    if constraint == '>':
        return version > target
    elif constraint == '<':
        return version < target
    elif constraint == '<=':
        return version <= target
    elif constraint == '>=':
        return version >= target
    elif constraint == '=':
        return version == target

def high_to_low(versions):
    return sorted(((pad_to_3(version_to_components(v)), v) for v in versions), reverse=True)

def version_to_components(verstring):
    return [int(comp) for comp in verstring.split('.')]

def components_to_version(components):
    return '.'.join(str(c) for c in components)

def highest_version_match(verspec, versions):
    constraint, target = verspec.split(' ')
    target = version_to_components(target)
    for version, verstring in high_to_low(versions):
        if matches_version_constraint(constraint, target, version):
            return verstring
