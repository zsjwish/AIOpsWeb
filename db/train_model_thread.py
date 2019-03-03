#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/3 16:21
# @Author  : zsj
# @File    : train_model_thread.py
# @Description:
import queue
import threading


class TrainModelThreadPool:
    def __init__(self, max_size=5):
        """
        初始化一个有着5个线程的线程池，线程放在thread_queue中
        :param max_size:
        """
        self.max_size = max_size
        self.thread_queue = queue.Queue(max_size)
        for i in range(max_size):
            self.thread_queue.put(threading.Thread)

    def get_thread(self):
        return self.thread_queue.get()

    def put_thread(self):
        self.thread_queue.put(threading.Thread)

    def start_new_task(self, task, args):
        thread_tmp = self.get_thread()
        thread_case = thread_tmp(target = task, args = args)

