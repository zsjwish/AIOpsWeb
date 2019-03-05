#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/3/4 17:28
# @Author  : zsj
# @File    : static_value.py
# @Description:
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import wraps


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return getinstance


@singleton
class StaticValue(object):
    def __init__(self):
        self.executor5 = ProcessPoolExecutor(5)
        # self.executor5 = ThreadPoolExecutor(5)


sv = StaticValue()

