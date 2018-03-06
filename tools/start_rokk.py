import sys
import os
import subprocess
import tempfile
import random

from util.parser import parse_solution_file


def parse_out(code, out):
    t = 0
    st = None
    lines = out.split('\n')
    for line in lines:
        if line.startswith("c CPU time"):
            t_str = ""
            for c in line.split(':')[1]:
                if c.isdigit() or c == '.':
                    t_str += c
            t = float(t_str)

        if line.startswith("s "):
            st = line.split(' ')[1]

    return t, st


if len(sys.argv) < 2:
    print "USAGE: rokk_py.py <input CNF> [time limit]"
    exit(1)

cnf = sys.argv[1]
time_limit = None
if len(sys.argv) > 2:
    time_limit = int(sys.argv[2])

elite_path = ''
minisat_path = ''
number = int(random.random() * 1000000)
out_dir = 'rokk_out'

files = []
for ex in ['.cnf', '.vmap', '.elim', '.result']:
    files.append(tempfile.NamedTemporaryFile(dir=out_dir, prefix=number, suffix=ex).name)

# start SATELite
l_args = [elite_path, cnf, files[0], files[1], files[2]]
p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate()[0]
code = p.poll()

elite_time, status = parse_out(code, output)
time = 0
solution = ''

if status is None:
    l_args = [minisat_path]
    if time_limit is not None:
        l_args.append('-cpu-lim=' + str(time_limit))
    l_args.append(files[0])
    l_args.append(files[3])

    p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    code = p.poll()

    time, status = parse_out(code, output)

    if (status is not None) and (status == 'SATISFIABLE'):
        solution = parse_solution_file(files[3])

print time
print status
print solution

for f in files:
    if os.path.isfile(f):
        os.remove(f)
exit(0)
