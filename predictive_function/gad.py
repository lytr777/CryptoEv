from concurrency.module.filler import TaskFiller
from model.case_generator import BackdoorCaseGenerator
from predictive_function import PredictiveFunction, TaskGenerator
from constants.runtime import runtime_constants as rc


class GADTask:
    def __init__(self, **kwargs):
        self.bcg = kwargs["bcg"]
        self.solvers = kwargs["solvers"]
        self.init_case = kwargs["init_case"]

    def solve(self):
        # main
        main_case = self.bcg.generate(self.init_case.solution, rnd="b")
        main_report = self.solvers.solve("main", main_case.get_cnf())
        main_case.mark_solved(main_report)

        return main_case.get_status(short=True), main_case.time


class GuessAndDetermine(PredictiveFunction):
    type = "gad"

    def __init__(self, **kwargs):
        PredictiveFunction.__init__(self, **kwargs)
        self.decomposition = kwargs["decomposition"] if ("decomposition" in kwargs) else None

    def solve_init(self, bcg, solvers):
        init_case = bcg.generate_init()
        init_report = solvers.solve("init", init_case.get_cnf())

        init_case.mark_solved(init_report)
        init_case.check_solution()
        return init_case

    def compute(self, cg, backdoor, cases=()):
        cases = list(cases)

        solvers = rc.configuration["solvers"]
        concurrency = rc.configuration["concurrency"]

        rc.debugger.deferred_write(1, 0, "compute for backdoor: %s" % backdoor)

        bcg = BackdoorCaseGenerator(cg, backdoor)
        init_case = self.solve_init(bcg, solvers)

        rc.debugger.write(1, 0, "creating task generators")
        generator = TaskGenerator(
            GADTask,
            bcg=bcg,
            solvers=solvers,
            init_case=init_case
        )

        rc.debugger.write(1, 0, "creating task filler")
        filler = TaskFiller(
            generator=generator,
            complexity=solvers.get_workers("main"),
            count=self.selection.get_N() - len(cases)
        )

        rc.debugger.write(1, 0, "solving...")
        solved, time = concurrency.solve(filler)
        cases.extend(solved)
        rc.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        rc.debugger.write(1, 0, "spent time: %f" % time)

        return cases, time

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
