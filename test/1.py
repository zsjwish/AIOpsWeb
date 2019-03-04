#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 15:33
# @Author  : zsj
# @File    : 1.py
# @Description:
from concurrent.futures import ProcessPoolExecutor
import  time
def task(name):
    for i in range(10):
        print("name", name, i)
        time.sleep(1)

if __name__ == "__main__":
    start = time.time()
    ex = ProcessPoolExecutor(2)

    for i in range(5):
        ex.submit(task, "safly%d"%i)
    ex.shutdown(wait=False)

    print("main")
    end = time.time()
    print(end - start)