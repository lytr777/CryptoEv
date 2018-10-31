from concurrency.module.filler import TaskFiller
from model.case_generator import BackdoorCaseGenerator
from predictive_function import PredictiveFunction, TaskGenerator
from constants.runtime import runtime_constants as rc


class IBSTask:
    def __init__(self, **kwargs):
        self.bcg = kwargs["bcg"]
        self.solvers = kwargs["solvers"]

    def solve(self):
        # init
        init_case = self.bcg.generate_init()
        try:
            init_report = self.solvers.solve("init", init_case.get_cnf())
            init_case.mark_solved(init_report)
            init_case.check_solution()
        except Exception as e:
            rc.debugger.write(2, 3, "error while solving init case:\n%s" % e)

        # main
        main_case = self.bcg.generate(init_case.solution)
        try:
            main_report = self.solvers.solve("main", main_case.get_cnf())
            main_case.mark_solved(main_report)
        except Exception as e:
            rc.debugger.write(2, 3, "error while solving init case:\n%s" % e)

        return main_case.get_status(short=True), main_case.time


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

        rc.debugger.write(1, 0, "creating task generators")
        generator = TaskGenerator(
            IBSTask,
            solvers=solvers,
            bcg=BackdoorCaseGenerator(cg, backdoor)
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
