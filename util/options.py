from algorithm.evolution import EvolutionAlgorithm
from algorithm.tabu import TabuSearch
from algorithm.module import mutation, crossover
from algorithm.module.evolution_strategies import MuCommaLambda, MuPlusLambda, Genetic

from module.decomposition import Decomposition
from module.gad_function import GADFunction
from module.ibs_function import IBSFunction

from key_generators.a5_1 import A5_1
from key_generators.e0 import E0
from key_generators.trivium_64 import Trivium_64
from key_generators.bivium import Bivium

from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.rokk import RokkWrapper
from wrapper.rokk_py import RokkPyWrapper

from solvers.sleep_solver import SleepSolver
from solvers.worker_solver import WorkerSolver

from util import constant, comparator, corrector

algorithms = {
    "ev": EvolutionAlgorithm,
    "ts": TabuSearch
}

# meta
comparators = {
    "max_min": comparator.max_min
}

minimization_functions = {
    "gad": GADFunction,
    "ibs": IBSFunction
}


def mutation_function(args):
    if len(args) != 1:
        raise Exception("Count of mutation_function args must equals 1! [<scale>]")
    return {
        "neighbour": mutation.neighbour_mutation,
        "uniform": mutation.scaled_uniform_mutation(args[0]),
        "swap": mutation.swap_mutation
    }


def crossover_function(args):
    if len(args) != 1:
        raise Exception("Count of crossover_function args must equals 1! [<p>]")
    return {
        "one-point": crossover.one_point_crossover,
        "two-point": crossover.two_point_crossover,
        "uniform": crossover.uniform_crossover(args[0])
    }


def stop_conditions(args):
    if len(args) != 3:
        raise Exception("Count of stop_conditions args must equals 3! [<it>, <mf calls>, <locals>]")
    return {
        "iterable": lambda _1, _2, _3: _1 > args[0],
        "mf_calls": lambda _1, _2, _3: _2 >= args[1],
        "locals": lambda _1, _2, _3: _3 >= args[2],
    }


def evolution_strategy(args):
    if len(args) != 3:
        raise Exception("Count of evolution_strategy args must equals 3! [<m>, <l>, <k>]")
    return {
        "comma": MuCommaLambda(args[0], args[1]),
        "plus": MuPlusLambda(args[0], args[1]),
        "genetic": Genetic(args[0], args[1], args[2])
    }


# mf
crypto_algorithms = {
    "a5_1": (A5_1, constant.a5_1_cnf),
    "bivium": (Bivium, constant.bivium_cnf),
    "trivium_64": (Trivium_64, constant.trivium_64_cnf),
    "e0": (E0, constant.e0_cnf)
}

solver_wrappers = {
    "minisat": MinisatWrapper(),
    "lingeling": LingelingWrapper(),
    "rokk": RokkWrapper(),
    "rokk_py": RokkPyWrapper(),
}

multi_solvers = {
    "sleep": SleepSolver,
    "worker": WorkerSolver
}


def correctors(args):
    if len(args) != 1:
        raise Exception("Count of correctors args must equals 1! [<coefficient>]")
    return {
        "none": None,
        "mass": corrector.mass_corrector(args[0])
    }


def decompositions(value_hash, args):
    if len(args) != 2:
        raise Exception("Count of decomposition args must equals 2! [<decomposition power>, <break time>]")
    return {
        "none": None,
        "base": Decomposition(value_hash, args[0], args[1])
    }


# matcher
matcher = {
    "comparator": comparators,
    "minimization_function": minimization_functions,
    "mutation_function": mutation_function,
    "crossover_function": crossover_function,
    "stop_condition": stop_conditions,
    "evolution_strategy": evolution_strategy,
    "crypto_algorithm": crypto_algorithms,
    "solver_wrapper": solver_wrappers,
    "multi_solver": multi_solvers,
    "corrector": correctors,
    "decomposition": decompositions
}
