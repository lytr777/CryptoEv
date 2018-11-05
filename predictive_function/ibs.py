from predictive_function import PredictiveFunction
from task import InitTask, MainTask
from constants.runtime import runtime_constants as rc


class InverseBackdoorSets(PredictiveFunction):
    type = "ibs"

    def __init__(self, **kwargs):
        PredictiveFunction.__init__(self, **kwargs)
        self.corrector = kwargs["corrector"] if ("corrector" in kwargs) else None

    def compute(self, cg, backdoor, cases=()):
        cases = list(cases)

        solvers = rc.configuration["solvers"]
        concurrency = rc.configuration["concurrency"]

        rc.debugger.deferred_write(1, 0, "compute for backdoor: %s" % backdoor)
        rc.debugger.deferred_write(1, 0, "use time limit: %s" % solvers.get_tl("main"))
        case_count = self.selection.get_N() - len(cases)

        # init
        init_solver = solvers.get("init")
        rc.debugger.write(1, 0, "generating init cases...")

        init_tasks, init_cases = [], []
        for i in range(case_count):
            case = cg.generate_init()
            init_cases.append(case)

            init_task = InitTask(
                case=case,
                solver=init_solver
            )
            init_tasks.append(init_task)

        init_solved, init_time = concurrency.solve(init_tasks)
        rc.debugger.write(1, 0, "has been solved %d init cases" % len(init_solved))
        if case_count != len(init_solved):
            rc.debugger.write(0, 0, "warning! case_count != len(init_solved)")

        # main
        main_solver = solvers.get("main")
        rc.debugger.write(1, 0, "generating main cases...")

        main_tasks = []
        for init_case in init_solved:
            main_task = MainTask(
                case=cg.generate(backdoor, init_case.solution),
                solver=main_solver
            )
            main_tasks.append(main_task)

        rc.debugger.write(1, 0, "solving...")
        solved, time = concurrency.solve(main_tasks, solvers.get_workers("main"))
        cases.extend(solved)

        rc.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        if case_count != len(solved):
            rc.debugger.write(0, 0, "warning! case_count != len(solved)")
        rc.debugger.write(1, 0, "spent time: %f" % (init_time + time))

        return cases, time

    def calculate(self, cg, backdoor, compute_out):
        cases, time = compute_out
        solvers = rc.configuration["solvers"]

        rc.debugger.write(1, 0, "counting time stat...")
        time_stat, log = self.get_time_stat(cases)
        rc.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)

        tl = solvers.get_tl("main")
        if self.corrector is not None:
            rc.debugger.write(1, 0, "correcting time limit...")
            tl, dis_count = self.corrector.correct(cases, tl)
            log += "corrected time limit: %f\n" % tl
            rc.debugger.deferred_write(1, 0, "new time limit: %f" % tl)

            rc.debugger.write(1, 0, "correcting time stat...")
            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count
            rc.debugger.deferred_write(1, 0, "new time stat: %s" % time_stat)

        log += "spent time: %f\n" % time
        rc.debugger.write(1, 0, "calculating value...")
        xi = float(time_stat["DETERMINATE"]) / float(len(cases))
        if xi != 0:
            value = (2 ** len(backdoor)) * tl * (3 / xi)
        else:
            value = (2 ** cg.algorithm.secret_key_len) * tl
        rc.debugger.write(1, 0, "value: %.7g" % value)

        self.selection.correct_by((backdoor, value, cases))
        log += "%s\n" % time_stat
        return value, log, cases
