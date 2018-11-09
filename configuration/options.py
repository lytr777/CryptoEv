from algorithm.evolution import EvolutionAlgorithm
from algorithm.mpi_evolution import MPIEvolutionAlgorithm
from algorithm.tabu import TabuSearch

from algorithm.module.strategies import MuCommaLambda, MuPlusLambda, Genetic
from algorithm.module.mutation import UniformMutation
from algorithm.module.crossover import OnePointCrossover, TwoPointCrossover, UniformCrossover
from algorithm.module.comparator import MaxMin
from algorithm.module.stop_condition import IterationStop, LocalsStop, PFValueStop, PFCallsStop, TimeStop

from predictive_function.gad import GuessAndDetermine
from predictive_function.ibs import InverseBackdoorSets

from key_generators.key_generator import builder
from key_generators.a5_1 import A5_1
from key_generators.e0 import E0
from key_generators.bivium import Bivium
from key_generators.trivium_64 import Trivium_64
from key_generators.trivium_96 import Trivium_96
from key_generators.trivium import Trivium
from key_generators.present_5_2kp import Present_5_2KP
from key_generators.present_6_1kp import Present_6_1KP
from key_generators.present_6_2kp import Present_6_2KP
from key_generators.asg_72_76 import ASG_72_76
from key_generators.asg_96_112 import ASG_96_112
from key_generators.asg_192_200 import ASG_192_200
from key_generators.geffe import Geffe
from key_generators.volfram import Volfram
from predictive_function.module.corrector import MassCorrector, MaxCorrector, RulerCorrector
from predictive_function.module.selection import AdaptiveFunction, ConstSelection

from solver.solver_net import SolverNet

from solver.cryptominisat import CryptoMinisatSolver
from solver.lingeling import LingelingSolver
from solver.minisat import MinisatSolver
from solver.painless import PainlessSolver
from solver.plingeling import PlingelingSolver
from solver.treengeling import TreengelingSolver
from solver.rokk import RokkSolver

from concurrency.module.task_queue import TaskQueue
from concurrency.workers import Workers
from concurrency.map_pool import MapPool
from concurrency.apply_pool import ApplyPool

from output.storage import Storage


def __get(d):
    def __w(name, *args):
        return d[name]

    return __w


# algorithm
def get_algorithm(name, mpi):
    name = "mpi_%s" % name if mpi else name
    return {
        "evolution": EvolutionAlgorithm,
        "mpi_evolution": MPIEvolutionAlgorithm,
        "tabu": TabuSearch
    }[name]


strategies = {
    "comma": MuCommaLambda,
    "plus": MuPlusLambda,
    "genetic": Genetic
}

mutation_functions = {
    "uniform": UniformMutation,
    # "level": LevelMutation
}

crossover_functions = {
    "one-point": OnePointCrossover,
    "two-point": TwoPointCrossover,
    "uniform": UniformCrossover
}

comparators = {
    "max_min": MaxMin
}

stop_conditions = {
    "iterations": IterationStop,
    "pf_calls": PFCallsStop,
    "pf_value": PFValueStop,
    "locals": LocalsStop,
    "time": TimeStop
}

# predictive function
predictive_functions = {
    "gad": GuessAndDetermine,
    "ibs": InverseBackdoorSets,
}


def get_key_generators(name):
    kg = {
        "a5_1": A5_1,
        "e0": E0,
        # Trivium
        "bivium": Bivium,
        "trivium_64": Trivium_64,
        "trivium_96": Trivium_96,
        "trivium": Trivium,
        # Present
        "present_5_2kp": Present_5_2KP,
        "present_6_1kp": Present_6_1KP,
        "present_6_2kp": Present_6_2KP,
        # ASG
        "asg_72_76": ASG_72_76,
        "asg_96_112": ASG_96_112,
        "asg_192_200": ASG_192_200,
        # Other
        "volfram": Volfram,
        "geffe": Geffe
    }[name]
    return builder(kg)


selection = {
    "const": ConstSelection,
    "function": AdaptiveFunction
}

correctors = {
    "mass": MassCorrector,
    "max": MaxCorrector,
    "ruler": RulerCorrector
}

# solvers
solver_system = {
    "net": SolverNet
}

solvers = {
    "minisat": MinisatSolver,
    "lingeling": LingelingSolver,
    "plingeling": PlingelingSolver,
    "treengeling": TreengelingSolver,
    "cryptominisat": CryptoMinisatSolver,
    "rokk": RokkSolver,
    "painless": PainlessSolver
}

# concurrency
concurrency = {
    "workers": Workers,
    "map_pool": MapPool,
    "apply_pool": ApplyPool
}

queues = {
    "task": TaskQueue
}

# output
output = {
    "storage": Storage
}

# modules
modules = {
    "algorithm": get_algorithm,
    "predictive_function": __get(predictive_functions),
    "solvers": __get(solver_system),
    "concurrency": __get(concurrency),
    "output": __get(output)
}

# modules
options = {
    "strategy": __get(strategies),
    "mutation_function": __get(mutation_functions),
    "crossover_function": __get(crossover_functions),
    "comparator": __get(comparators),
    "stop_condition": __get(stop_conditions),

    "key_generator": get_key_generators,
    "selection": __get(selection),
    "corrector": __get(correctors),

    "init_solver": __get(solvers),
    "main_solver": __get(solvers),

    "task_queue": __get(queues)
}
