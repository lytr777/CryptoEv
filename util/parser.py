from model.cnf_model import Clause, Var, Cnf


def __read_file(file_path):
    with open(file_path) as f:
        lines = f.readlines()
        data = [str(x).split("\n")[0] for x in lines]

        return data


def parse_solution(solver_out_file):
    data = __read_file(solver_out_file)

    status = data[0]
    if status != "SAT":
        return []

    data = data[1].split(" ")
    solution = []
    for var in data:
        num_int = int(var)
        if num_int < 0:
            solution.append(0)
        elif num_int > 0:
            solution.append(1)

    return solution


def parse_cnf(cnf_file):
    cnf = Cnf()
    for rec in __read_file(cnf_file):
        rec = rec.strip()
        clause = Clause()
        if (rec[0].isdigit()) or (rec[0].startswith("-")):
            for num in rec.split():
                num_int = int(num)
                if num_int < 0:
                    clause.add_var(Var(abs(num_int), True))
                elif num_int > 0:
                    clause.add_var(Var(abs(num_int), False))
            cnf.add_clause(clause)

    return cnf


def parse_out(out_path, k):
    data = __read_file(out_path)
    i = 0
    steps = []
    while len(data) > i:
        step = []
        for j in range(k):
            i += __skip_while(data, i, lambda s: not s.startswith("start") and (
                    not s.startswith("mask") and not s.startswith("best")))
            if data[i].startswith("mask"):
                mask = data[i].split(" ")[1].split("(")[0]
                i += 1
                metric = float(data[i].split(" ")[2])
                step.append((metric, mask))
            elif data[i].startswith("start"):
                mask = data[i].split(" ")[4].split("(")[0]
                i += __skip_while(data, i, lambda s: not s.startswith("end"))
                metric = float(data[i].split(" ")[4])
                step.append((metric, mask))
            else:
                break

        if len(step) == 0:
            break
        best = step[0]
        for j in range(1, k):
            if step[j][0] < best[0]:
                best = step[j]
        steps.append(best)

    return steps


def __skip_while(data, index, predicate):
    i = 0
    while predicate(data[index + i]):
        i += 1

    return i
