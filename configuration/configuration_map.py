configurations = {
    "2500": "configuration/examples/2500.json",
    "base": "configuration/examples/base.json",
    "tabu": "configuration/examples/tabu.json",
    "trivium_64": "configuration/examples/trivium_64.json",
    "true": "configuration/examples/true.json",
}


def get_path(tag):
    if tag in configurations:
        return configurations[tag]

    exc_str = "Unknown tag: '%s'. Use one of the following: %s\n" % (tag, configurations.keys())
    exc_str += "Please, add extension '.json' if you trying to load own configuration"
    raise Exception(exc_str)
