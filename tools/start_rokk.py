import sys
import subprocess


def parse_out(out):
    i = 0
    lines = out.split('\n')

    while i < len(lines) and not lines[i].startswith("i CPU time"):
        i += 1
    t = float(lines[i].split(':')[1])
    i += 1

    while i < len(lines) and not lines[i].startswith("i "):
        i += 1
    st = lines[i].split(' ')[1]
    i += 1

    s = ''
    c = ''
    if st == 'SATISFIABLE':
        s = lines[i]
    elif st == 'PRESATELITED':
        while i < len(lines):
            c += lines[i] + '\n'
            i += 1

    return t, st, s, c


if len(sys.argv) < 2:
    print "USAGE: rokk_py.py <simplify?> [time limit]"
    exit(1)

simplify = sys.argv[1] != '0'
time_limit = None
if len(sys.argv) > 2:
    time_limit = int(sys.argv[2])

elite_path = './rokk/binary/SatELite_release'
solver_path = './rokk/binary/rokk_static'

if not simplify:
    l_args = [solver_path]
    if time_limit is not None:
        l_args.append('-cpu-lim=' + str(time_limit))

    p = subprocess.Popen(l_args, stdin=sys.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate()[0]
    time, status, solution, _ = parse_out(output)

    print str(time)
    print status
    print solution
    exit(0)

p = subprocess.Popen([elite_path], stdin=sys.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate()[0]

elite_time, status, solution, cnf = parse_out(output)

if status == 'SATISFIABLE' or status == 'UNSATISFIABLE':
    print str(elite_time) + ' p'
    print status
    print solution
elif cnf != '':
    l_args = [solver_path]
    if time_limit is not None:
        l_args.append('-cpu-lim=' + str(time_limit))

    p = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = p.communicate(cnf)[0]
    time, status, solution, _ = parse_out(output)

    print str(elite_time + time)
    print status
    print solution
