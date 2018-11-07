from predictive_function import PredictiveFunction
from task import MainTask, InitTask
from constants.runtime import runtime_constants as rc


class GuessAndDetermine(PredictiveFunction):
    type = "gad"

    def __init__(self, **kwargs):
        PredictiveFunction.__init__(self, **kwargs)
        self.decomposition = kwargs["decomposition"] if ("decomposition" in kwargs) else None

    def __main_phase(self, backdoor, init_case, count):
        concurrency = rc.configuration["concurrency"]
        solvers = rc.configuration["solvers"]
        cg = rc.case_generator
        rc.debugger.write(1, 0, "generating main cases...")

        main_tasks = []
        for i in range(count):
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
        if count != len(solved):
            rc.debugger.deferred_write(0, 0, "warning! count != len(solved)")
        rc.debugger.write(1, 0, "spent time: %f" % time)

        return solved, time

    def compute(self, backdoor, cases=()):
        cases = list(cases)

        cg = rc.case_generator
        rc.debugger.write(1, 0, "compute for backdoor: %s" % backdoor)

        # init
        init_task = InitTask(
            solver=rc.configuration["solvers"].get("init"),
            substitutions=cg.get_init_substitutions(),
            algorithm=cg.algorithm
        )
        init_case = init_task.solve()

        all_time = 0
        while len(cases) < self.selection.get_N():
            all_case_count = self.selection.get_N() - len(cases)

            if all_case_count > self.chunk_size:
                case_count = self.chunk_size
            else:
                case_count = all_case_count

            solved, time = self.__main_phase(backdoor, init_case, case_count)

            cases.extend(solved)
            all_time += time

        rc.debugger.write(1, 0, "spent time: %f" % all_time)
        return cases, all_time

    def calculate(self, backdoor, compute_out):
        cases, time = compute_out
        
        rc.debugger.write(1, 0, "counting time stat...")
        time_stat, cases_log = self.get_time_stat(cases)
        rc.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)
        
        log = cases_log
        log += "spent time: %f\n" % time

        rc.debugger.write(1, 0, "calculating value...")
        times_sum = 0
        for _, time in cases:
            times_sum += time

        value = (2 ** len(backdoor)) * times_sum / len(cases)
        rc.debugger.write(1, 0, "value: %.7g\n" % value)

        log += "%s\n" % time_stat
        return value, log, cases
