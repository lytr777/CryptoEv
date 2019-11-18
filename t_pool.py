from multiprocessing import Pool
from time import sleep, time as now


def task_function(n):
    sleep(2)
    return n % 2


pool = Pool(processes=4)

res_list, result = [], []
for n in range(100):
    res = pool.apply_async(task_function, (n,))
    res_list.append(res)

while len(res_list) > 0:
    timestamp = now()
    res_list[0].wait()

    i = 0
    while i < len(res_list):
        if res_list[i].ready():
            res = res_list.pop(i)
            if res.successful():
                result.append(res.get())
            else:
                print "Pool solving was completed unsuccessfully"
                result.append(None)
        else:
            i += 1

    print "Already solved %d tasks" % len(result)

print result
pool.terminate()
