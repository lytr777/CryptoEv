import sys
import os
import subprocess
import tempfile
import random


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

elite_path = './rokk/binary/SatELite_release'
solver_path = './rokk/binary/rokk_static'
number = str(int(random.random() * 1000000))

files = []
for ex in ['.cnf', '.vmap', '.elim']:
    files.append(tempfile.NamedTemporaryFile(prefix=number, suffix=ex).name)

l_args = [elite_path, cnf, files[0], files[1], files[2]]
p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate()[0]
code = p.poll()

elite_time, status = parse_out(code, output)
time = 0
solution = ''

if status is None:
    p_flag = False
    files.append(tempfile.NamedTemporaryFile(prefix=number, suffix='.result').name)
    l_args = [solver_path]
    if time_limit is not None:
        l_args.append('-cpu-lim=' + str(time_limit))
    l_args.append(files[0])
    l_args.append(files[3])

    p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    code = p.poll()

    time, status = parse_out(code, output)

    if (status is not None) and (status == 'SATISFIABLE'):
        l_args = [elite_path, '+ext', cnf, files[3], files[1], files[2]]
        p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()[0]

        solution = output.split("\n")[1][2:]
else:
    p_flag = True

with open(files[0]) as f:
    lines = f.readlines()
    if lines[0].__contains__('#vars: 0'):
        p_flag = True

print str(elite_time + time) + (' p' if p_flag else '')
print status
print solution

for ff in files:
    if os.path.isfile(ff):
        os.remove(ff)

exit(0)
