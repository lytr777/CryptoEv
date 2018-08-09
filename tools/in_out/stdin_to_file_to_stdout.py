import tempfile
import sys
import os
import subprocess

if len(sys.argv) < 2:
    print "USAGE: stdin_to_file.py <args>"
    exit(1)

in_file = tempfile.NamedTemporaryFile(prefix="cnf_").name
out_file = tempfile.NamedTemporaryFile(prefix="out_").name
open(in_file, 'w').write(sys.stdin.read())

l_args = sys.argv[1:]
l_args.extend([in_file, out_file])

p = subprocess.Popen(l_args)
p.wait()
print open(out_file, 'w').read()

if os.path.isfile(in_file):
    os.remove(in_file)
if os.path.isfile(out_file):
    os.remove(out_file)
