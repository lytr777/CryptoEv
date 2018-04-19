import numpy as np

from model.cnf_model import Clause, Var, Cnf


def __read_file(file_path):
    with open(file_path) as f:
        lines = f.readlines()
        data = [str(x).split("\n")[0] for x in lines]

        return data


def parse_solution_file(solver_out_file):
    data = __read_file(solver_out_file)

    status = data[0]
    if status != "SAT":
        return ""

    return data[1]


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


def restore_hash(value_hash, out_path, k):
    data = __read_file(out_path)
    i = 0
    while len(data) > i:
        for j in range(k):
            i += __skip_while(data, i, lambda s: not s.startswith("start") and not s.startswith("best"))
            if data[i].startswith("start"):
                key = data[i].split(" ")[4]
                i += __skip_while(data, i, lambda s: not s.startswith("end"))
                value = float(data[i].split(" ")[4])
                value_hash[key] = value
            else:
                return


def parse_out(out_path, k):
    data = __read_file(out_path)
    i = 0
    steps = []
    while len(data) > i:
        step = []
        for j in range(k):
            try:
                i += __skip_while(data, i, lambda s: not s.startswith("start") and (not s.startswith("mask") and not s.startswith("best")))
            except IndexError:
                break
            if data[i].startswith("mask"):
                mask = data[i].split(" ")[1].split("(")[0]
                mask = np.array([c for c in mask]).astype(np.int)
                i += 1
                value = float(data[i].split(" ")[2])
                step.append((mask, value))
            elif data[i].startswith("start"):
                mask = data[i].split(" ")[4].split("(")[0]
                mask = np.array([c for c in mask]).astype(np.int)
                i += __skip_while(data, i, lambda s: not s.startswith("end"))
                value = float(data[i].split(" ")[4])
                step.append((mask, value))
            else:
                break

        if len(step) == 0:
            break
        best = step[0]
        for j in range(1, k):
            if step[j][1] < best[1]:
                best = step[j]
        steps.append(best)

    return steps


def parse_true_out(out_path):
    data = __read_file(out_path)
    i = 0
    cases = []
    while len(data) > i:
        times = []
        i += __skip_while(data, i, lambda s: not s.startswith("start") and (
                not s.startswith("metric")))
        if data[i].startswith("start"):
            i += __skip_while(data, i, lambda s: not s.startswith("progress"))
            while data[i].startswith("progress"):
                str_times = data[i].split("[")[1].split("]")[0].split(",")
                for j in range(len(str_times)):
                    times.append(float(str_times[j]))
                i += 1
        else:
            break

        if len(times) != 0:
            statistic = {"0.1": 0, "<1": 0, "<10": 0, ">10": 0}

            time_sum = 0
            unfair_time_sum = 0
            for time in times:
                if time == 0.1:
                    statistic["0.1"] += 1
                    unfair_time_sum += 0.000005
                elif time < 1.:
                    statistic["<1"] += 1
                    unfair_time_sum += time
                elif time < 10.:
                    statistic["<10"] += 1
                    unfair_time_sum += time
                else:
                    statistic[">10"] += 1
                    unfair_time_sum += time
                time_sum += time

            print unfair_time_sum / time_sum
            cases.append(statistic)

    return cases


def __skip_while(data, index, predicate):
    i = 0
    while predicate(data[index + i]):
        i += 1

    return i
