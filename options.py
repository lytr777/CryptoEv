from key_generators.a5_1 import A5_1
from key_generators.e0 import E0
from key_generators.trivium_64 import Trivium_64
from key_generators.bivium import Bivium

from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PLingelingWrapper
from wrapper.rokk import RokkWrapper
from wrapper.rokk_py import RokkPyWrapper

from solvers.sleep_solver import SleepSolver
from solvers.worker_solver import WorkerSolver
from module.gad_function import GADFunction
from module.ibs_function import IBSFunction

from util import constant, mutation

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "rokk": RokkWrapper(constant.rokk_path),
    "rokk_py": RokkPyWrapper(constant.rokk_py_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

crypto_algorithms = {
    "a5_1": (A5_1, constant.a5_1_cnf),
    "bivium": (Bivium, constant.bivium_cnf),
    "trivium_64": (Trivium_64, constant.trivium_64_cnf),
    "e0": (E0, constant.e0_cnf)
}


def stop_conditions(it, value, locals_count):
    return {
        "iterable": lambda _1, _2, _3: _1 > it,
        "value": lambda _1, _2, _3: _2 <= value,
        "mix": lambda _1, _2, _3: _1 > it or _2 <= value,
        "locals": lambda _1, _2, _3: _3 >= locals_count,
    }


mutation_strategy = {
    "neighbour": mutation.neighbour_mutation,
    "normally": mutation.normally_mutation,
    "scaled": lambda v: mutation.scaled_mutation(2., v),
    "swap": mutation.swap_mutation
}

minimization_functions = {
    "gad": GADFunction,
    "ibs": IBSFunction
}

multi_solvers = {
    "sleep": SleepSolver,
    "worker": WorkerSolver
}
