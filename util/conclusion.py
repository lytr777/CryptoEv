from parse_utils.log_parser_v3 import LogParserV3


def add_conclusion(parameters):
    comparator = parameters["comparator"]
    path = parameters["path"]

    if "locals_list" in parameters:
        locals_list = parameters["locals_list"]
    else:
        parser = LogParserV3()
        info, its = parser.parse_for_path(path)

        if len(its) == 0:
            return

        locals_list = []
        previous = its[0][0].mv()
        for cases in its:
            best = cases[0].mv()
            for case in cases:
                current = case.mv()
                if comparator(best, current) > 0:
                    best = current

            if comparator(best, previous) > 0 and str(best[0]) != str(previous[0]):
                locals_list.append(previous)

            previous = best

        if len(locals_list) == 0:
            locals_list.append(previous)

    conclusion = "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"

    if len(locals_list) > 0:
        best = locals_list[0]

        for local in locals_list:
            if comparator(best, local) > 0:
                best = local
            conclusion += "value: %.7g for backdoor: %s\n" % (local[1], local[0])

        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "best value: %.7g for backdoor: %s\n" % (best[1], best[0])
    else:
        conclusion += "locals not found\n"

    with open(path, 'a') as f:
        f.write(conclusion)



