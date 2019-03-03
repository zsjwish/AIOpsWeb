import threading
import time
import queue


class Mythrea():
    def __init__(self, maxsize=5):
        self.maxsize = maxsize
        self.q = queue.Queue(maxsize)
        for i in range(maxsize):
            self.q.put(threading.Thread)

    def get_thread(self):
        return self.q.get()

    def put_thread(self):
        self.q.put(threading.Thread)


pool = Mythrea(5)


def task(arg, p):
    print(arg)
    time.sleep(1)
    p.put_thread()


for i in range(100):
    t = pool.get_thread()
    obj = t(target = task, args = (i, pool,))
    obj.start()
