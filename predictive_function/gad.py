from predictive_function import PredictiveFunction
from task import MainTask, InitTask
from constants.runtime import runtime_constants as rc


class GuessAndDetermine(PredictiveFunction):
    type = "gad"

    def __init__(self, **kwargs):
        PredictiveFunction.__init__(self, **kwargs)
        self.decomposition = kwargs["decomposition"] if ("decomposition" in kwargs) else None

    def __main_phase(self, cg, backdoor, init_case, count):
        solvers = rc.configuration["solvers"]
        concurrency = rc.configuration["concurrency"]

        main_solver = solvers.get("main")
        rc.debugger.write(1, 0, "generating main cases...")

        main_tasks = []
        for i in range(count):
            main_task = MainTask(
                case=cg.generate(backdoor, init_case.solution, rnd="b"),
                solver=main_solver
            )
            main_tasks.append(main_task)

        rc.debugger.write(1, 0, "solving...")
        solved, time = concurrency.solve(main_tasks, solvers.get_workers("main"))

        rc.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        if count != len(solved):
            rc.debugger.deferred_write(0, 0, "warning! count != len(solved)")
        rc.debugger.write(1, 0, "spent time: %f" % time)

        return solved, time

    def compute(self, cg, backdoor, cases=()):
        cases = list(cases)

        solvers = rc.configuration["solvers"]
        rc.debugger.write(1, 0, "compute for backdoor: %s" % backdoor)

        # init
        init_task = InitTask(
            case=cg.generate_init(),
            solver=solvers.get("init")
        )
        init_case = init_task.solve()

        all_time = 0
        while len(cases) < self.selection.get_N():
            all_case_count = self.selection.get_N() - len(cases)

            if all_case_count > self.chunk_size:
                case_count = self.chunk_size
            else:
                case_count = all_case_count

            solved, time = self.__main_phase(cg, backdoor, init_case, case_count)

            cases.extend(solved)
            all_time += time

        rc.debugger.write(1, 0, "spent time: %f" % all_time)
        return cases, all_time

    def calculate(self, cg, backdoor, compute_out):
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
        
        partially_value = (2 ** len(backdoor)) * times_sum

        # additional decomposition?
        #
        
        value = partially_value / len(cases)
        rc.debugger.write(1, 0, "value: %.7g\n" % value)

        log += "%s\n" % time_stat
        return value, log, cases
