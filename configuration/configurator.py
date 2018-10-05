import json

from configuration_map import get_path
from options import modules, options


class MissingArgumentException(Exception):
    def __init__(self, name, arg_name):
        self.name = name
        self.arg_name = arg_name

    def __str__(self):
        return "Missing argument '%s' from option: '%s'" % (self.arg_name, self.name)


def __substitute_option(key, value):
    name = value["name"]
    option = options[key](name)

    for v_key in value.keys():
        if isinstance(value[v_key], dict):
            value[v_key] = __substitute_option(v_key, value[v_key])
    try:
        return option(**value)
    except KeyError as e:
        raise MissingArgumentException(option.name, e.message)


def __substitute(key, value, mpi):
    t = value["type"]
    module = modules[key](t, mpi)

    for v_key in value.keys():
        if isinstance(value[v_key], dict):
            value[v_key] = __substitute_option(v_key, value[v_key])

    return module(**value)


def load_base():
    return load(get_path("base"))


def load(path, mpi=False):
    if not path.endswith(".json"):
        path = get_path(path)

    data = json.load(open(path, 'r'))

    for key in data.keys():
        data[key] = __substitute(key, data[key], mpi)

    return path, data
