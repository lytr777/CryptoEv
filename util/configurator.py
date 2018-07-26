import codecs
import json

from constant import base_conf_path
from options import matcher, algorithms


def __get_option(key):
    return matcher[key]


def __substitution(parameters, value_hash):
    for key in parameters.keys():
        value = parameters[key]
        if isinstance(value, unicode) or isinstance(value, str):
            parameters[key] = __get_option(key)[value]
        elif isinstance(value, dict):
            name, args = value["name"], value["args"]
            option = __get_option(key)
            if key != "decomposition":
                parameters[key] = option(args)[name]
            else:
                parameters[key] = option(value_hash, args)[name]


def load_base(value_hash):
    return load(base_conf_path, value_hash)


def load(path, value_hash, mpi=False):
    data = json.load(open(path, 'r'))

    meta_name = data["algorithm"]
    if mpi:
        algorithm = algorithms["mpi_%s" % meta_name]
    else:
        algorithm = algorithms[meta_name]

    # meta
    meta_parameters = data[meta_name + "_parameters"]
    __substitution(meta_parameters, value_hash)
    meta_parameters["value_hash"] = value_hash

    # mf
    mf_parameters = data["mf_parameters"]
    __substitution(mf_parameters, value_hash)

    return algorithm, meta_parameters, mf_parameters
