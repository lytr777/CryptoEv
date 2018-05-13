from parser import parse_out
from formatter import format_array


def add_conclusion(filename, k, comparator, locals_list=None):
    if locals_list is None:
        steps, stat = parse_out(filename, k)
        print stat

        if len(steps) == 0:
            return

        print steps
        last_step = steps[0]
        locals_list = []
        for step in steps:
            if comparator(last_step, step) < 0:
                locals_list.append(last_step)

            last_step = step

        if len(locals_list) == 0:
            locals_list.append(last_step)

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

    with open(filename, 'a') as f:
        f.write(conclusion)



