from algorithm.evolution import EvolutionAlgorithm
from algorithm.mpi_evolution import MPIEvolutionAlgorithm
from algorithm.tabu import TabuSearch
from algorithm.module import mutation, crossover
from algorithm.module.evolution_strategies import MuCommaLambda, MuPlusLambda, Genetic

from module.decomposition import Decomposition
from module.gad import GADFunction
from module.ibs import IBSFunction
from module.pool_ibs import PoolIBSFunction

from key_generators.a5_1 import A5_1
from key_generators.e0 import E0
from key_generators.trivium_64 import Trivium_64
from key_generators.trivium_96 import Trivium_96
from key_generators.bivium import Bivium
from key_generators.geffe import Geffe
from key_generators.volfram import Volfram

from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PlingelingWrapper
from wrapper.treengeling import TreengelingWrapper
from wrapper.rokk import RokkWrapper
from wrapper.cryptominisat import CryptoMinisatWrapper

from util import constant, comparator, corrector
from util.adaptive_selection import AdaptiveFunction

algorithms = {
    "ev": EvolutionAlgorithm,
    "mpi_ev": MPIEvolutionAlgorithm,
    "ts": TabuSearch
}

# meta
comparators = {
    "max_min": comparator.max_min
}

predictive_function = {
    "gad": GADFunction,
    "ibs": IBSFunction,
    "pool_ibs": PoolIBSFunction,
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
    if len(args) != 4:
        raise Exception("Count of stop_conditions args must equals 4! [<it>, <mf calls>, <locals>, <mf_value>]")
    return {
        "iterable": lambda _1, _2, _3, _4: _1 > args[0],
        "mf_calls": lambda _1, _2, _3, _4: _2 >= args[1],
        "locals": lambda _1, _2, _3, _4: _3 >= args[2],
        "mf_value": lambda _1, _2, _3, _4: _4 < args[3],
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
    "a5_1": (A5_1, constant.cnfs["a5_1"]),
    "bivium": (Bivium, constant.cnfs["bivium"]),
    "trivium_64": (Trivium_64, constant.cnfs["trivium_64"]),
    "trivium_96": (Trivium_96, constant.cnfs["trivium_96"]),
    "e0": (E0, constant.cnfs["e0"]),
    "volfram": (Volfram, constant.cnfs["volfram"]),
    "geffe": (Geffe, constant.cnfs["geffe"])
}


def adaptive_selection(args):
    if len(args) != 2:
        raise Exception("Count of adaptive_selection args must equals 2! [<min_N>, <max_N>]")
    return {
        "function": AdaptiveFunction(args[0], args[1])
    }


def solver_wrapper(args):
    if len(args) != 1:
        raise Exception("Count of evolution_strategy args must equals 1! [<timelimit?>]")
    return {
        "minisat": MinisatWrapper(args[0]),
        "lingeling": LingelingWrapper(args[0]),
        "plingeling": PlingelingWrapper(args[0]),
        "treengeling": TreengelingWrapper(args[0]),
        "rokk": RokkWrapper(args[0]),
        "cryptominisat": CryptoMinisatWrapper(args[0]),
    }


correctors = {
    "none": None,
    "mass": corrector.mass_corrector,
    "max": corrector.max_corrector,
    "throw": corrector.throw_corrector,
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
    "predictive_function": predictive_function,
    "mutation_function": mutation_function,
    "crossover_function": crossover_function,
    "stop_condition": stop_conditions,
    "evolution_strategy": evolution_strategy,
    "crypto_algorithm": crypto_algorithms,
    "adaptive_N": adaptive_selection,
    "solver_wrapper": solver_wrapper,
    "corrector": correctors,
    "decomposition": decompositions
}
