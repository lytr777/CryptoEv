base_out = "./out/"
out_suffix = ".out"

cnfs = {
    "a5_1": "./templates/A5_1.cnf",
    "e0": "./templates/E0.cnf",
    "trivium_64": "./templates/Trivium_64.cnf",
    "trivium_96": "./templates/Trivium_96.cnf",
    "bivium": "./templates/Bivium.cnf",
    "present_5_2kp": "./templates/Present_5_2KP.cnf",
    "present_6_1kp": "./templates/Present_6_1KP.cnf",
    "present_6_2kp": "./templates/Present_6_2KP.cnf",
    "volfram": "./templates/Volfram.cnf",
    "geffe": "./templates/Geffe.cnf"
}

solver_paths = {
    "minisat": "./minisat/core/minisat_static",
    "lingeling": "./lingeling/lingeling",
    "treengeling": "./lingeling/treengeling",
    "plingeling": "./lingeling/plingeling",
    "rokk": "./rokk/binary/rokk.py",
    "cryptominisat": "./cryptominisat/build/cryptominisat5",
    "painless": "./painless/painless-maplecomsps"
}

in_out_tools = {
    "in": "./tools/in_out/stdin_to_file.py",
    "out": "./tools/in_out/file_to_stdout.py",
    "both": "./tools/in_out/stdin_to_file_to_stdout.py",
}

log_path = './out/new_log_'
locals_log_path = './out/new_locals_log_'
true_log_path = './out/true_log_'
