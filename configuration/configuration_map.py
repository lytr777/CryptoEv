configurations = {
    "base": "configuration/examples/base.json",
    "rank": "configuration/examples/rank.json",
    "tabu": "configuration/examples/tabu.json",
    "trivium_64": "configuration/examples/trivium_64.json",

    "true": "configuration/examples/true.json",
    "verification": "configuration/examples/verification.json",

    "base_test": "configuration/test/base.json",
    "tabu_test": "configuration/test/tabu.json",
    "true_test": "configuration/test/true.json",
    "rank_test": "configuration/test/rank.json",
}


def get_path(tag):
    if tag in configurations:
        return configurations[tag]

    exc_str = "Unknown tag: '%s'. Use one of the following: %s\n" % (tag, configurations.keys())
    exc_str += "Please, add extension '.json' if you trying to load own configuration"
    raise Exception(exc_str)
