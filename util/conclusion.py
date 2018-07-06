from parse_utils.log_parser import LogParser
from formatter import format_array


def add_conclusion(path, comparator, locals_list=None):
    if locals_list is None:
        parser = LogParser()
        info, its = parser.parse_for_path(path)
        print info

        if len(its) == 0:
            return

        locals_list = []
        previous = its[0][0].get_case()
        for cases in its:
            best = cases[0].get_case()
            for case in cases:
                current = case.get_case()
                if comparator(best, current) > 0:
                    best = current

            if comparator(best, previous) > 0:
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
            conclusion += "best local: %s with value: %.7g\n" % (format_array(local[0]), local[1])

        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "------------------------------------------------------\n"
        conclusion += "best: %s with value: %.7g\n" % (format_array(best[0]), best[1])
    else:
        conclusion += "best locals not found\n"

    with open(path, 'a') as f:
        f.write(conclusion)



