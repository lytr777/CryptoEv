from parse_utils.log_parser import LogParser

def add_conclusion(parameters):
    comparator = parameters["comparator"]
    path = parameters["path"]

    if "locals_list" in parameters:
        locals_list = parameters["locals_list"]
    elif "function_type" in parameters:
        function_type = parameters["function_type"]
        parser = LogParser(function_type)
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
    else:
        raise Exception("add locals_list or function_type in parameters map")

    conclusion = "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"

    if len(locals_list) > 0:
        best = locals_list[0]

        for local in locals_list:
            if comparator(best, local) > 0:
                best = local
            conclusion += "local: %s with value: %.7g\n" % (local[0], local[1])

        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "best: %s with value: %.7g\n" % (best[0], best[1])
    else:
        conclusion += "locals not found\n"

    with open(path, 'a') as f:
        f.write(conclusion)



