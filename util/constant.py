base_out = "./out/"
out_suffix = ".out"

cnfs = {
    "a5_1": "./templates/A5_1.cnf",
    "a5_toy": "./templates/A5_toy.cnf",
    "trivium_64": "./templates/Trivium_64.cnf",
    "trivium_96":  "./templates/Trivium_96.cnf",
    "bivium": "./templates/Bivium.cnf",
    "e0": "./templates/E0.cnf",
    "volfram": "./templates/Volfram.cnf",
    "geffe": "./templates/Geffe.cnf"
}

solver_paths = {
    "minisat": "./minisat/core/minisat_static",
    "lingeling": "./lingeling/lingeling",
    "treengeling": "./lingeling/treengeling",
    "plingeling": "./lingeling/plingeling",
    "rokk": "./rokk/binary/rokk.py",
    "cryptominisat": "./cryptominisat/build/cryptominisat5"
}

log_path = './out/new_log_'
locals_log_path = './out/new_locals_log_'
true_log_path = './out/true_log'
