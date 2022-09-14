from multiprocessing import Process, Manager

from cursor.misc import Timer
import time
import random
import wasabi

log = wasabi.Printer()


def f(_list, idx, other_data):
    # print(idx)
    random_sleep = random.random() * 5
    log.info(f"sleeping for: {random_sleep}")
    time.sleep(random_sleep)
    _list[idx] = idx + other_data


if __name__ == "__main__":

    cpus = 7  # os.cpu_count()

    timer = Timer()

    with Manager() as manager:
        _list = manager.list(range(cpus))

        processes = []
        data = [111, 222, 333, 444, 555, 666, 777, 888]

        timer.start()
        for i in range(cpus):

            p = Process(target=f, args=(_list, i, data[i]))
            p.start()
            processes.append(p)
            timer.print_elapsed(f"starting {i} took")

        timer.print_elapsed("before joining")
        for p in processes:
            newtimer = Timer()
            newtimer.start()
            p.join()
            newtimer.print_elapsed(f"joining {p.pid}")

        timer.print_elapsed("everything")
        print(_list)
