import sys
import subprocess


def parse_out(out):
    i = 0
    lines = out.split('\n')
    while not lines[i].startswith("i CPU time"):
        i += 1
    t = float(lines[i].split(':')[1])

    while not lines[i].startswith("i "):
        i += 1
    st = lines[i].split(' ')[1]

    s = ''
    c = ''
    i += 1
    if st == 'SATISFIABLE':
        s = lines[i]
    elif st == 'PRESATELITED':
        while i < len(lines):
            c += lines[i] + '\n'
            i += 1

    return t, st, s, c


if len(sys.argv) < 2:
    print "USAGE: rokk_py.py [time limit]"
    exit(1)

time_limit = None
if len(sys.argv) > 1:
    time_limit = int(sys.argv[1])

cnf = ''
for l in sys.stdin:
    cnf += l

elite_path = './rokk/binary/SatELite_release'
solver_path = './rokk/binary/rokk_static'

p = subprocess.Popen([elite_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate(cnf)[0]

elite_time, status, solution, cnf = parse_out(output)

if status == 'SATISFIABLE' or status == 'UNSATISFIABLE':
    print str(elite_time) + ' p'
    print status
    print solution
elif cnf != '':
    l_args = [solver_path]
    if time_limit is not None:
        l_args.append('-cpu-lim=' + str(time_limit))
    p = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = p.communicate(cnf)[0]
    time, status, solution, cnf = parse_out(output)

    print str(elite_time + time)
    print status
    print solution

exit(0)
