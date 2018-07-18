import subprocess

from key_generators.a5_1 import A5_1
from parse_utils.cnf_parser import CnfParser
from util import caser
from wrapper.cryptominisat import CryptoMinisatWrapper
from wrapper.lingeling import LingelingWrapper

solver_wrapper = CryptoMinisatWrapper(True)
cnf = CnfParser().parse_for_path("./templates/A5_1.cnf")


def my_test(k):
    count = 0
    av_time = 0
    for j in range(k):
        init_case = caser.create_init_case(cnf, A5_1)
        init_args = solver_wrapper.get_arguments(tl=1)

        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = init_sp.communicate(init_case.get_cnf())
        if len(err) != 0 and not err.startswith("timelimit"):
            raise Exception(err)
        try:
            report = solver_wrapper.parse_out(output)
            init_case.mark_solved(report)
            count += 1
            av_time += init_case.time
        except KeyError:
            pass

    return count, av_time / count


print "start init test"
print "test 1 init case"

for k in [1, 10, 50, 100, 200]:
    count, av_time = my_test(k)
    print "%d/%d solved with time: %f" % (count, k, av_time)
