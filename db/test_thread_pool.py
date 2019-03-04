from concurrent.futures import ThreadPoolExecutor
from time import sleep





def task(n):
    print("Processing {}".format(n))
    sleep(1)


def main():
    print("Starting ThreadPoolExecutor")
    with ThreadPoolExecutor(max_workers = 4) as executor:
        future = executor.submit(task, (2))
        future = executor.submit(task, (3))
        future = executor.submit(task, (4))
        future = executor.submit(task, (5))
        future = executor.submit(task, (6))
        future = executor.submit(task, (7))
    print("All tasks complete")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 9:44
# @Author  : zsj
# @File    : test_thread_pool.py
# @Description:
