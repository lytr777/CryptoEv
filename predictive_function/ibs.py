from predictive_function import PredictiveFunction
from task import InitTask, MainTask
from constants.runtime import runtime_constants as rc


class InverseBackdoorSets(PredictiveFunction):
    type = "ibs"

    def __init__(self, **kwargs):
        PredictiveFunction.__init__(self, **kwargs)
        self.corrector = kwargs["corrector"] if ("corrector" in kwargs) else None

    def __init_phase(self, count):
        concurrency = rc.configuration["concurrency"]
        cg = rc.case_generator
        rc.debugger.write(1, 0, "generating init cases...")

        init_tasks = []
        for i in range(count):
            init_task = InitTask(
                solver=rc.configuration["solvers"].get("init"),
                substitutions=cg.get_init_substitutions(),
                algorithm=cg.algorithm
            )
            init_tasks.append(init_task)

        init_solved, init_time = concurrency.solve(init_tasks)
        rc.debugger.write(1, 0, "has been solved %d init cases" % len(init_solved))
        if count != len(init_solved):
            rc.debugger.write(0, 0, "warning! count != len(init_solved)")

        return init_solved, init_time

    def __main_phase(self, backdoor, init_solved):
        concurrency = rc.configuration["concurrency"]
        solvers = rc.configuration["solvers"]
        cg = rc.case_generator
        rc.debugger.write(1, 0, "generating main cases...")

        main_tasks = []
        for init_case in init_solved:
            main_subs = cg.get_substitutions(backdoor, init_case.solution)
            main_task = MainTask(
                solver=solvers.get("main"),
                substitutions=main_subs,
                algorithm=cg.algorithm
            )
            main_tasks.append(main_task)

        rc.debugger.write(1, 0, "solving...")
        solved, time = concurrency.solve(main_tasks, solvers.get_workers("main"))
        rc.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        if len(init_solved) != len(solved):
            rc.debugger.write(0, 0, "warning! len(init_solved) != len(solved)")

        return solved, time

    def compute(self, backdoor, cases=()):
        cases = list(cases)

        solvers = rc.configuration["solvers"]
        rc.debugger.deferred_write(1, 0, "compute for backdoor: %s" % backdoor)
        rc.debugger.deferred_write(1, 0, "use time limit: %s" % solvers.get_tl("main"))

        all_time = 0
        while len(cases) < self.selection.get_N():
            all_case_count = self.selection.get_N() - len(cases)

            if all_case_count > self.chunk_size:
                case_count = self.chunk_size
            else:
                case_count = all_case_count

            init_solved, init_time = self.__init_phase(case_count)
            solved, time = self.__main_phase(backdoor, init_solved)

            cases.extend(solved)
            all_time += init_time + time

        rc.debugger.write(1, 0, "spent time: %f" % all_time)
        return cases, all_time

    def calculate(self, backdoor, compute_out):
        cases, time = compute_out
        solvers = rc.configuration["solvers"]
        cg = rc.case_generator

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

        self.correct_selection(backdoor, value, cases)
        log += "%s\n" % time_stat
        return value, log, cases
