import json
import pkg_resources


def resource_spec(spec):
    """
    Loads resource from a string specifier. 
    
    >>> config.resource_spec('egg:monkeylib#data/languages.ini')
    '.../monkeylib/data/languages.ini'

    >>> config.resource_spec('file:data/languages.ini')
    'data/languages.ini'

    >>> config.resource_spec('data/languages.ini')
    'data/languages.ini'
    """
    filepath = spec
    if spec.startswith('egg:'):
        req, subpath = spec.split('egg:')[1].split('#')
        req = pkg_resources.Requirement.parse(req)
        filepath = res_filename(req, subpath)
    elif spec.startswith('file:'):
        filepath = spec.split('file:')[1]
    # Other specs could be added, but egg and file should be fine for
    # now
    return filepath


def res_stream(req, path):
    return pkg_resources.resource_stream(req, path)


def res_filename(req, path):
    return pkg_resources.resource_filename(req, path)


def res_json(req, path):
    return json.load(res_stream(req, path))


