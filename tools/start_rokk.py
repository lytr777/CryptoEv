import sys
import os
import subprocess
import tempfile
import random



def parse_out(code, out):

    return 0, '', []


def print_report(time, status, solution):

    return


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

elite_time, status, solution = parse_out(code, output)
time = 0

if status is None:
    l_args = [minisat_path]
    if time_limit is not None:
        l_args.append("-cpu-lim=" + str(time_limit))
    l_args.append(files[0])
    l_args.append(files[3])

    p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    code = p.poll()

    time, status, solution = parse_out(code, output)

print_report(time + elite_time, status, solution)

for f in files:
    if os.path.isfile(f):
        os.remove(f)
exit(0)
